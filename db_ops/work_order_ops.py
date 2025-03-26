import json
from mysql.connector import Error
from datetime import datetime

class WorkOrder_Ops:
    def __init__(self, db_manager) -> None:
        self.db_manager = db_manager
        self.console_logger = self.db_manager.console_logger

    def connect(self):
        return self.db_manager.connect()

    def close(self, connection):
        return self.db_manager.close(connection)
    
    def check_upcoming_work_orders(self):
        """Check for work orders due soon and send notifications"""
        try:
            connection = self.connect()
            cursor = connection.cursor(dictionary=True)
            
            # First check if notification_sent column exists
            cursor.execute("SHOW COLUMNS FROM work_orders LIKE 'notification_sent'")
            has_notification_column = cursor.fetchone() is not None
            
            # Adjust query based on column existence
            base_query = """
                SELECT wo.*, ms.notification_days_before, ms.notification_emails
                FROM work_orders wo
                JOIN maintenance_schedules ms ON wo.schedule_id = ms.schedule_id
                WHERE 
                    wo.status = 'Open'
                    AND wo.due_date BETWEEN CURDATE() 
                    AND DATE_ADD(CURDATE(), INTERVAL ms.notification_days_before DAY)
            """
            
            if has_notification_column:
                base_query += " AND wo.notification_sent = 0"
            
            cursor.execute(base_query)
            upcoming_orders = cursor.fetchall()
            
            for order in upcoming_orders:
                if order.get('notification_emails'):
                    # Send notification
                    if self.send_work_order_notifications(
                        order['work_order_id'],
                        json.loads(order['notification_emails']),
                        'upcoming'
                    ):
                        # Mark notification as sent if column exists
                        if has_notification_column:
                            cursor.execute("""
                                UPDATE work_orders
                                SET notification_sent = 1
                                WHERE work_order_id = %s
                            """, (order['work_order_id'],))
                            connection.commit()
            
            return True
            
        except Exception as e:
            print(f"Error checking upcoming work orders: {e}")
            return False
        finally:
            self.close(connection)

    def send_work_order_notifications(self, work_order_id, recipients, notification_type):
        """Send email notifications for work orders"""
        try:
            # Get work order details
            work_order = self.get_work_order_by_id(work_order_id)
            if not work_order:
                return False
            
            # Get email settings
            settings = self.get_email_settings()
            if not settings or not settings.get('enabled'):
                return False
            
            import smtplib
            from email.mime.text import MIMEText
            from email.mime.multipart import MIMEMultipart
            
            # Create message
            msg = MIMEMultipart()
            msg['From'] = settings['from_address']
            msg['To'] = ', '.join(recipients)
            
            if notification_type == 'new_scheduled':
                msg['Subject'] = f"New Scheduled Work Order: {work_order['title']}"
                body = f"""
                A new scheduled work order has been generated:
                
                Title: {work_order['title']}
                Equipment: {work_order['equipment_name']}
                Priority: {work_order['priority']}
                Due Date: {work_order['due_date']}
                
                Please log into the CMMS system to view the full details.
                """
            elif notification_type == 'upcoming':
                msg['Subject'] = f"Upcoming Work Order Due: {work_order['title']}"
                body = f"""
                Reminder: The following work order is due soon:
                
                Title: {work_order['title']}
                Equipment: {work_order['equipment_name']}
                Priority: {work_order['priority']}
                Due Date: {work_order['due_date']}
                
                Please ensure this work order is completed on time.
                """
            
            msg.attach(MIMEText(body, 'plain'))
            
            # Send email
            with smtplib.SMTP(settings['server'], int(settings['port'])) as server:
                if settings.get('use_tls'):
                    server.starttls()
                if settings.get('username') and settings.get('password'):
                    server.login(settings['username'], settings['password'])
                server.send_message(msg)
            
            return True
            
        except Exception as e:
            print(f"Error sending work order notification: {e}")
            return False

    def get_email_settings(self):
        """Get email notification settings"""
        try:
            connection = self.connect()
            cursor = connection.cursor(dictionary=True)
            
            cursor.execute("SELECT * FROM email_settings LIMIT 1")
            settings = cursor.fetchone()
            
            return settings
            
        except Exception as e:
            print(f"Error getting email settings: {e}")
            return None
        finally:
            self.close(connection)

    def get_work_order_by_id(self, work_order_id):
        """Get work order by ID"""
        try:
            connection = self.connect()
            cursor = connection.cursor(dictionary=True)
            
            cursor.execute("""
                SELECT wo.*, 
                       e.equipment_name,
                       CONCAT(c.first_name, ' ', c.last_name) as assigned_to
                FROM work_orders wo
                LEFT JOIN equipment_registry e ON wo.equipment_id = e.equipment_id
                LEFT JOIN craftsmen c ON wo.craftsman_id = c.craftsman_id
                WHERE wo.work_order_id = %s
            """, (work_order_id,))
            
            return cursor.fetchone()
        except Error as e:
            print(f"Error getting work order: {e}")
            return None
        finally:
            self.close(connection)

    def get_all_work_orders(self):
        """Get all work orders"""
        try:
            connection = self.connect()
            cursor = connection.cursor(dictionary=True)
            
            cursor.execute("""
                SELECT wo.*, 
                       e.equipment_name,
                       CONCAT(c.first_name, ' ', c.last_name) as assigned_to
                FROM work_orders wo
                LEFT JOIN equipment_registry e ON wo.equipment_id = e.equipment_id
                LEFT JOIN craftsmen c ON wo.craftsman_id = c.craftsman_id
                ORDER BY wo.created_date DESC
            """)
            
            return cursor.fetchall()
        except Error as e:
            print(f"Error getting work orders: {e}")
            return []
        finally:
            self.close(connection)


    def get_recent_work_orders(self, limit=10):
        """Get recent work orders"""
        try:
            connection = self.connect()
            cursor = connection.cursor(dictionary=True)
            
            cursor.execute("""
                SELECT wo.work_order_id, wo.title, wo.status, wo.due_date,
                       e.equipment_name,
                       CONCAT(c.first_name, ' ', c.last_name) as assigned_to
                FROM work_orders wo
                LEFT JOIN equipment_registry e ON wo.equipment_id = e.equipment_id
                LEFT JOIN craftsmen c ON wo.craftsman_id = c.craftsman_id
                ORDER BY wo.created_date DESC
                LIMIT %s
            """, (limit,))
            
            return cursor.fetchall()
        except Error as e:
            print(f"Error getting recent work orders: {e}")
            return []
        finally:
            self.close(connection)

    def delete_work_order(self, work_order_id):
        """Delete a work order"""
        try:
            connection = self.connect()
            cursor = connection.cursor()
            
            cursor.execute("""
                DELETE FROM work_orders
                WHERE work_order_id = %s
            """, (work_order_id,))
            
            connection.commit()
            return cursor.rowcount > 0
        except Error as e:
            print(f"Error deleting work order: {e}")
            return False
        finally:
            self.close(connection)

    def update_work_order_status(self, work_order_id, new_status):
        """Update the status of a work order"""
        try:
            connection = self.connect()
            cursor = connection.cursor()
            
            # Get current status and equipment ID
            cursor.execute("""
                SELECT status, equipment_id, craftsman_id, title
                FROM work_orders
                WHERE work_order_id = %s
            """, (work_order_id,))
            
            result = cursor.fetchone()
            if not result:
                return False
            
            current_status, equipment_id, craftsman_id, title = result
            
            # Update status
            cursor.execute("""
                UPDATE work_orders SET
                    status = %s,
                    completed_date = CASE WHEN %s = 'Completed' THEN CURDATE() ELSE NULL END
                WHERE work_order_id = %s
            """, (new_status, new_status, work_order_id))
            
            connection.commit()
            
            # Add to equipment history if status changed to Completed
            if current_status != "Completed" and new_status == "Completed" and equipment_id:
                cursor.execute("""
                    INSERT INTO equipment_history (
                        equipment_id, date, event_type, description, performed_by
                    ) VALUES (%s, %s, %s, %s, %s)
                """, (
                    equipment_id,
                    datetime.now().date(),
                    "Work Order Completed",
                    f"Work Order #{work_order_id}: {title}",
                    f"Completed by: {self.get_craftsman_name(craftsman_id)}"
                ))
                connection.commit()
            
            return True
        except Error as e:
            print(f"Error updating work order status: {e}")
            return False
        finally:
            self.close(connection)

    def get_work_order_statistics(self):
        """Get work order statistics"""
        try:
            connection = self.connect()
            cursor = connection.cursor(dictionary=True)
            
            # Get total count
            cursor.execute("SELECT COUNT(*) as count FROM work_orders")
            total = cursor.fetchone()['count']
            
            # Get open count
            cursor.execute("""
                SELECT COUNT(*) as count FROM work_orders
                WHERE status IN ('Open', 'In Progress', 'On Hold')
            """)
            open_count = cursor.fetchone()['count']
            
            # Get completed count
            cursor.execute("""
                SELECT COUNT(*) as count FROM work_orders
                WHERE status = 'Completed'
            """)
            completed = cursor.fetchone()['count']
            
            # Get overdue count
            cursor.execute("""
                SELECT COUNT(*) as count FROM work_orders
                WHERE due_date < CURDATE() AND status NOT IN ('Completed', 'Cancelled')
            """)
            overdue = cursor.fetchone()['count']
            
            return {
                'total': total,
                'open': open_count,
                'completed': completed,
                'overdue': overdue
            }
        except Error as e:
            print(f"Error getting work order statistics: {e}")
            return None
        finally:
            self.close(connection)


    def get_work_orders_by_date(self, date):
        """Get work orders for a specific date"""
        try:
            connection = self.connect()
            cursor = connection.cursor(dictionary=True)
            
            cursor.execute("""
                SELECT wo.*, 
                       e.equipment_name,
                       CONCAT(c.first_name, ' ', c.last_name) as assigned_to
                FROM work_orders wo
                LEFT JOIN equipment_registry e ON wo.equipment_id = e.equipment_id
                LEFT JOIN craftsmen c ON wo.craftsman_id = c.craftsman_id
                WHERE wo.due_date = %s
                ORDER BY wo.created_date DESC
            """, (date,))
            
            return cursor.fetchall()
        except Error as e:
            print(f"Error getting work orders by date: {e}")
            return []
        finally:
            self.close(connection)


    def get_work_orders_by_date_range(self, start_date, end_date):
        """Get work orders for a date range"""
        try:
            connection = self.connect()
            cursor = connection.cursor(dictionary=True)
            
            cursor.execute("""
                SELECT wo.*, 
                       e.equipment_name,
                       CONCAT(c.first_name, ' ', c.last_name) as assigned_to
                FROM work_orders wo
                LEFT JOIN equipment_registry e ON wo.equipment_id = e.equipment_id
                LEFT JOIN craftsmen c ON wo.craftsman_id = c.craftsman_id
                WHERE wo.due_date BETWEEN %s AND %s
                ORDER BY wo.due_date ASC
            """, (start_date, end_date))
            
            return cursor.fetchall()
        except Error as e:
            print(f"Error getting work orders by date range: {e}")
            return []
        finally:
            self.close(connection)


    def get_work_orders_for_report(self, start_date, end_date, status_filter=None):
        """
        Get work orders for reporting within a date range and optional status filter.
        
        Args:
            start_date: Start date for the report period
            end_date: End date for the report period
            status_filter: Optional status to filter by
            
        Returns:
            List of work order dictionaries
        """
        try:
            connection = self.connect()
            cursor = connection.cursor(dictionary=True)
            
            query = """
                SELECT 
                    wo.work_order_id,
                    wo.title,
                    wo.description,
                    wo.status,
                    wo.priority,
                    wo.created_date,
                    wo.due_date,
                    wo.completed_date,
                    wo.estimated_hours,
                    wo.actual_hours,
                    (wo.actual_hours * 50) as labor_cost,
                    wo.total_cost as parts_cost,
                    ((wo.actual_hours * 50) + IFNULL(wo.total_cost, 0)) as total_cost,
                    e.equipment_name,
                    CONCAT(c.first_name, ' ', c.last_name) as assigned_to
                FROM work_orders wo
                LEFT JOIN equipment_registry e ON wo.equipment_id = e.equipment_id
                LEFT JOIN craftsmen c ON wo.craftsman_id = c.craftsman_id
                WHERE wo.created_date BETWEEN %s AND %s
            """
            
            params = [start_date, end_date]
            
            if status_filter:
                query += " AND wo.status = %s"
                params.append(status_filter)
            
            query += " ORDER BY wo.created_date DESC"
            
            cursor.execute(query, tuple(params))
            work_orders = cursor.fetchall()
            
            # Convert datetime objects to string for JSON serialization
            for wo in work_orders:
                if wo.get('created_date'):
                    wo['created_date'] = wo['created_date'].strftime('%Y-%m-%d')
                if wo.get('due_date'):
                    wo['due_date'] = wo['due_date'].strftime('%Y-%m-%d')
                if wo.get('completed_date'):
                    wo['completed_date'] = wo['completed_date'].strftime('%Y-%m-%d')
            
            return work_orders
        
        except Error as e:
            self.console_logger.error(f"Error getting work orders for report: {e}")
            return []
        finally:
            self.close(connection)

    def get_work_order_costs(self, start_date, end_date, status_filter=None):
        """
        Get work order cost data for reporting.
        
        Args:
            start_date: Start date for the report period
            end_date: End date for the report period
            status_filter: Optional status to filter by
            
        Returns:
            List of work order dictionaries with cost information
        """
        try:
            connection = self.connect()
            cursor = connection.cursor(dictionary=True)
            
            query = """
                SELECT 
                    wo.work_order_id,
                    wo.title,
                    wo.status,
                    wo.created_date,
                    wo.completed_date,
                    wo.estimated_hours,
                    wo.actual_hours,
                    wo.total_cost as parts_cost,
                    (wo.actual_hours * 50) as labor_cost,
                    ((wo.actual_hours * 50) + IFNULL(wo.total_cost, 0)) as total_cost,
                    e.equipment_name,
                    CONCAT(c.first_name, ' ', c.last_name) as assigned_to
                FROM work_orders wo
                LEFT JOIN equipment_registry e ON wo.equipment_id = e.equipment_id
                LEFT JOIN craftsmen c ON wo.craftsman_id = c.craftsman_id
                WHERE wo.created_date BETWEEN %s AND %s
            """
            
            params = [start_date, end_date]
            
            if status_filter:
                query += " AND wo.status = %s"
                params.append(status_filter)
            
            query += " ORDER BY wo.created_date DESC"
            
            cursor.execute(query, tuple(params))
            work_orders = cursor.fetchall()
            
            # Convert datetime objects to string for JSON serialization
            for wo in work_orders:
                if wo.get('created_date'):
                    wo['created_date'] = wo['created_date'].strftime('%Y-%m-%d')
                if wo.get('completed_date'):
                    wo['completed_date'] = wo['completed_date'].strftime('%Y-%m-%d')
                
                # Ensure numeric values are not None
                wo['estimated_hours'] = wo.get('estimated_hours', 0) or 0
                wo['actual_hours'] = wo.get('actual_hours', 0) or 0
                wo['labor_cost'] = wo.get('labor_cost', 0) or 0
                wo['parts_cost'] = wo.get('parts_cost', 0) or 0
                wo['total_cost'] = wo.get('total_cost', 0) or 0
            
            return work_orders
        
        except Error as e:
            self.console_logger.error(f"Error getting work order costs: {e}")
            return []
        finally:
            self.close(connection)


    def get_work_orders_by_due_date(self, due_date):
        """
        Get work orders due on a specific date.
        
        Args:
            due_date: The due date to check
            
        Returns:
            List of work order dictionaries
        """
        try:
            connection = self.connect()
            cursor = connection.cursor(dictionary=True)
            
            cursor.execute("""
                SELECT wo.*, 
                       e.equipment_name,
                       CONCAT(c.first_name, ' ', c.last_name) as assigned_to
                FROM work_orders wo
                LEFT JOIN equipment_registry e ON wo.equipment_id = e.equipment_id
                LEFT JOIN craftsmen c ON wo.craftsman_id = c.craftsman_id
                WHERE wo.due_date = %s
                ORDER BY wo.priority DESC
            """, (due_date,))
            
            return cursor.fetchall()
        except Error as e:
            self.console_logger.error(f"Error getting work orders by due date: {e}")
            return []
        finally:
            self.close(connection)

    def get_overdue_work_orders(self):
        """
        Get work orders that are overdue.
        
        Returns:
            List of overdue work order dictionaries
        """
        try:
            connection = self.connect()
            cursor = connection.cursor(dictionary=True)
            
            today = datetime.now().date()
            
            cursor.execute("""
                SELECT wo.*, 
                       e.equipment_name,
                       CONCAT(c.first_name, ' ', c.last_name) as assigned_to
                FROM work_orders wo
                LEFT JOIN equipment_registry e ON wo.equipment_id = e.equipment_id
                LEFT JOIN craftsmen c ON wo.craftsman_id = c.craftsman_id
                WHERE wo.due_date < %s
                AND wo.status NOT IN ('Completed', 'Cancelled')
                ORDER BY wo.due_date ASC, wo.priority DESC
            """, (today,))
            
            return cursor.fetchall()
        except Error as e:
            self.console_logger.error(f"Error getting overdue work orders: {e}")
            return []
        finally:
            self.close(connection)

    def get_work_orders_by_team(self, team_id):
        """Get work orders assigned to a team"""
        try:
            connection = self.connect()
            cursor = connection.cursor(dictionary=True)
            
            cursor.execute("""
                SELECT wo.*, e.equipment_name
                FROM work_orders wo
                LEFT JOIN equipment e ON wo.equipment_id = e.equipment_id
                WHERE wo.team_id = %s
                ORDER BY wo.created_date DESC
            """, (team_id,))
            
            work_orders = cursor.fetchall()
            return work_orders
            
        except Exception as e:
            print(f"Error getting work orders by team: {e}")
            return []
        finally:
            if 'connection' in locals():
                self.close(connection)

    def create_recurring_work_order(self, work_order_data, schedule_data):
        """Create a recurring work order with scheduling information"""
        connection = None
        try:
            connection = self.connect()
            cursor = connection.cursor()
            
            # First create the schedule record
            cursor.execute("""
                INSERT INTO maintenance_schedules (
                    frequency,
                    frequency_unit,
                    start_date,
                    end_date,
                    last_generated,
                    notification_days_before,
                    notification_emails
                ) VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (
                schedule_data['frequency'],
                schedule_data['frequency_unit'],
                schedule_data['start_date'],
                schedule_data.get('end_date'),
                None,
                schedule_data.get('notification_days_before', 2),
                json.dumps(schedule_data.get('notification_emails', []))
            ))
            
            schedule_id = cursor.lastrowid
            
            # Create the work order template
            cursor.execute("""
                INSERT INTO work_order_templates (
                    title,
                    description,
                    equipment_id,
                    priority,
                    estimated_hours,
                    assignment_type,
                    craftsman_id,
                    team_id,
                    tools_required,
                    spares_required,
                    schedule_id
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                work_order_data['title'],
                work_order_data['description'],
                work_order_data['equipment_id'],
                work_order_data['priority'],
                work_order_data.get('estimated_hours', 0),
                work_order_data.get('assignment_type', 'Individual'),
                work_order_data.get('craftsman_id'),
                work_order_data.get('team_id'),
                json.dumps(work_order_data.get('tools_required', [])),
                json.dumps(work_order_data.get('spares_required', [])),
                schedule_id
            ))
            
            # Now create the first work order instance directly instead of calling create_work_order
            tools_required = json.dumps(work_order_data.get('tools_required', []))
            spares_required = json.dumps(work_order_data.get('spares_required', []))
            
            cursor.execute("""
                INSERT INTO work_orders (
                    title,
                    description,
                    equipment_id,
                    craftsman_id,
                    team_id,
                    assignment_type,
                    priority,
                    status,
                    created_date,
                    due_date,
                    completed_date,
                    estimated_hours,
                    actual_hours,
                    tools_required,
                    spares_required,
                    notes,
                    schedule_id
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                work_order_data['title'],
                work_order_data['description'],
                work_order_data['equipment_id'],
                work_order_data.get('craftsman_id'),
                work_order_data.get('team_id'),
                work_order_data.get('assignment_type', 'Individual'),
                work_order_data['priority'],
                work_order_data.get('status', 'Open'),
                datetime.now().date(),
                work_order_data['due_date'],
                work_order_data.get('completed_date'),
                work_order_data.get('estimated_hours', 0),
                work_order_data.get('actual_hours', 0),
                tools_required,
                spares_required,
                work_order_data.get('notes', ''),
                schedule_id
            ))
            
            work_order_id = cursor.lastrowid
            
            # Update the last_generated date in the schedule
            cursor.execute("""
                UPDATE maintenance_schedules
                SET last_generated = %s
                WHERE schedule_id = %s
            """, (datetime.now().date(), schedule_id))
            
            connection.commit()
            return True
            
        except Exception as e:
            print(f"Error creating recurring work order: {e}")
            if connection:
                connection.rollback()
            return False
        finally:
            if connection:
                self.close(connection)

    def get_pending_scheduled_work_orders(self):
        """Get work orders that need to be generated based on schedules"""
        try:
            connection = self.connect()
            cursor = connection.cursor(dictionary=True)
            
            cursor.execute("""
                SELECT 
                    wot.*,
                    ms.*,
                    CASE 
                        WHEN ms.last_generated IS NULL THEN ms.start_date
                        WHEN ms.frequency_unit = 'days' THEN DATE_ADD(ms.last_generated, INTERVAL ms.frequency DAY)
                        WHEN ms.frequency_unit = 'weeks' THEN DATE_ADD(ms.last_generated, INTERVAL ms.frequency WEEK)
                        WHEN ms.frequency_unit = 'months' THEN DATE_ADD(ms.last_generated, INTERVAL ms.frequency MONTH)
                    END as next_due_date
                FROM work_order_templates wot
                JOIN maintenance_schedules ms ON wot.schedule_id = ms.schedule_id
                WHERE 
                    (ms.last_generated IS NULL AND ms.start_date <= CURDATE())
                    OR
                    (
                        CASE 
                            WHEN ms.frequency_unit = 'days' THEN DATE_ADD(ms.last_generated, INTERVAL ms.frequency DAY)
                            WHEN ms.frequency_unit = 'weeks' THEN DATE_ADD(ms.last_generated, INTERVAL ms.frequency WEEK)
                            WHEN ms.frequency_unit = 'months' THEN DATE_ADD(ms.last_generated, INTERVAL ms.frequency MONTH)
                        END <= CURDATE()
                    )
                    AND (ms.end_date IS NULL OR ms.end_date >= CURDATE())
            """)
            
            return cursor.fetchall()
            
        except Exception as e:
            print(f"Error getting pending scheduled work orders: {e}")
            return []
        finally:
            self.close(connection)

    def generate_scheduled_work_order(self, template, due_date):
        """Generate a work order from a template"""
        try:
            connection = self.connect()
            cursor = connection.cursor()
            
            # Create the work order
            cursor.execute("""
                INSERT INTO work_orders (
                    title,
                    description,
                    equipment_id,
                    priority,
                    status,
                    created_date,
                    due_date,
                    estimated_hours,
                    assignment_type,
                    craftsman_id,
                    team_id,
                    tools_required,
                    spares_required,
                    notes,
                    schedule_id
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                template['title'],
                template['description'],
                template['equipment_id'],
                template['priority'],
                'Open',
                datetime.now().date(),
                due_date,
                template['estimated_hours'],
                template['assignment_type'],
                template['craftsman_id'],
                template['team_id'],
                template['tools_required'],
                template['spares_required'],
                f"Auto-generated from schedule #{template['schedule_id']}",
                template['schedule_id']
            ))
            
            work_order_id = cursor.lastrowid
            
            # Update the last generated date
            cursor.execute("""
                UPDATE maintenance_schedules
                SET last_generated = %s
                WHERE schedule_id = %s
            """, (datetime.now().date(), template['schedule_id']))
            
            connection.commit()
            return work_order_id
            
        except Exception as e:
            print(f"Error generating scheduled work order: {e}")
            if connection:
                connection.rollback()
            return None
        finally:
            if connection:
                self.close(connection)

    def update_work_order_status(self, data):
        """
        Update work order status.
        
        Args:
            data: Dictionary with work_order_id, status, and optional fields
            
        Returns:
            Boolean indicating success
        """
        try:
            connection = self.connect()
            cursor = connection.cursor()
            
            # Build query dynamically based on provided fields
            query = "UPDATE work_orders SET "
            params = []
            
            if 'status' in data:
                query += "status = %s, "
                params.append(data['status'])
            
            if 'completed_date' in data:
                query += "completed_date = %s, "
                params.append(data['completed_date'])
            
            if 'notes' in data:
                query += "notes = %s, "
                params.append(data['notes'])
            
            # Remove trailing comma and space
            query = query.rstrip(', ')
            
            # Add WHERE clause
            query += " WHERE work_order_id = %s"
            params.append(data['work_order_id'])
            
            cursor.execute(query, tuple(params))
            connection.commit()
            
            return True
        except Error as e:
            self.console_logger.error(f"Error updating work order status: {e}")
            return False
        finally:
            self.close(connection)

    def update_work_order(self, work_order_data):
        """Update an existing work order"""
        try:
            connection = self.connect()
            cursor = connection.cursor()
            
            # Get current status and equipment_id
            cursor.execute("""
                SELECT status, equipment_id FROM work_orders
                WHERE work_order_id = %s
            """, (work_order_data['work_order_id'],))
            
            result = cursor.fetchone()
            if not result:
                return False
            
            current_status = result[0]
            current_equipment_id = result[1]
            
            # Update work order
            cursor.execute("""
                UPDATE work_orders SET
                    title = %s,
                    description = %s,
                    equipment_id = %s,
                    assignment_type = %s,
                    craftsman_id = %s,
                    team_id = %s,
                    priority = %s,
                    status = %s,
                    due_date = %s,
                    completed_date = %s,
                    estimated_hours = %s,
                    actual_hours = %s,
                    tools_required = %s,
                    spares_required = %s,
                    notes = %s
                WHERE work_order_id = %s
            """, (
                work_order_data['title'],
                work_order_data['description'],
                work_order_data['equipment_id'],
                work_order_data['assignment_type'],
                work_order_data.get('craftsman_id'),
                work_order_data.get('team_id'),
                work_order_data['priority'],
                work_order_data['status'],
                work_order_data['due_date'],
                work_order_data['completed_date'],
                work_order_data['estimated_hours'],
                work_order_data['actual_hours'],
                json.dumps(work_order_data.get('tools_required', [])),
                json.dumps(work_order_data.get('spares_required', [])),
                work_order_data['notes'],
                work_order_data['work_order_id']
            ))
            
            connection.commit()
            
            # Add to equipment history if status changed to Completed
            if current_status != "Completed" and work_order_data['status'] == "Completed" and work_order_data['equipment_id']:
                assignee = ""
                if work_order_data['assignment_type'] == 'Individual':
                    assignee = f"Completed by: {self.get_craftsman_name(work_order_data['craftsman_id'])}"
                else:
                    team_name = self.get_team_name(work_order_data['team_id'])
                    assignee = f"Completed by team: {team_name}"
                
                cursor.execute("""
                    INSERT INTO equipment_history (
                        equipment_id, date, event_type, description, performed_by, notes
                    ) VALUES (%s, %s, %s, %s, %s, %s)
                """, (
                    work_order_data['equipment_id'],
                    datetime.now().date(),
                    "Work Order Completed",
                    f"Work Order #{work_order_data['work_order_id']}: {work_order_data['title']}",
                    assignee,
                    work_order_data['notes']
                ))
                connection.commit()
            
            return True
        except Error as e:
            print(f"Error updating work order: {e}")
            return False
        finally:
            self.close(connection)

    def create_work_order(self, work_order_data):
        """Create a new work order"""
        try:
            connection = self.connect()
            cursor = connection.cursor()
            
            # Convert JSON fields
            tools_required = json.dumps(work_order_data.get('tools_required', []))
            spares_required = json.dumps(work_order_data.get('spares_required', []))
            
            # Insert work order
            cursor.execute("""
                INSERT INTO work_orders (
                    title,
                    description,
                    equipment_id,
                    craftsman_id,
                    team_id,
                    assignment_type,
                    priority,
                    status,
                    created_date,
                    due_date,
                    completed_date,
                    estimated_hours,
                    actual_hours,
                    tools_required,
                    spares_required,
                    notes,
                    schedule_id
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                work_order_data['title'],
                work_order_data['description'],
                work_order_data['equipment_id'],
                work_order_data.get('craftsman_id'),
                work_order_data.get('team_id'),
                work_order_data.get('assignment_type', 'Individual'),
                work_order_data['priority'],
                work_order_data.get('status', 'Open'),
                datetime.now().date(),
                work_order_data['due_date'],
                work_order_data.get('completed_date'),
                work_order_data.get('estimated_hours', 0),
                work_order_data.get('actual_hours', 0),
                tools_required,
                spares_required,
                work_order_data.get('notes', ''),
                work_order_data.get('schedule_id')
            ))
            
            work_order_id = cursor.lastrowid
            connection.commit()

            return work_order_id
            
        except Exception as e:
            print(f"Error creating work order: {e}")
            return None
        finally:
            self.close(connection)
