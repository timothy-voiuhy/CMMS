"""
Scheduler service for handling recurring work orders and notifications.
This module provides functionality for:
- Generating recurring work orders based on maintenance schedules
- Sending notifications for upcoming work orders
- Managing the scheduling service lifecycle
"""

import time
import threading
import logging
from datetime import datetime, timedelta
from db_manager import DatabaseManager

class MaintenanceScheduler:
    """
    A scheduler service that manages recurring work orders and notifications.
    
    This class handles:
    - Automatic generation of work orders based on maintenance schedules
    - Email notifications for upcoming work orders
    - Background processing of scheduled tasks
    """
    
    def __init__(self, db_manager=None):
        """
        Initialize the scheduler service.
        
        Args:
            db_manager: Optional DatabaseManager instance. If not provided, creates a new one.
        """
        self.db_manager = db_manager or DatabaseManager()
        self.running = False
        self.scheduler_thread = None
        self.logger = logging.getLogger('maintenance_scheduler')
        self.check_interval = 3600  # Default to 1 hour
        
    def start(self):
        """
        Start the scheduler service.
        
        If the scheduler is already running, this method will return without action.
        The scheduler runs in a daemon thread that will automatically terminate when
        the main program exits.
        """
        if self.scheduler_thread and self.scheduler_thread.is_alive():
            self.logger.info("Scheduler is already running")
            return
        
        try:
            self.running = True
            self.scheduler_thread = threading.Thread(target=self._scheduler_loop)
            self.scheduler_thread.daemon = True
            self.scheduler_thread.start()
            self.logger.info("Maintenance scheduler started successfully")
        except Exception as e:
            self.logger.error(f"Failed to start scheduler: {e}")
            self.running = False
            raise
    
    def stop(self):
        """
        Stop the scheduler service.
        
        This method will wait for the current scheduler loop to complete before
        stopping the service.
        """
        self.logger.info("Stopping maintenance scheduler...")
        self.running = False
        if self.scheduler_thread:
            try:
                self.scheduler_thread.join(timeout=10)  # Wait up to 10 seconds
                if self.scheduler_thread.is_alive():
                    self.logger.warning("Scheduler thread did not stop gracefully")
                else:
                    self.logger.info("Maintenance scheduler stopped successfully")
            except Exception as e:
                self.logger.error(f"Error stopping scheduler: {e}")
    
    def _scheduler_loop(self):
        """
        Main scheduler loop that processes scheduled tasks.
        
        This method runs continuously while the scheduler is active, checking for:
        - Pending scheduled work orders that need to be generated
        - Upcoming work orders that require notifications
        - Completed work orders that need to be rescheduled
        
        The loop runs at intervals defined by self.check_interval (default: 1 hour)
        """
        while self.running:
            try:
                self._process_pending_work_orders()
                self._process_notifications()
                self._process_completed_work_orders()
                
            except Exception as e:
                self.logger.error(f"Error in scheduler loop: {e}")
                # Add a shorter sleep on error to prevent rapid error loops
                time.sleep(60)  # Wait 1 minute before retrying after error
                continue
            
            # Sleep until next check interval
            time.sleep(self.check_interval)
    
    def _process_pending_work_orders(self):
        """Process any pending scheduled work orders that need to be generated."""
        try:
            pending_orders = self.db_manager.get_pending_scheduled_work_orders()
            for template in pending_orders:
                try:
                    work_order_id = self.db_manager.generate_scheduled_work_order(
                        template,
                        template['next_due_date']
                    )
                    if work_order_id:
                        self.logger.info(
                            f"Generated scheduled work order #{work_order_id} "
                            f"from template #{template['template_id']}"
                        )
                    else:
                        self.logger.error(
                            f"Failed to generate work order for template "
                            f"#{template['template_id']}"
                        )
                except Exception as e:
                    self.logger.error(
                        f"Error generating work order from template "
                        f"#{template['template_id']}: {e}"
                    )
        except Exception as e:
            self.logger.error(f"Error processing pending work orders: {e}")
    
    def _process_notifications(self):
        """Process notifications for upcoming work orders."""
        try:
            self.db_manager.check_upcoming_work_orders()
        except Exception as e:
            self.logger.error(f"Error processing notifications: {e}")
    
    def _process_completed_work_orders(self):
        """Process completed work orders that need to be rescheduled."""
        try:
            # Get completed work orders with schedules
            connection = self.db_manager.connect()
            cursor = connection.cursor(dictionary=True)
            
            cursor.execute("""
                SELECT 
                    wo.*,
                    ms.schedule_id,
                    ms.frequency,
                    ms.frequency_unit,
                    ms.end_date
                FROM work_orders wo
                JOIN maintenance_schedules ms ON wo.schedule_id = ms.schedule_id
                WHERE 
                    wo.status = 'Completed' 
                    AND wo.rescheduled = 0
                    AND (ms.end_date IS NULL OR ms.end_date >= CURDATE())
            """)
            
            completed_orders = cursor.fetchall()
            self.db_manager.close(connection)
            
            for order in completed_orders:
                try:
                    # Calculate next due date based on completion date
                    completion_date = order['completed_date']
                    if not completion_date:
                        completion_date = datetime.now().date()
                    
                    if order['frequency_unit'] == 'days':
                        next_due_date = completion_date + timedelta(days=order['frequency'])
                    elif order['frequency_unit'] == 'weeks':
                        next_due_date = completion_date + timedelta(weeks=order['frequency'])
                    elif order['frequency_unit'] == 'months':
                        # Approximate months as 30 days
                        next_due_date = completion_date + timedelta(days=30*order['frequency'])
                    
                    # Check if next due date is before end date (if set)
                    if order['end_date'] and next_due_date > order['end_date']:
                        self.logger.info(
                            f"Work order #{order['work_order_id']} schedule has ended. "
                            f"No new work order will be created."
                        )
                        continue
                    
                    # Create new work order
                    new_work_order = {
                        'title': order['title'],
                        'description': order['description'],
                        'equipment_id': order['equipment_id'],
                        'assignment_type': order['assignment_type'],
                        'craftsman_id': order['craftsman_id'],
                        'team_id': order['team_id'],
                        'priority': order['priority'],
                        'status': 'Open',
                        'due_date': next_due_date,
                        'estimated_hours': order['estimated_hours'],
                        'tools_required': order['tools_required'],
                        'spares_required': order['spares_required'],
                        'notes': order['notes'],
                        'schedule_id': order['schedule_id']
                    }
                    
                    # Save new work order
                    new_id = self.db_manager.create_work_order(new_work_order)
                    
                    if new_id:
                        # Mark original as rescheduled
                        connection = self.db_manager.connect()
                        cursor = connection.cursor()
                        cursor.execute("""
                            UPDATE work_orders
                            SET rescheduled = 1
                            WHERE work_order_id = %s
                        """, (order['work_order_id'],))
                        connection.commit()
                        self.db_manager.close(connection)
                        
                        self.logger.info(
                            f"Created new work order #{new_id} from completed "
                            f"work order #{order['work_order_id']}"
                        )
                    else:
                        self.logger.error(
                            f"Failed to create new work order from completed "
                            f"work order #{order['work_order_id']}"
                        )
                        
                except Exception as e:
                    self.logger.error(
                        f"Error processing completed work order "
                        f"#{order['work_order_id']}: {e}"
                    )
                    
        except Exception as e:
            self.logger.error(f"Error processing completed work orders: {e}")
    
    def is_running(self):
        """
        Check if the scheduler is currently running.
        
        Returns:
            bool: True if the scheduler is running, False otherwise.
        """
        return self.running and self.scheduler_thread and self.scheduler_thread.is_alive()
    
    def set_check_interval(self, interval):
        """
        Set the interval between scheduler checks.
        
        Args:
            interval (int): The interval in seconds between scheduler checks.
        """
        if interval < 60:  # Don't allow intervals less than 1 minute
            raise ValueError("Check interval must be at least 60 seconds")
        self.check_interval = interval
        self.logger.info(f"Scheduler check interval set to {interval} seconds")