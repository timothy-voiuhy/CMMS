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
    
    def send_email(self, to_address, subject, html_content, attachments=None):
        """
        Send an email.
        
        Args:
            to_address: Recipient email address
            subject: Email subject
            html_content: HTML content of the email
            attachments: Optional list of file paths to attach
            
        Returns:
            Boolean indicating success or failure
        """
        if not self.is_enabled():
            logger.warning("Email notifications are disabled. Cannot send email.")
            return False
        
        if not to_address:
            logger.warning("No recipient email address provided.")
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
            return True
        
        except Exception as e:
            logger.error(f"Error sending email: {e}")
            return False
    
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
        
        # Get craftsman email
        craftsman = self.db_manager.get_craftsman_by_id(work_order['craftsman_id'])
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
        return self.send_email(craftsman['email'], subject, html_content)
    
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
            return
        
        try:
            today = datetime.now().date()
            upcoming_date = today + timedelta(days=2)
            
            # Get work orders due in 2 days
            upcoming_work_orders = self.db_manager.get_work_orders_by_due_date(upcoming_date)
            for work_order in upcoming_work_orders:
                if work_order['status'] not in ['Completed', 'Cancelled']:
                    self.send_work_order_notification(work_order, 'upcoming')
            
            # Get work orders due today
            due_today_work_orders = self.db_manager.get_work_orders_by_due_date(today)
            for work_order in due_today_work_orders:
                if work_order['status'] not in ['Completed', 'Cancelled']:
                    self.send_work_order_notification(work_order, 'due_today')
            
            # Get overdue work orders
            overdue_work_orders = self.db_manager.get_overdue_work_orders()
            for work_order in overdue_work_orders:
                if work_order['status'] not in ['Completed', 'Cancelled']:
                    self.send_work_order_notification(work_order, 'overdue')
            
            logger.info(f"Notification check completed. Processed {len(upcoming_work_orders)} upcoming, "
                       f"{len(due_today_work_orders)} due today, and {len(overdue_work_orders)} overdue work orders.")
        
        except Exception as e:
            logger.error(f"Error checking and sending notifications: {e}")
    
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