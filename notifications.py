"""
Email notification system for CMMS application.
Handles sending email notifications to craftsmen about work orders.
"""

import os
import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from datetime import datetime, timedelta
import json
import threading
import time
import schedule

from config import WORK_ORDER_SETTINGS_FILE

# Setup logging
logger = logging.getLogger('notifications')
logger.setLevel(logging.INFO)
if not logger.handlers:
    handler = logging.FileHandler('notifications.log')
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

class EmailNotificationService:
    """Service for sending email notifications to craftsmen."""
    
    def __init__(self, db_manager):
        """
        Initialize the email notification service.
        
        Args:
            db_manager: Database manager instance
        """
        self.db_manager = db_manager
        self.settings = self._load_email_settings()
        self.is_running = False
        self.scheduler_thread = None
    
    def _load_email_settings(self):
        """Load email settings from configuration file."""
        try:
            settings_file = WORK_ORDER_SETTINGS_FILE
            
            if not os.path.exists(settings_file):
                logger.warning("Email settings file not found. Using default settings.")
                return {
                    'email': {
                        'enabled': False,
                        'server': '',
                        'port': '',
                        'username': '',
                        'password': '',
                        'from_address': ''
                    },
                    'notifications': {
                        'approaching_due_dates': True,
                        'due_date_days': 2
                    }
                }
            
            with open(settings_file, 'r') as f:
                settings = json.load(f)
            
            # Ensure email settings exist
            if 'email' not in settings:
                settings['email'] = {
                    'enabled': False,
                    'server': '',
                    'port': '',
                    'username': '',
                    'password': '',
                    'from_address': ''
                }
            
            # If from_address is not set, use username
            if 'from_address' not in settings['email'] or not settings['email']['from_address']:
                settings['email']['from_address'] = settings['email'].get('username', '')
            
            return settings
        except Exception as e:
            logger.error(f"Error loading email settings: {e}")
            return {
                'email': {
                    'enabled': False,
                    'server': '',
                    'port': '',
                    'username': '',
                    'password': '',
                    'from_address': ''
                },
                'notifications': {
                    'approaching_due_dates': True,
                    'due_date_days': 2
                }
            }
    
    def is_enabled(self):
        """Check if email notifications are enabled."""
        return (self.settings.get('email', {}).get('enabled', False) and
                self.settings.get('email', {}).get('server') and
                self.settings.get('email', {}).get('username') and
                self.settings.get('email', {}).get('password'))
    
    def send_email(self, to_address, subject, html_content, attachments=None, notification_type=None, reference_id=None):
        """
        Send an email and track it in the database.
        
        Args:
            to_address: Recipient email address
            subject: Email subject
            html_content: HTML content of the email
            attachments: Optional list of file paths to attach
            notification_type: Type of notification (work_order, purchase_order, etc.)
            reference_id: ID of the related entity (work order ID, PO ID, etc.)
            
        Returns:
            Boolean indicating success or failure
        """
        # Log the attempt
        self.log_email_activity("attempt_send", {
            "recipient": to_address,
            "subject": subject,
            "notification_type": notification_type,
            "reference_id": reference_id,
            "attachments_count": len(attachments) if attachments else 0
        })
        
        # Create notification record in database
        notification_id = self._create_notification_record(
            to_address, subject, html_content, 'pending', 
            notification_type, reference_id, attachments
        )
        
        if not self.is_enabled():
            error_msg = "Email notifications are disabled. Cannot send email."
            logger.warning(error_msg)
            self._update_notification_status(notification_id, 'failed', error_msg)
            self.log_email_activity("send_failed", {
                "notification_id": notification_id,
                "reason": "notifications_disabled"
            }, "warning")
            return False
        
        if not to_address:
            error_msg = "No recipient email address provided."
            logger.warning(error_msg)
            self._update_notification_status(notification_id, 'failed', error_msg)
            self.log_email_activity("send_failed", {
                "notification_id": notification_id,
                "reason": "missing_recipient"
            }, "warning")
            return False
        
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = self.settings['email']['from_address']
            msg['To'] = to_address
            
            # Attach HTML content
            html_part = MIMEText(html_content, 'html')
            msg.attach(html_part)
            
            # Attach files if provided
            attached_files = []
            if attachments:
                for file_path in attachments:
                    if os.path.exists(file_path):
                        with open(file_path, 'rb') as file:
                            attachment = MIMEApplication(file.read())
                            attachment.add_header(
                                'Content-Disposition', 
                                'attachment', 
                                filename=os.path.basename(file_path)
                            )
                            msg.attach(attachment)
                            attached_files.append(os.path.basename(file_path))
                    else:
                        self.log_email_activity("attachment_missing", {
                            "notification_id": notification_id,
                            "file_path": file_path
                        }, "warning")
            
            # Connect to server and send
            server = smtplib.SMTP(
                self.settings['email']['server'], 
                int(self.settings['email']['port'])
            )
            server.starttls()
            server.login(
                self.settings['email']['username'], 
                self.settings['email']['password']
            )
            server.send_message(msg)
            server.quit()
            
            logger.info(f"Email sent successfully to {to_address}")
            self._update_notification_status(notification_id, 'sent')
            
            self.log_email_activity("send_success", {
                "notification_id": notification_id,
                "recipient": to_address,
                "subject": subject,
                "notification_type": notification_type,
                "reference_id": reference_id,
                "attachments": attached_files
            })
            
            return True
        
        except Exception as e:
            error_msg = f"Error sending email: {e}"
            logger.error(error_msg)
            self._update_notification_status(notification_id, 'failed', error_msg)
            
            self.log_email_activity("send_error", {
                "notification_id": notification_id,
                "error": str(e),
                "recipient": to_address,
                "subject": subject
            }, "error")
            
            return False
    
    def _create_notification_record(self, recipient, subject, content, status, notification_type=None, reference_id=None, attachments=None):
        """Create a record of the notification in the database"""
        try:
            connection = self.db_manager.connect()
            cursor = connection.cursor()
            
            attachments_json = json.dumps(attachments) if attachments else '[]'
            
            query = """
                INSERT INTO email_notifications 
                (recipient, subject, content, status, notification_type, reference_id, attachments)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(query, (
                recipient, subject, content, status, 
                notification_type, reference_id, attachments_json
            ))
            
            notification_id = cursor.lastrowid
            connection.commit()
            return notification_id
        
        except Exception as e:
            logger.error(f"Error creating notification record: {e}")
            return None
        finally:
            if connection:
                connection.close()
    
    def _update_notification_status(self, notification_id, status, error_message=None):
        """Update the status of a notification in the database"""
        if not notification_id:
            return
        
        try:
            connection = self.db_manager.connect()
            cursor = connection.cursor()
            
            if status == 'sent':
                query = """
                    UPDATE email_notifications 
                    SET status = %s, sent_at = CURRENT_TIMESTAMP
                    WHERE notification_id = %s
                """
                cursor.execute(query, (status, notification_id))
            else:
                query = """
                    UPDATE email_notifications 
                    SET status = %s, error_message = %s
                    WHERE notification_id = %s
                """
                cursor.execute(query, (status, error_message, notification_id))
            
            connection.commit()
        
        except Exception as e:
            logger.error(f"Error updating notification status: {e}")
        finally:
            if connection:
                connection.close()
    
    def get_notifications(self, status=None, limit=100, offset=0):
        """Get notifications from the database"""
        try:
            connection = self.db_manager.connect()
            cursor = connection.cursor(dictionary=True)
            
            if status:
                query = """
                    SELECT * FROM email_notifications
                    WHERE status = %s
                    ORDER BY created_at DESC
                    LIMIT %s OFFSET %s
                """
                cursor.execute(query, (status, limit, offset))
            else:
                query = """
                    SELECT * FROM email_notifications
                    ORDER BY created_at DESC
                    LIMIT %s OFFSET %s
                """
                cursor.execute(query, (limit, offset))
            
            return cursor.fetchall()
        
        except Exception as e:
            logger.error(f"Error getting notifications: {e}")
            return []
        finally:
            if connection:
                connection.close()
    
    def get_notification_by_id(self, notification_id):
        """Get a specific notification by ID"""
        try:
            connection = self.db_manager.connect()
            cursor = connection.cursor(dictionary=True)
            
            query = "SELECT * FROM email_notifications WHERE notification_id = %s"
            cursor.execute(query, (notification_id,))
            return cursor.fetchone()
        
        except Exception as e:
            logger.error(f"Error getting notification: {e}")
            return None
        finally:
            if connection:
                connection.close()
    
    def retry_failed_notification(self, notification_id):
        """Retry sending a failed notification"""
        notification = self.get_notification_by_id(notification_id)
        if not notification:
            self.log_email_activity("retry_failed", {
                "notification_id": notification_id,
                "status": "not_found"
            }, "warning")
            return False
        
        if notification['status'] != 'failed':
            self.log_email_activity("retry_failed", {
                "notification_id": notification_id,
                "status": notification['status'],
                "error": "Only failed notifications can be retried"
            }, "warning")
            return False
        
        # Log the retry attempt
        self.log_email_activity("retry_attempt", {
            "notification_id": notification_id,
            "recipient": notification['recipient'],
            "subject": notification['subject'],
            "notification_type": notification['notification_type'],
            "reference_id": notification['reference_id']
        })
        
        # Parse attachments JSON
        attachments = json.loads(notification['attachments']) if notification['attachments'] else None
        
        # Retry sending
        result = self.send_email(
            notification['recipient'],
            notification['subject'],
            notification['content'],
            attachments,
            notification['notification_type'],
            notification['reference_id']
        )
        
        if result:
            self.log_email_activity("retry_success", {
                "notification_id": notification_id
            })
        else:
            self.log_email_activity("retry_failed", {
                "notification_id": notification_id
            }, "error")
        
        return result
    
    def send_work_order_notification(self, work_order, notification_type):
        """
        Send a notification about a work order.
        
        Args:
            work_order: Work order data dictionary
            notification_type: Type of notification ('upcoming', 'due_today', 'overdue')
            
        Returns:
            Boolean indicating success or failure
        """
        if not work_order.get('craftsman_id'):
            logger.warning(f"Work order #{work_order.get('work_order_id')} has no assigned craftsman.")
            return False
        
        # Check if we already have the craftsman email in the work order data
        if work_order.get('craftsman_email'):
            craftsman_email = work_order['craftsman_email']
            craftsman_name = work_order.get('craftsman_name', 'Craftsman')
            craftsman = {
                'email': craftsman_email,
                'first_name': craftsman_name.split(' ')[0] if ' ' in craftsman_name else craftsman_name
            }
        else:
            # Get craftsman email
            craftsman = self.get_craftsman_by_id(work_order['craftsman_id'])
            if not craftsman or not craftsman.get('email'):
                logger.warning(f"No email found for craftsman ID {work_order.get('craftsman_id')}")
                return False
        
        # Prepare email content based on notification type
        if notification_type == 'upcoming':
            subject = f"Upcoming Work Order #{work_order['work_order_id']} Due in 2 Days"
            html_content = self._create_upcoming_email_template(work_order, craftsman)
        elif notification_type == 'due_today':
            subject = f"Work Order #{work_order['work_order_id']} Due Today"
            html_content = self._create_due_today_email_template(work_order, craftsman)
        elif notification_type == 'overdue':
            subject = f"OVERDUE: Work Order #{work_order['work_order_id']}"
            html_content = self._create_overdue_email_template(work_order, craftsman)
        else:
            logger.error(f"Unknown notification type: {notification_type}")
            return False
        
        # Send the email
        return self.send_email(
            craftsman['email'], 
            subject, 
            html_content, 
            notification_type='work_order', 
            reference_id=work_order['work_order_id']
        )
    
    def _create_upcoming_email_template(self, work_order, craftsman):
        """Create HTML email template for upcoming work orders."""
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background-color: #2196F3; color: white; padding: 10px 20px; text-align: center; }}
                .content {{ padding: 20px; border: 1px solid #ddd; }}
                .work-order {{ background-color: #f9f9f9; padding: 15px; margin-top: 20px; border-left: 4px solid #2196F3; }}
                .footer {{ text-align: center; margin-top: 20px; font-size: 12px; color: #777; }}
                .button {{ display: inline-block; background-color: #2196F3; color: white; padding: 10px 20px; 
                          text-decoration: none; border-radius: 4px; margin-top: 15px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h2>Work Order Reminder</h2>
                </div>
                <div class="content">
                    <p>Hello {craftsman['first_name']},</p>
                    
                    <p>This is a friendly reminder that you have a work order due in <strong>2 days</strong>.</p>
                    
                    <div class="work-order">
                        <h3>Work Order #{work_order['work_order_id']}: {work_order['title']}</h3>
                        <p><strong>Equipment:</strong> {work_order.get('equipment_name', 'N/A')}</p>
                        <p><strong>Priority:</strong> {work_order.get('priority', 'Medium')}</p>
                        <p><strong>Due Date:</strong> {work_order.get('due_date', 'Not specified')}</p>
                        <p><strong>Description:</strong> {work_order.get('description', 'No description provided.')}</p>
                    </div>
                    
                    <p>Please ensure this work order is completed by the due date. If you anticipate any issues with completing this task on time, please notify your supervisor as soon as possible.</p>
                    
                    <p>Thank you for your attention to this matter.</p>
                    
                    <p>Best regards,<br>CMMS System</p>
                </div>
                <div class="footer">
                    <p>This is an automated message from the CMMS System. Please do not reply to this email.</p>
                </div>
            </div>
        </body>
        </html>
        """
    
    def _create_due_today_email_template(self, work_order, craftsman):
        """Create HTML email template for work orders due today."""
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background-color: #FF9800; color: white; padding: 10px 20px; text-align: center; }}
                .content {{ padding: 20px; border: 1px solid #ddd; }}
                .work-order {{ background-color: #fff3e0; padding: 15px; margin-top: 20px; border-left: 4px solid #FF9800; }}
                .footer {{ text-align: center; margin-top: 20px; font-size: 12px; color: #777; }}
                .button {{ display: inline-block; background-color: #FF9800; color: white; padding: 10px 20px; 
                          text-decoration: none; border-radius: 4px; margin-top: 15px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h2>Work Order Due Today</h2>
                </div>
                <div class="content">
                    <p>Hello {craftsman['first_name']},</p>
                    
                    <p>This is an important reminder that you have a work order <strong>due today</strong>.</p>
                    
                    <div class="work-order">
                        <h3>Work Order #{work_order['work_order_id']}: {work_order['title']}</h3>
                        <p><strong>Equipment:</strong> {work_order.get('equipment_name', 'N/A')}</p>
                        <p><strong>Priority:</strong> {work_order.get('priority', 'Medium')}</p>
                        <p><strong>Due Date:</strong> {work_order.get('due_date', 'Today')}</p>
                        <p><strong>Description:</strong> {work_order.get('description', 'No description provided.')}</p>
                    </div>
                    
                    <p>Please prioritize this task to ensure it is completed today. If you have already completed this work order, please update its status in the system.</p>
                    
                    <p>If you are unable to complete this work order today, please contact your supervisor immediately.</p>
                    
                    <p>Thank you for your prompt attention to this matter.</p>
                    
                    <p>Best regards,<br>CMMS System</p>
                </div>
                <div class="footer">
                    <p>This is an automated message from the CMMS System. Please do not reply to this email.</p>
                </div>
            </div>
        </body>
        </html>
        """
    
    def _create_overdue_email_template(self, work_order, craftsman):
        """Create HTML email template for overdue work orders."""
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background-color: #F44336; color: white; padding: 10px 20px; text-align: center; }}
                .content {{ padding: 20px; border: 1px solid #ddd; }}
                .work-order {{ background-color: #ffebee; padding: 15px; margin-top: 20px; border-left: 4px solid #F44336; }}
                .footer {{ text-align: center; margin-top: 20px; font-size: 12px; color: #777; }}
                .button {{ display: inline-block; background-color: #F44336; color: white; padding: 10px 20px; 
                          text-decoration: none; border-radius: 4px; margin-top: 15px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h2>OVERDUE Work Order</h2>
                </div>
                <div class="content">
                    <p>Hello {craftsman['first_name']},</p>
                    
                    <p>This is an <strong>urgent notification</strong> that you have an <strong>OVERDUE</strong> work order that requires immediate attention.</p>
                    
                    <div class="work-order">
                        <h3>Work Order #{work_order['work_order_id']}: {work_order['title']}</h3>
                        <p><strong>Equipment:</strong> {work_order.get('equipment_name', 'N/A')}</p>
                        <p><strong>Priority:</strong> {work_order.get('priority', 'Medium')}</p>
                        <p><strong>Due Date:</strong> {work_order.get('due_date', 'Past due')}</p>
                        <p><strong>Description:</strong> {work_order.get('description', 'No description provided.')}</p>
                    </div>
                    
                    <p>This work order is now overdue. Please complete it as soon as possible or contact your supervisor to discuss any issues preventing its completion.</p>
                    
                    <p>Timely completion of work orders is critical for maintaining equipment reliability and operational efficiency.</p>
                    
                    <p>Thank you for your immediate attention to this matter.</p>
                    
                    <p>Best regards,<br>CMMS System</p>
                </div>
                <div class="footer">
                    <p>This is an automated message from the CMMS System. Please do not reply to this email.</p>
                </div>
            </div>
        </body>
        </html>
        """
    
    def check_and_send_notifications(self):
        """Check for work orders that need notifications and send them."""
        if not self.is_enabled():
            logger.info("Email notifications are disabled. Skipping notification check.")
            self.log_email_activity("check_skipped", {
                "reason": "notifications_disabled"
            }, "warning")
            return
        print("Checking and sending notifications")
        try:
            today = datetime.now().date()
            upcoming_date = today + timedelta(days=1)
            
            self.log_email_activity("check_started", {
                "check_date": str(today),
                "upcoming_date": str(upcoming_date)
            })
            
            # Check if notification_sent column exists
            connection = self.db_manager.connect()
            cursor = connection.cursor()
            cursor.execute("SHOW COLUMNS FROM work_orders LIKE 'notification_sent'")
            has_notification_column = cursor.fetchone() is not None
            connection.close()
            
            print(f"Checking for work orders due on {upcoming_date}")

            # Get work orders due that are yet due.
            upcoming_work_orders = self.db_manager.get_work_orders_by_date(upcoming_date)
            upcoming_sent = 0
            print(f"Found {len(upcoming_work_orders)} upcoming work orders")
            for work_order in upcoming_work_orders:
                # Skip if notification already sent
                if has_notification_column and work_order.get('notification_sent'):
                    print(f"Notification already sent for work order {work_order['work_order_id']}")
                    continue
                    
                if work_order['status'] not in ['Completed', 'Cancelled']:
                    print(f"Sending notification for work order {work_order['work_order_id']}")
                    if self.send_work_order_notification(work_order, 'upcoming'):
                        upcoming_sent += 1
                        # Mark as sent if column exists
                        if has_notification_column:
                            self._mark_notification_sent(work_order['work_order_id'])
            
            # Get work orders due today
            due_today_work_orders = self.db_manager.get_work_orders_by_date(today)
            today_sent = 0
            for work_order in due_today_work_orders:
                if work_order['status'] not in ['Completed', 'Cancelled']:
                    if self.send_work_order_notification(work_order, 'due_today'):
                        today_sent += 1
        
            # Get overdue work orders
            overdue_work_orders = self.db_manager.get_overdue_work_orders()
            overdue_sent = 0
            for work_order in overdue_work_orders:
                if work_order['status'] not in ['Completed', 'Cancelled']:
                    if self.send_work_order_notification(work_order, 'overdue'):
                        overdue_sent += 1
            
            self.log_email_activity("check_completed", {
                "upcoming_total": len(upcoming_work_orders),
                "upcoming_sent": upcoming_sent,
                "today_total": len(due_today_work_orders),
                "today_sent": today_sent,
                "overdue_total": len(overdue_work_orders),
                "overdue_sent": overdue_sent
            })
            
            logger.info(f"Notification check completed. Processed {len(upcoming_work_orders)} upcoming, "
                       f"{len(due_today_work_orders)} due today, and {len(overdue_work_orders)} overdue work orders.")
        
        except Exception as e:
            logger.error(f"Error checking and sending notifications: {e}")
            self.log_email_activity("check_error", {
                "error": str(e)
            }, "error")
    
    def start_scheduler(self):
        """Start the notification scheduler in a separate thread."""
        if self.is_running:
            logger.warning("Notification scheduler is already running.")
            return
        
        def run_scheduler():
            logger.info("Starting notification scheduler...")
            
            # Schedule notification checks
            schedule.every().day.at("08:00").do(self.check_and_send_notifications)  # Morning check
            schedule.every().day.at("12:00").do(self.check_and_send_notifications)  # Midday check
            
            self.is_running = True
            
            while self.is_running:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
        
        self.scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
        self.scheduler_thread.start()
        
        # Run an initial check
        self.check_and_send_notifications()
    
    def stop_scheduler(self):
        """Stop the notification scheduler."""
        self.is_running = False
        if self.scheduler_thread:
            self.scheduler_thread.join(timeout=2)
            logger.info("Notification scheduler stopped.")
    
    def get_craftsman_by_id(self, craftsman_id):
        """Get craftsman details by ID"""
        try:
            connection = self.db_manager.connect()
            cursor = connection.cursor(dictionary=True)
            
            query = """
                SELECT * FROM craftsmen 
                WHERE craftsman_id = %s
            """
            cursor.execute(query, (craftsman_id,))
            return cursor.fetchone()
        
        except Exception as e:
            logger.error(f"Error getting craftsman by ID: {e}")
            return None
        finally:
            if connection:
                connection.close()
                
    def log_email_activity(self, activity_type, details, status="info"):
        """
        Log email notification activity with detailed information
        
        Args:
            activity_type: Type of activity (check, send, retry, etc.)
            details: Dictionary with activity details
            status: Log level (info, warning, error)
        """
        try:
            # Format the details for logging
            details_str = ", ".join([f"{k}={v}" for k, v in details.items() if v is not None])
            
            # Log to the notifications log file
            if status == "error":
                logger.error(f"EMAIL ACTIVITY [{activity_type}]: {details_str}")
            elif status == "warning":
                logger.warning(f"EMAIL ACTIVITY [{activity_type}]: {details_str}")
            else:
                logger.info(f"EMAIL ACTIVITY [{activity_type}]: {details_str}")
            
            # Save to database if connected
            self._save_activity_to_database(activity_type, details, status)
            
        except Exception as e:
            logger.error(f"Error logging email activity: {e}")

    def _save_activity_to_database(self, activity_type, details, status):
        """Save email activity to database for tracking"""
        try:
            connection = self.db_manager.connect()
            cursor = connection.cursor()
            
            # Convert details to JSON
            details_json = json.dumps(details)
            
            query = """
                INSERT INTO email_activity_log (
                    activity_type, details, status, timestamp
                ) VALUES (%s, %s, %s, CURRENT_TIMESTAMP)
            """
            cursor.execute(query, (activity_type, details_json, status))
            connection.commit()
            
        except Exception as e:
            logger.error(f"Error saving email activity to database: {e}")
        finally:
            if connection:
                connection.close()

    def get_email_activity_log(self, limit=100, offset=0, activity_type=None):
        """Get email activity log entries from database"""
        try:
            connection = self.db_manager.connect()
            cursor = connection.cursor(dictionary=True)
            
            if activity_type:
                query = """
                    SELECT * FROM email_activity_log
                    WHERE activity_type = %s
                    ORDER BY timestamp DESC
                    LIMIT %s OFFSET %s
                """
                cursor.execute(query, (activity_type, limit, offset))
            else:
                query = """
                    SELECT * FROM email_activity_log
                    ORDER BY timestamp DESC
                    LIMIT %s OFFSET %s
                """
                cursor.execute(query, (limit, offset))
            
            return cursor.fetchall()
        
        except Exception as e:
            logger.error(f"Error getting email activity log: {e}")
            return []
        finally:
            if connection:
                connection.close()

    def get_notification_statistics(self):
        """Get statistics about email notifications"""
        try:
            connection = self.db_manager.connect()
            cursor = connection.cursor(dictionary=True)
            
            # Get counts by status
            cursor.execute("""
                SELECT status, COUNT(*) as count 
                FROM email_notifications 
                GROUP BY status
            """)
            status_counts = cursor.fetchall()
            
            # Get counts by type
            cursor.execute("""
                SELECT notification_type, COUNT(*) as count 
                FROM email_notifications 
                GROUP BY notification_type
            """)
            type_counts = cursor.fetchall()
            
            # Get daily counts for the last 7 days
            cursor.execute("""
                SELECT DATE(created_at) as date, COUNT(*) as count 
                FROM email_notifications 
                WHERE created_at >= DATE_SUB(CURRENT_DATE, INTERVAL 7 DAY)
                GROUP BY DATE(created_at)
                ORDER BY date
            """)
            daily_counts = cursor.fetchall()
            
            return {
                'status_counts': status_counts,
                'type_counts': type_counts,
                'daily_counts': daily_counts
            }
        
        except Exception as e:
            logger.error(f"Error getting notification statistics: {e}")
            return {
                'status_counts': [],
                'type_counts': [],
                'daily_counts': []
            }
        finally:
            if connection:
                connection.close()

    def _mark_notification_sent(self, work_order_id):
        """Mark a work order as having had its notification sent"""
        try:
            connection = self.db_manager.connect()
            cursor = connection.cursor()
            
            cursor.execute("""
                UPDATE work_orders
                SET notification_sent = 1
                WHERE work_order_id = %s
            """, (work_order_id,))
            
            connection.commit()
        except Exception as e:
            logger.error(f"Error marking notification as sent: {e}")
        finally:
            if connection:
                connection.close() 