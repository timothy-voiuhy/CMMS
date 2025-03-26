from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                              QPushButton, QLabel, QTabWidget, QFrame, QGridLayout, 
                              QMessageBox, QLineEdit, QFormLayout, QComboBox, QListWidget, QApplication,
                              QDialog, QDialogButtonBox, QCheckBox, QGroupBox, QTreeWidget, QProgressDialog,
                              QTreeWidgetItem, QSplitter, QFileDialog, QProgressBar, QTextEdit, QProgressBar,
                              QStackedWidget, QDateEdit, QTimeEdit, QCalendarWidget, QComboBox, QSpinBox, 
                              QInputDialog, QTableWidgetItem, QTextEdit, QTableWidget, QTextEdit)
from PySide6.QtCore import Qt, Signal, Slot, QSize, QDate, QTime
from PySide6.QtGui import QIcon, QFont, QColor
import json
import os
import time
import shutil
import hashlib
import logging
from datetime import datetime

class AdminWindow(QMainWindow):
    """Main window for CMMS administration"""
    
    log_message = Signal(str)  # Signal for logging messages
    
    def __init__(self, db_manager, parent=None):
        super().__init__(parent)
        self.db_manager = db_manager
        self.setWindowTitle("CMMS Administration")
        self.setMinimumSize(1000, 700)
        
        # Setup logging
        self.logger = logging.getLogger('cmms_admin')
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # Create header
        header_label = QLabel("CMMS System Administration")
        header_label.setFont(QFont("Arial", 16, QFont.Bold))
        header_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(header_label)
        
        # Create tab widget
        self.tab_widget = QTabWidget()
        main_layout.addWidget(self.tab_widget)
        
        # Create status bar
        self.status_bar = self.statusBar()

        # Add tabs
        self.setup_user_management_tab()
        self.setup_database_tab()
        self.setup_system_settings_tab()
        self.setup_audit_log_tab()
        self.setup_backup_restore_tab()
        
        self.status_bar.showMessage("Ready")
        
        # Connect log signal
        self.log_message.connect(self.log_to_audit)
    
    def setup_user_management_tab(self):
        """Setup the user management tab"""
        tab = QWidget()
        layout = QHBoxLayout(tab)
        
        # Create user list panel
        user_list_group = QGroupBox("Administrator Accounts")
        user_list_layout = QVBoxLayout(user_list_group)
        
        # Add search box
        search_layout = QHBoxLayout()
        search_label = QLabel("Search:")
        self.user_search = QLineEdit()
        self.user_search.setPlaceholderText("Search by name or username")
        self.user_search.textChanged.connect(self.filter_user_list)
        search_layout.addWidget(search_label)
        search_layout.addWidget(self.user_search)
        user_list_layout.addLayout(search_layout)
        
        # Add user list
        self.user_list = QTreeWidget()
        self.user_list.setHeaderLabels(["Username", "Role", "Last Login"])
        self.user_list.setAlternatingRowColors(True)
        self.user_list.itemClicked.connect(self.on_user_selected)
        user_list_layout.addWidget(self.user_list)
        
        # Add buttons
        button_layout = QHBoxLayout()
        self.add_user_btn = QPushButton("Add Admin")
        self.add_user_btn.clicked.connect(self.show_add_user_dialog)
        self.edit_user_btn = QPushButton("Edit")
        self.edit_user_btn.clicked.connect(self.show_edit_user_dialog)
        self.edit_user_btn.setEnabled(False)
        self.delete_user_btn = QPushButton("Delete")
        self.delete_user_btn.clicked.connect(self.delete_user)
        self.delete_user_btn.setEnabled(False)
        button_layout.addWidget(self.add_user_btn)
        button_layout.addWidget(self.edit_user_btn)
        button_layout.addWidget(self.delete_user_btn)
        user_list_layout.addLayout(button_layout)
        
        # Create user details panel
        user_details_group = QGroupBox("User Details")
        user_details_layout = QVBoxLayout(user_details_group)
        
        # Add user details form
        form_layout = QFormLayout()
        self.user_details_username = QLabel("")
        self.user_details_fullname = QLabel("")
        self.user_details_email = QLabel("")
        self.user_details_role = QLabel("")
        self.user_details_created = QLabel("")
        self.user_details_last_login = QLabel("")
        form_layout.addRow("Username:", self.user_details_username)
        form_layout.addRow("Full Name:", self.user_details_fullname)
        form_layout.addRow("Email:", self.user_details_email)
        form_layout.addRow("Role:", self.user_details_role)
        form_layout.addRow("Created On:", self.user_details_created)
        form_layout.addRow("Last Login:", self.user_details_last_login)
        user_details_layout.addLayout(form_layout)
        
        # Add user permissions
        permissions_group = QGroupBox("Permissions")
        permissions_layout = QVBoxLayout(permissions_group)
        self.permission_list = QTreeWidget()
        self.permission_list.setHeaderLabels(["Permission", "Status"])
        self.permission_list.setAlternatingRowColors(True)
        permissions_layout.addWidget(self.permission_list)
        user_details_layout.addWidget(permissions_group)
        
        # Add password reset button
        self.reset_password_btn = QPushButton("Reset Password")
        self.reset_password_btn.clicked.connect(self.reset_user_password)
        self.reset_password_btn.setEnabled(False)
        user_details_layout.addWidget(self.reset_password_btn)
        
        # Add panels to main layout
        layout.addWidget(user_list_group, 1)
        layout.addWidget(user_details_group, 1)
        
        self.tab_widget.addTab(tab, "User Management")
        
        # Load initial data
        self.load_user_list()
    
    def setup_database_tab(self):
        """Setup the database management tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Database information section
        info_group = QGroupBox("Database Information")
        info_layout = QFormLayout(info_group)
        
        self.db_type_label = QLabel("Loading...")
        self.db_version_label = QLabel("Loading...")
        self.db_size_label = QLabel("Loading...")
        self.db_tables_label = QLabel("Loading...")
        self.db_last_backup_label = QLabel("Never")
        
        info_layout.addRow("Database Type:", self.db_type_label)
        info_layout.addRow("Version:", self.db_version_label)
        info_layout.addRow("Size:", self.db_size_label)
        info_layout.addRow("Tables:", self.db_tables_label)
        info_layout.addRow("Last Backup:", self.db_last_backup_label)
        
        layout.addWidget(info_group)
        
        # Database operations section
        operations_group = QGroupBox("Database Operations")
        operations_layout = QGridLayout(operations_group)
        
        optimize_btn = QPushButton("Optimize Database")
        optimize_btn.clicked.connect(self.optimize_database)
        
        repair_btn = QPushButton("Repair Database")
        repair_btn.clicked.connect(self.repair_database)
        
        check_btn = QPushButton("Check Integrity")
        check_btn.clicked.connect(self.check_database_integrity)
        
        reset_btn = QPushButton("Reset Database")
        reset_btn.clicked.connect(self.reset_database)
        reset_btn.setStyleSheet("background-color: #FF9999")
        
        clear_data_btn = QPushButton("Clear All Data")
        clear_data_btn.clicked.connect(self.clear_all_data)
        clear_data_btn.setStyleSheet("background-color: #FF9999")
        
        delete_db_btn = QPushButton("Delete Database")
        delete_db_btn.clicked.connect(self.delete_database)
        delete_db_btn.setStyleSheet("background-color: #FF6666; font-weight: bold;")
        
        operations_layout.addWidget(optimize_btn, 0, 0)
        operations_layout.addWidget(repair_btn, 0, 1)
        operations_layout.addWidget(check_btn, 0, 2)
        operations_layout.addWidget(reset_btn, 1, 0)
        operations_layout.addWidget(clear_data_btn, 1, 1)
        operations_layout.addWidget(delete_db_btn, 1, 2)
        
        layout.addWidget(operations_group)
        
        # Database structure section
        structure_group = QGroupBox("Database Structure")
        structure_layout = QHBoxLayout(structure_group)
        
        # Table list
        self.table_list = QListWidget()
        self.table_list.itemClicked.connect(self.on_table_selected)
        
        # Table details
        table_details_layout = QVBoxLayout()
        self.table_info_label = QLabel("Select a table to view details")
        self.table_info_label.setAlignment(Qt.AlignCenter)
        self.table_info_label.setWordWrap(True)
        
        # Add operations buttons
        table_ops_layout = QHBoxLayout()
        view_data_btn = QPushButton("View Data")
        view_data_btn.clicked.connect(self.view_table_data)
        truncate_btn = QPushButton("Truncate Table")
        truncate_btn.clicked.connect(self.truncate_table)
        truncate_btn.setStyleSheet("background-color: #FF9999")
        table_ops_layout.addWidget(view_data_btn)
        table_ops_layout.addWidget(truncate_btn)
        
        table_details_layout.addWidget(self.table_info_label)
        table_details_layout.addLayout(table_ops_layout)
        
        structure_layout.addWidget(self.table_list, 1)
        structure_layout.addLayout(table_details_layout, 2)
        
        layout.addWidget(structure_group, 1)  # Give it more vertical space
        
        self.tab_widget.addTab(tab, "Database Management")
        
        # Load initial data
        self.load_database_info()
    
    def setup_system_settings_tab(self):
        """Setup the system settings tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Create splitter for settings categories and details
        splitter = QSplitter(Qt.Horizontal)
        
        # Settings categories panel
        categories_widget = QWidget()
        categories_layout = QVBoxLayout(categories_widget)
        categories_layout.setContentsMargins(0, 0, 0, 0)
        
        categories_label = QLabel("Settings Categories")
        categories_label.setFont(QFont("Arial", 12, QFont.Bold))
        
        self.settings_categories = QListWidget()
        self.settings_categories.addItems([
            "General Settings",
            "Security Settings",
            "Email Notifications",
            "Data Retention",
            "Interface Settings",
            "Integration Settings",
            "Advanced Settings"
        ])
        self.settings_categories.currentRowChanged.connect(self.on_settings_category_changed)
        
        categories_layout.addWidget(categories_label)
        categories_layout.addWidget(self.settings_categories)
        
        # Settings details panel
        self.settings_details = QStackedWidget()
        self.setup_settings_pages()
        
        # Add widgets to splitter
        splitter.addWidget(categories_widget)
        splitter.addWidget(self.settings_details)
        splitter.setSizes([200, 600])  # Initial sizes
        
        # Add splitter to main layout
        layout.addWidget(splitter)
        
        # Add save/cancel buttons
        buttons_layout = QHBoxLayout()
        save_btn = QPushButton("Save Settings")
        save_btn.clicked.connect(self.save_settings)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.load_settings)
        buttons_layout.addStretch()
        buttons_layout.addWidget(save_btn)
        buttons_layout.addWidget(cancel_btn)
        layout.addLayout(buttons_layout)
        
        self.tab_widget.addTab(tab, "System Settings")
        
        # Load initial settings
        self.settings_categories.setCurrentRow(0)
        self.load_settings()
    
    def setup_audit_log_tab(self):
        """Setup the audit log tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Filter controls
        filter_layout = QHBoxLayout()
        
        # Date range
        date_layout = QHBoxLayout()
        date_from_label = QLabel("From:")
        self.date_from = QDateEdit()
        self.date_from.setDate(QDate.currentDate().addMonths(-1))
        self.date_from.setCalendarPopup(True)
        date_to_label = QLabel("To:")
        self.date_to = QDateEdit()
        self.date_to.setDate(QDate.currentDate())
        self.date_to.setCalendarPopup(True)
        date_layout.addWidget(date_from_label)
        date_layout.addWidget(self.date_from)
        date_layout.addWidget(date_to_label)
        date_layout.addWidget(self.date_to)
        
        # User filter
        user_layout = QHBoxLayout()
        user_label = QLabel("User:")
        self.user_filter = QComboBox()
        self.user_filter.addItem("All Users")
        user_layout.addWidget(user_label)
        user_layout.addWidget(self.user_filter)
        
        # Action type filter
        action_layout = QHBoxLayout()
        action_label = QLabel("Action:")
        self.action_filter = QComboBox()
        self.action_filter.addItem("All Actions")
        self.action_filter.addItems([
            "Login", "Logout", "Create", "Update", 
            "Delete", "View", "Export", "Import",
            "Database Operation", "System Setting"
        ])
        action_layout.addWidget(action_label)
        action_layout.addWidget(self.action_filter)
        
        # Add filters to main filter layout
        filter_layout.addLayout(date_layout)
        filter_layout.addLayout(user_layout)
        filter_layout.addLayout(action_layout)
        
        # Apply filter button
        apply_filter_btn = QPushButton("Apply Filter")
        apply_filter_btn.clicked.connect(self.load_audit_logs)
        filter_layout.addWidget(apply_filter_btn)
        
        layout.addLayout(filter_layout)
        
        # Audit log table
        self.audit_log = QTreeWidget()
        self.audit_log.setHeaderLabels([
            "Timestamp", "User", "IP Address", "Action", "Details", "Status"
        ])
        self.audit_log.setAlternatingRowColors(True)
        self.audit_log.setSortingEnabled(True)
        layout.addWidget(self.audit_log)
        
        # Export button
        export_layout = QHBoxLayout()
        export_btn = QPushButton("Export Log")
        export_btn.clicked.connect(self.export_audit_log)
        clear_btn = QPushButton("Clear Log")
        clear_btn.clicked.connect(self.clear_audit_log)
        clear_btn.setStyleSheet("background-color: #FF9999")
        export_layout.addStretch()
        export_layout.addWidget(export_btn)
        export_layout.addWidget(clear_btn)
        layout.addLayout(export_layout)
        
        self.tab_widget.addTab(tab, "Audit Log")
        
        # Load initial audit logs
        self.load_audit_log_users()
        self.load_audit_logs()
    
    def setup_backup_restore_tab(self):
        """Setup the backup and restore tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Backup section
        backup_group = QGroupBox("Database Backup")
        backup_layout = QVBoxLayout(backup_group)
        
        # Backup options
        options_layout = QFormLayout()
        
        self.backup_path = QLineEdit()
        self.backup_path.setReadOnly(True)
        backup_path_layout = QHBoxLayout()
        backup_path_layout.addWidget(self.backup_path)
        browse_btn = QPushButton("Browse")
        browse_btn.clicked.connect(self.browse_backup_path)
        backup_path_layout.addWidget(browse_btn)
        options_layout.addRow("Backup Location:", backup_path_layout)
        
        self.compression_level = QComboBox()
        self.compression_level.addItems(["None", "Low", "Medium", "High"])
        self.compression_level.setCurrentIndex(2)  # Default to Medium
        options_layout.addRow("Compression:", self.compression_level)
        
        self.include_attachments = QCheckBox("Include equipment attachments")
        self.include_attachments.setChecked(True)
        options_layout.addRow("", self.include_attachments)
        
        # Add backup buttons
        backup_buttons = QHBoxLayout()
        backup_now_btn = QPushButton("Backup Now")
        backup_now_btn.clicked.connect(self.backup_database)
        schedule_backup_btn = QPushButton("Schedule Backups")
        schedule_backup_btn.clicked.connect(self.schedule_backup)
        backup_buttons.addWidget(backup_now_btn)
        backup_buttons.addWidget(schedule_backup_btn)
        
        backup_layout.addLayout(options_layout)
        backup_layout.addLayout(backup_buttons)
        
        # Restore section
        restore_group = QGroupBox("Database Restore")
        restore_layout = QVBoxLayout(restore_group)
        
        # Restore options
        restore_options = QFormLayout()
        
        self.restore_path = QLineEdit()
        self.restore_path.setReadOnly(True)
        restore_path_layout = QHBoxLayout()
        restore_path_layout.addWidget(self.restore_path)
        browse_restore_btn = QPushButton("Browse")
        browse_restore_btn.clicked.connect(self.browse_restore_file)
        restore_path_layout.addWidget(browse_restore_btn)
        restore_options.addRow("Backup File:", restore_path_layout)
        
        self.restore_options = QComboBox()
        self.restore_options.addItems([
            "Restore database only", 
            "Restore database and attachments",
            "Restore only specific tables"
        ])
        restore_options.addRow("Restore Options:", self.restore_options)
        
        # Add restore button
        restore_btn = QPushButton("Restore Database")
        restore_btn.clicked.connect(self.restore_database)
        restore_btn.setStyleSheet("background-color: #FFCC99")
        
        restore_layout.addLayout(restore_options)
        restore_layout.addWidget(restore_btn)
        
        # Backup history section
        history_group = QGroupBox("Backup History")
        history_layout = QVBoxLayout(history_group)
        
        self.backup_history = QTreeWidget()
        self.backup_history.setHeaderLabels([
            "Date", "Time", "Size", "Type", "Status"
        ])
        self.backup_history.setAlternatingRowColors(True)
        
        history_layout.addWidget(self.backup_history)
        
        # Add all groups to main layout
        layout.addWidget(backup_group)
        layout.addWidget(restore_group)
        layout.addWidget(history_group, 1)  # Give it more vertical space
        
        self.tab_widget.addTab(tab, "Backup & Restore")
        
        # Initialize backup history
        self.load_backup_history()
        
        # Set default backup path
        default_backup_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "backups")
        os.makedirs(default_backup_dir, exist_ok=True)
        self.backup_path.setText(default_backup_dir)
    
    def setup_settings_pages(self):
        """Setup the pages for different settings categories"""
        # General Settings
        general_page = QWidget()
        general_layout = QFormLayout(general_page)
        
        self.app_name = QLineEdit()
        self.company_name = QLineEdit()
        self.timezone = QComboBox()
        self.timezone.addItems([
            "UTC", "US/Eastern", "US/Central", "US/Mountain", "US/Pacific",
            "Europe/London", "Europe/Berlin", "Asia/Tokyo", "Australia/Sydney"
        ])
        
        general_layout.addRow("Application Name:", self.app_name)
        general_layout.addRow("Company Name:", self.company_name)
        general_layout.addRow("Default Timezone:", self.timezone)
        
        # Security Settings
        security_page = QWidget()
        security_layout = QFormLayout(security_page)
        
        self.password_expiry = QComboBox()
        self.password_expiry.addItems([
            "Never", "30 days", "60 days", "90 days", "180 days", "1 year"
        ])
        
        self.min_password_length = QSpinBox()
        self.min_password_length.setMinimum(4)
        self.min_password_length.setMaximum(32)
        
        self.require_special_chars = QCheckBox()
        self.password_history = QSpinBox()
        self.password_history.setMinimum(0)
        self.password_history.setMaximum(10)
        
        self.max_login_attempts = QSpinBox()
        self.max_login_attempts.setMinimum(3)
        self.max_login_attempts.setMaximum(10)
        
        self.session_timeout = QComboBox()
        self.session_timeout.addItems([
            "15 minutes", "30 minutes", "1 hour", "2 hours", "4 hours", "8 hours"
        ])
        
        security_layout.addRow("Password Expiry:", self.password_expiry)
        security_layout.addRow("Minimum Password Length:", self.min_password_length)
        security_layout.addRow("Require Special Characters:", self.require_special_chars)
        security_layout.addRow("Password History:", self.password_history)
        security_layout.addRow("Max Login Attempts:", self.max_login_attempts)
        security_layout.addRow("Session Timeout:", self.session_timeout)
        
        # Email Settings
        email_page = QWidget()
        email_layout = QFormLayout(email_page)
        
        self.email_enabled = QCheckBox("Enable Email Notifications")
        self.email_server = QLineEdit()
        self.email_port = QSpinBox()
        self.email_port.setMinimum(1)
        self.email_port.setMaximum(65535)
        self.email_port.setValue(587)
        self.email_use_tls = QCheckBox("Use TLS")
        self.email_use_tls.setChecked(True)
        self.email_username = QLineEdit()
        self.email_password = QLineEdit()
        self.email_password.setEchoMode(QLineEdit.Password)
        self.email_from_address = QLineEdit()
        
        email_layout.addRow("", self.email_enabled)
        email_layout.addRow("SMTP Server:", self.email_server)
        email_layout.addRow("SMTP Port:", self.email_port)
        email_layout.addRow("", self.email_use_tls)
        email_layout.addRow("Username:", self.email_username)
        email_layout.addRow("Password:", self.email_password)
        email_layout.addRow("From Address:", self.email_from_address)
        
        # Test email button
        test_email_layout = QHBoxLayout()
        self.test_email_address = QLineEdit()
        self.test_email_address.setPlaceholderText("Enter email address for testing")
        test_email_btn = QPushButton("Test Email")
        test_email_btn.clicked.connect(self.test_email_settings)
        test_email_layout.addWidget(self.test_email_address)
        test_email_layout.addWidget(test_email_btn)
        email_layout.addRow("Test Email:", test_email_layout)
        
        # Data Retention Settings
        retention_page = QWidget()
        retention_layout = QFormLayout(retention_page)
        
        self.work_order_retention = QComboBox()
        self.work_order_retention.addItems([
            "Forever", "1 year", "2 years", "3 years", "5 years", "7 years"
        ])
        
        self.report_retention = QComboBox()
        self.report_retention.addItems([
            "Forever", "1 year", "2 years", "3 years", "5 years"
        ])
        
        self.log_retention = QComboBox()
        self.log_retention.addItems([
            "30 days", "60 days", "90 days", "180 days", "1 year", "2 years"
        ])
        
        self.equipment_history_retention = QComboBox()
        self.equipment_history_retention.addItems([
            "Forever", "3 years", "5 years", "7 years", "10 years"
        ])
        
        retention_layout.addRow("Work Order Retention:", self.work_order_retention)
        retention_layout.addRow("Report Retention:", self.report_retention)
        retention_layout.addRow("Log Retention:", self.log_retention)
        retention_layout.addRow("Equipment History Retention:", self.equipment_history_retention)
        
        # Interface Settings
        interface_page = QWidget()
        interface_layout = QFormLayout(interface_page)
        
        self.default_theme = QComboBox()
        self.default_theme.addItems(["Light", "Dark", "System Default"])
        
        self.default_page = QComboBox()
        self.default_page.addItems([
            "Welcome Page", "Equipment", "Craftsmen", 
            "Work Orders", "Inventory", "Reports"
        ])
        
        self.table_row_limit = QSpinBox()
        self.table_row_limit.setMinimum(10)
        self.table_row_limit.setMaximum(1000)
        self.table_row_limit.setValue(100)
        
        interface_layout.addRow("Default Theme:", self.default_theme)
        interface_layout.addRow("Default Start Page:", self.default_page)
        interface_layout.addRow("Table Row Limit:", self.table_row_limit)
        
        # Integration Settings
        integration_page = QWidget()
        integration_layout = QFormLayout(integration_page)
        
        self.enable_web_api = QCheckBox("Enable Web API")
        self.api_key = QLineEdit()
        self.api_key.setReadOnly(True)
        
        api_key_layout = QHBoxLayout()
        api_key_layout.addWidget(self.api_key)
        generate_key_btn = QPushButton("Generate New Key")
        generate_key_btn.clicked.connect(self.generate_api_key)
        api_key_layout.addWidget(generate_key_btn)
        
        self.allowed_origins = QTextEdit()
        self.allowed_origins.setPlaceholderText("Enter one origin per line, e.g. http://example.com")
        
        integration_layout.addRow("", self.enable_web_api)
        integration_layout.addRow("API Key:", api_key_layout)
        integration_layout.addRow("Allowed Origins:", self.allowed_origins)
        
        # Advanced Settings
        advanced_page = QWidget()
        advanced_layout = QFormLayout(advanced_page)
        
        self.debug_mode = QCheckBox("Enable Debug Mode")
        self.logging_level = QComboBox()
        self.logging_level.addItems(["ERROR", "WARNING", "INFO", "DEBUG"])
        
        self.backup_auto = QCheckBox("Automatic Database Backups")
        
        self.backup_frequency = QComboBox()
        self.backup_frequency.addItems([
            "Daily", "Weekly", "Monthly"
        ])
        
        self.max_upload_size = QSpinBox()
        self.max_upload_size.setMinimum(1)
        self.max_upload_size.setMaximum(100)
        self.max_upload_size.setValue(10)
        self.max_upload_size.setSuffix(" MB")
        
        advanced_layout.addRow("", self.debug_mode)
        advanced_layout.addRow("Logging Level:", self.logging_level)
        advanced_layout.addRow("", self.backup_auto)
        advanced_layout.addRow("Backup Frequency:", self.backup_frequency)
        advanced_layout.addRow("Max Upload Size:", self.max_upload_size)
        
        # Add all pages to the stacked widget
        self.settings_details.addWidget(general_page)
        self.settings_details.addWidget(security_page)
        self.settings_details.addWidget(email_page)
        self.settings_details.addWidget(retention_page)
        self.settings_details.addWidget(interface_page)
        self.settings_details.addWidget(integration_page)
        self.settings_details.addWidget(advanced_page)
    
    # User Management Methods
    def load_user_list(self):
        """Load the list of admin users"""
        # Clear existing items
        self.user_list.clear()
        
        # Load users from database
        try:
            users = self.db_manager.get_admin_users()
            for user in users:
                item = QTreeWidgetItem(self.user_list)
                item.setText(0, user['username'])
                item.setText(1, user['role'])
                item.setText(2, user.get('last_login', 'Never'))
                # Store user data in item
                item.setData(0, Qt.UserRole, user)
            
            self.user_list.resizeColumnToContents(0)
            self.user_list.resizeColumnToContents(1)
            self.user_list.resizeColumnToContents(2)
        except Exception as e:
            self.logger.error(f"Error loading admin users: {e}")
            self.status_bar.showMessage(f"Error loading users: {e}", 5000)
    
    def filter_user_list(self):
        """Filter the user list based on search text"""
        search_text = self.user_search.text().lower()
        for i in range(self.user_list.topLevelItemCount()):
            item = self.user_list.topLevelItem(i)
            username = item.text(0).lower()
            role = item.text(1).lower()
            # Get full name from data
            user_data = item.data(0, Qt.UserRole)
            full_name = user_data.get('full_name', '').lower() if user_data else ''
            
            # Show item if search text is in username, role, or full name
            if search_text in username or search_text in role or search_text in full_name:
                item.setHidden(False)
            else:
                item.setHidden(True)
    
    def on_user_selected(self, item):
        """Handle user selection from list"""
        # Enable edit and delete buttons
        self.edit_user_btn.setEnabled(True)
        self.delete_user_btn.setEnabled(True)
        self.reset_password_btn.setEnabled(True)
        
        # Get user data
        user_data = item.data(0, Qt.UserRole)
        if user_data:
            # Update user details panel
            self.user_details_username.setText(user_data.get('username', ''))
            self.user_details_fullname.setText(user_data.get('full_name', ''))
            self.user_details_email.setText(user_data.get('email', ''))
            self.user_details_role.setText(user_data.get('role', ''))
            self.user_details_created.setText(user_data.get('created_date', 'Unknown'))
            self.user_details_last_login.setText(user_data.get('last_login', 'Never'))
            
            # Load permissions
            self.load_user_permissions(user_data.get('user_id'))
        else:
            # Clear user details
            self.user_details_username.setText("")
            self.user_details_fullname.setText("")
            self.user_details_email.setText("")
            self.user_details_role.setText("")
            self.user_details_created.setText("")
            self.user_details_last_login.setText("")
            self.permission_list.clear()
    
    def load_user_permissions(self, user_id):
        """Load permissions for the selected user"""
        self.permission_list.clear()
        
        try:
            # Get user permissions from database
            permissions = self.db_manager.get_admin_permissions(user_id)
            
            # Create permission items
            for perm_category, perm_list in permissions.items():
                # Add category as parent item
                category_item = QTreeWidgetItem(self.permission_list)
                category_item.setText(0, perm_category)
                category_item.setFont(0, QFont("Arial", weight=QFont.Bold))
                
                # Add permissions as child items
                for perm in perm_list:
                    perm_item = QTreeWidgetItem(category_item)
                    perm_item.setText(0, perm['name'])
                    # Set status icon/text based on permission value
                    if perm['granted']:
                        perm_item.setText(1, "Allowed")
                        perm_item.setForeground(1, QColor("#4CAF50"))  # Green
                    else:
                        perm_item.setText(1, "Denied")
                        perm_item.setForeground(1, QColor("#F44336"))  # Red
            
            # Expand all items
            self.permission_list.expandAll()
            
        except Exception as e:
            self.logger.error(f"Error loading user permissions: {e}")
    
    def show_add_user_dialog(self):
        """Show dialog to add a new admin user"""
        dialog = AdminUserDialog(self)
        if dialog.exec():
            # Get user data from dialog
            user_data = dialog.get_user_data()
            
            try:
                # Add user to database
                success = self.db_manager.add_admin_user(user_data)
                if success:
                    self.status_bar.showMessage("User added successfully", 3000)
                    self.log_message.emit(f"Added admin user: {user_data['username']}")
                    # Reload user list
                    self.load_user_list()
                else:
                    QMessageBox.warning(self, "Error", "Failed to add user")
            except Exception as e:
                self.logger.error(f"Error adding user: {e}")
                QMessageBox.critical(self, "Error", f"Error adding user: {e}")
    
    def show_edit_user_dialog(self):
        """Show dialog to edit the selected admin user"""
        selected_items = self.user_list.selectedItems()
        if not selected_items:
            return
        
        # Get user data
        user_data = selected_items[0].data(0, Qt.UserRole)
        if not user_data:
            return
        
        # Show edit dialog
        dialog = AdminUserDialog(self, user_data)
        if dialog.exec():
            # Get updated user data
            updated_data = dialog.get_user_data()
            updated_data['user_id'] = user_data.get('user_id')
            
            try:
                # Update user in database
                success = self.db_manager.update_admin_user(updated_data)
                if success:
                    self.status_bar.showMessage("User updated successfully", 3000)
                    self.log_message.emit(f"Updated admin user: {updated_data['username']}")
                    # Reload user list
                    self.load_user_list()
                else:
                    QMessageBox.warning(self, "Error", "Failed to update user")
            except Exception as e:
                self.logger.error(f"Error updating user: {e}")
                QMessageBox.critical(self, "Error", f"Error updating user: {e}")
    
    def delete_user(self):
        """Delete the selected admin user"""
        selected_items = self.user_list.selectedItems()
        if not selected_items:
            return
        
        # Get user data
        user_data = selected_items[0].data(0, Qt.UserRole)
        if not user_data:
            return
        
        # Confirm deletion
        reply = QMessageBox.question(
            self, 
            "Confirm Deletion",
            f"Are you sure you want to delete the admin user '{user_data['username']}'?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                # Delete user from database
                success = self.db_manager.delete_admin_user(user_data['user_id'])
                if success:
                    self.status_bar.showMessage("User deleted successfully", 3000)
                    self.log_message.emit(f"Deleted admin user: {user_data['username']}")
                    # Reload user list
                    self.load_user_list()
                    # Clear user details
                    self.on_user_selected(None)
                    self.edit_user_btn.setEnabled(False)
                    self.delete_user_btn.setEnabled(False)
                    self.reset_password_btn.setEnabled(False)
                else:
                    QMessageBox.warning(self, "Error", "Failed to delete user")
            except Exception as e:
                self.logger.error(f"Error deleting user: {e}")
                QMessageBox.critical(self, "Error", f"Error deleting user: {e}")
    
    def reset_user_password(self):
        """Reset password for the selected user"""
        selected_items = self.user_list.selectedItems()
        if not selected_items:
            return
        
        # Get user data
        user_data = selected_items[0].data(0, Qt.UserRole)
        if not user_data:
            return
        
        # Show password reset dialog
        dialog = PasswordResetDialog(self)
        if dialog.exec():
            # Get new password
            new_password = dialog.get_password()
            
            try:
                # Reset password in database
                success = self.db_manager.reset_admin_password(
                    user_data['user_id'], new_password)
                if success:
                    self.status_bar.showMessage("Password reset successfully", 3000)
                    self.log_message.emit(f"Reset password for admin user: {user_data['username']}")
                else:
                    QMessageBox.warning(self, "Error", "Failed to reset password")
            except Exception as e:
                self.logger.error(f"Error resetting password: {e}")
                QMessageBox.critical(self, "Error", f"Error resetting password: {e}")
    
    # Database Management Methods
    def load_database_info(self):
        """Load database information"""
        try:
            db_info = self.db_manager.get_database_info()
            
            self.db_type_label.setText(db_info.get('type', 'Unknown'))
            self.db_version_label.setText(db_info.get('version', 'Unknown'))
            self.db_size_label.setText(db_info.get('size', 'Unknown'))
            self.db_tables_label.setText(str(db_info.get('tables', 0)))
            
            # Get last backup time
            last_backup = self.db_manager.get_last_backup_time()
            self.db_last_backup_label.setText(last_backup if last_backup else "Never")
            
            # Load table list
            self.load_table_list()
        except Exception as e:
            self.logger.error(f"Error loading database info: {e}")
            self.status_bar.showMessage(f"Error loading database info: {e}", 5000)
    
    def load_table_list(self):
        """Load list of database tables"""
        try:
            # Clear existing items
            self.table_list.clear()
            
            # Get tables from database
            tables = self.db_manager.get_database_tables()
            
            # Add tables to list
            for table in tables:
                self.table_list.addItem(table)
            
        except Exception as e:
            self.logger.error(f"Error loading table list: {e}")
    
    def on_table_selected(self, item):
        """Handle table selection from list"""
        table_name = item.text()
        
        try:
            # Get table info
            table_info = self.db_manager.get_table_info(table_name)
            
            # Format info text
            info_text = f"<b>Table:</b> {table_name}<br><br>"
            info_text += f"<b>Rows:</b> {table_info.get('rows', 0)}<br>"
            info_text += f"<b>Size:</b> {table_info.get('size', 'Unknown')}<br><br>"
            
            # Add column information
            info_text += "<b>Columns:</b><br>"
            for col in table_info.get('columns', []):
                info_text += f"• {col['name']} ({col['type']})"
                if col.get('key') == 'PRI':
                    info_text += " <i>(Primary Key)</i>"
                elif col.get('key') == 'FOR':
                    info_text += f" <i>(Foreign Key to {col.get('ref_table')})</i>"
                info_text += "<br>"
            
            self.table_info_label.setText(info_text)
            
        except Exception as e:
            self.logger.error(f"Error loading table info: {e}")
            self.table_info_label.setText(f"Error loading table info: {e}")
    
    def view_table_data(self):
        """View data in the selected table"""
        selected_items = self.table_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Warning", "Please select a table first")
            return
        
        table_name = selected_items[0].text()
        
        # Show table data dialog
        dialog = TableDataDialog(self, self.db_manager, table_name)
        dialog.exec()
    
    def truncate_table(self):
        """Truncate (clear) the selected table"""
        selected_items = self.table_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Warning", "Please select a table first")
            return
        
        table_name = selected_items[0].text()
        
        # Confirm truncation
        reply = QMessageBox.question(
            self, 
            "Confirm Truncation",
            f"Are you sure you want to truncate the table '{table_name}'?\n\n"
            "This will permanently delete ALL data in this table.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # Double-check for important tables
            if table_name in ['admin_users', 'equipment_registry', 'craftsmen', 'work_orders']:
                second_reply = QMessageBox.warning(
                    self, 
                    "Critical Table Warning",
                    f"'{table_name}' is a critical table. Truncating it will cause severe disruption.\n\n"
                    "Are you ABSOLUTELY sure you want to continue?",
                    QMessageBox.Yes | QMessageBox.No,
                    QMessageBox.No
                )
                if second_reply != QMessageBox.Yes:
                    return
            
            try:
                # Truncate table
                success = self.db_manager.truncate_table(table_name)
                if success:
                    self.status_bar.showMessage(f"Table '{table_name}' truncated successfully", 3000)
                    self.log_message.emit(f"Truncated table: {table_name}")
                    # Refresh table info
                    self.on_table_selected(selected_items[0])
                else:
                    QMessageBox.warning(self, "Error", f"Failed to truncate table '{table_name}'")
            except Exception as e:
                self.logger.error(f"Error truncating table: {e}")
                QMessageBox.critical(self, "Error", f"Error truncating table: {e}")
    
    def optimize_database(self):
        """Optimize the database (reorganize and defragment)"""
        reply = QMessageBox.question(
            self, 
            "Confirm Optimization",
            "Optimizing the database may take some time depending on its size.\n\n"
            "Do you want to continue?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.Yes
        )
        
        if reply == QMessageBox.Yes:
            # Show progress dialog
            progress_dialog = QProgressDialog("Optimizing database...", "Cancel", 0, 100, self)
            progress_dialog.setWindowTitle("Database Optimization")
            progress_dialog.setWindowModality(Qt.WindowModal)
            progress_dialog.show()
            
            try:
                # Optimize database
                for i in range(101):  # Simulated progress
                    if progress_dialog.wasCanceled():
                        break
                    progress_dialog.setValue(i)
                    if i % 20 == 0:
                        progress_dialog.setLabelText(f"Optimizing database... ({i}%)")
                    time.sleep(0.05)  # Simulate work
                
                if not progress_dialog.wasCanceled():
                    # Perform actual optimization
                    success = self.db_manager.optimize_database()
                    progress_dialog.setValue(100)
                    
                    if success:
                        self.status_bar.showMessage("Database optimized successfully", 3000)
                        self.log_message.emit("Optimized database")
                        # Reload database info
                        self.load_database_info()
                    else:
                        QMessageBox.warning(self, "Error", "Failed to optimize database")
            except Exception as e:
                self.logger.error(f"Error optimizing database: {e}")
                QMessageBox.critical(self, "Error", f"Error optimizing database: {e}")
            finally:
                progress_dialog.close()
    
    def repair_database(self):
        """Repair the database (check and fix errors)"""
        reply = QMessageBox.question(
            self, 
            "Confirm Repair",
            "Repairing the database may take some time.\n\n"
            "Do you want to continue?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.Yes
        )
        
        if reply == QMessageBox.Yes:
            # Show progress dialog
            progress_dialog = QProgressDialog("Repairing database...", "Cancel", 0, 100, self)
            progress_dialog.setWindowTitle("Database Repair")
            progress_dialog.setWindowModality(Qt.WindowModal)
            progress_dialog.show()
            
            try:
                # Repair database
                for i in range(101):  # Simulated progress
                    if progress_dialog.wasCanceled():
                        break
                    progress_dialog.setValue(i)
                    if i % 10 == 0:
                        progress_dialog.setLabelText(f"Repairing database... ({i}%)")
                    time.sleep(0.05)  # Simulate work
                
                if not progress_dialog.wasCanceled():
                    # Perform actual repair
                    result = self.db_manager.repair_database()
                    progress_dialog.setValue(100)
                    
                    if result['success']:
                        self.status_bar.showMessage("Database repaired successfully", 3000)
                        self.log_message.emit(f"Repaired database: {result.get('details', '')}")
                        
                        # Show repair report if issues were found
                        if result.get('issues_found', False):
                            QMessageBox.information(
                                self,
                                "Repair Report",
                                f"Database repair completed with {result.get('issues_fixed', 0)} issues fixed.\n\n"
                                f"Details: {result.get('details', 'No details available')}"
                            )
                        
                        # Reload database info
                        self.load_database_info()
                    else:
                        QMessageBox.warning(
                            self, 
                            "Repair Failed", 
                            f"Failed to repair database: {result.get('error', 'Unknown error')}"
                        )
            except Exception as e:
                self.logger.error(f"Error repairing database: {e}")
                QMessageBox.critical(self, "Error", f"Error repairing database: {e}")
            finally:
                progress_dialog.close()
    
    def check_database_integrity(self):
        """Check the integrity of the database"""
        # Show progress dialog
        progress_dialog = QProgressDialog("Checking database integrity...", "Cancel", 0, 100, self)
        progress_dialog.setWindowTitle("Database Integrity Check")
        progress_dialog.setWindowModality(Qt.WindowModal)
        progress_dialog.show()
        
        try:
            # Check database
            result = {'success': False, 'issues': []}
            for i in range(101):  # Simulated progress
                if progress_dialog.wasCanceled():
                    break
                progress_dialog.setValue(i)
                if i % 10 == 0:
                    progress_dialog.setLabelText(f"Checking database integrity... ({i}%)")
                time.sleep(0.03)  # Simulate work
                
                # Perform actual check at 50%
                if i == 50 and not progress_dialog.wasCanceled():
                    result = self.db_manager.check_database_integrity()
            
            progress_dialog.setValue(100)
            
            if not progress_dialog.wasCanceled():
                if result['success']:
                    # Display results
                    if result.get('issues', []):
                        # Show issues in a detailed dialog
                        issues_text = "\n".join([f"• {issue}" for issue in result['issues']])
                        
                        msg_box = QMessageBox(self)
                        msg_box.setWindowTitle("Integrity Check Results")
                        msg_box.setIcon(QMessageBox.Warning)
                        msg_box.setText(f"Completed with {len(result['issues'])} issues found.")
                        msg_box.setDetailedText(issues_text)
                        msg_box.setStandardButtons(QMessageBox.Ok)
                        msg_box.exec()
                        
                        self.status_bar.showMessage(f"Integrity check completed: {len(result['issues'])} issues found", 5000)
                        self.log_message.emit(f"Database integrity check: {len(result['issues'])} issues found")
                    else:
                        QMessageBox.information(
                            self,
                            "Integrity Check Results",
                            "Database integrity check completed successfully.\n\nNo issues found."
                        )
                        self.status_bar.showMessage("Integrity check completed: No issues found", 5000)
                        self.log_message.emit("Database integrity check: No issues found")
                else:
                    QMessageBox.warning(
                        self, 
                        "Check Failed", 
                        f"Failed to check database integrity: {result.get('error', 'Unknown error')}"
                    )
        except Exception as e:
            self.logger.error(f"Error checking database integrity: {e}")
            QMessageBox.critical(self, "Error", f"Error checking database integrity: {e}")
        finally:
            progress_dialog.close()
    
    def reset_database(self):
        """Reset the database to initial state (keeping structure but clearing data)"""
        reply = QMessageBox.warning(
            self, 
            "Confirm Database Reset",
            "WARNING: This will delete ALL data from the database, keeping only the structure.\n\n"
            "This action CANNOT be undone. Are you sure you want to continue?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # Double-check
            second_reply = QMessageBox.critical(
                self, 
                "FINAL WARNING",
                "ALL DATA WILL BE PERMANENTLY DELETED.\n\n"
                "Please type 'RESET' to confirm:",
                QMessageBox.Cancel
            )
            
            if second_reply == QMessageBox.Cancel:
                # Prompt for confirmation text
                confirmation, ok = QInputDialog.getText(
                    self, 
                    "Confirmation Required", 
                    "Type 'RESET' to confirm database reset:"
                )
                
                if ok and confirmation == "RESET":
                    try:
                        # Perform actual reset
                        success = self.db_manager.reset_database()
                        
                        if success:
                            self.status_bar.showMessage("Database reset successfully", 5000)
                            self.log_message.emit("Reset database to initial state")
                            
                            QMessageBox.information(
                                self,
                                "Reset Complete",
                                "Database has been reset to its initial state.\n\n"
                                "All data has been removed but the structure remains."
                            )
                            
                            # Reload database info
                            self.load_database_info()
                        else:
                            QMessageBox.warning(
                                self, 
                                "Reset Failed", 
                                "Failed to reset database."
                            )
                    except Exception as e:
                        self.logger.error(f"Error resetting database: {e}")
                        QMessageBox.critical(self, "Error", f"Error resetting database: {e}")
    
    def clear_all_data(self):
        """Clear all data from all tables"""
        reply = QMessageBox.warning(
            self, 
            "Confirm Clear All Data",
            "WARNING: This will delete ALL data from ALL tables.\n\n"
            "This action CANNOT be undone. Are you sure you want to continue?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # Double-check
            confirmation, ok = QInputDialog.getText(
                self, 
                "Confirmation Required", 
                "Type 'CLEAR ALL DATA' to confirm:"
            )
            
            if ok and confirmation == "CLEAR ALL DATA":
                try:
                    # Show progress dialog
                    progress_dialog = QProgressDialog("Clearing all data...", "Cancel", 0, 100, self)
                    progress_dialog.setWindowTitle("Clearing Data")
                    progress_dialog.setWindowModality(Qt.WindowModal)
                    progress_dialog.show()
                    
                    # Get all tables
                    tables = self.db_manager.get_database_tables()
                    total_tables = len(tables)
                    
                    # Clear each table
                    success = True
                    for i, table in enumerate(tables):
                        if progress_dialog.wasCanceled():
                            break
                            
                        progress = int((i / total_tables) * 100)
                        progress_dialog.setValue(progress)
                        progress_dialog.setLabelText(f"Clearing table: {table}...")
                        
                        # Truncate table
                        table_success = self.db_manager.truncate_table(table)
                        if not table_success:
                            success = False
                    
                    progress_dialog.setValue(100)
                    
                    if not progress_dialog.wasCanceled():
                        if success:
                            self.status_bar.showMessage("All data cleared successfully", 5000)
                            self.log_message.emit("Cleared all data from all tables")
                            
                            QMessageBox.information(
                                self,
                                "Operation Complete",
                                "All data has been cleared from the database."
                            )
                            
                            # Reload database info
                            self.load_database_info()
                        else:
                            QMessageBox.warning(
                                self, 
                                "Operation Failed", 
                                "Failed to clear all data. Some tables may still contain data."
                            )
                except Exception as e:
                    self.logger.error(f"Error clearing all data: {e}")
                    QMessageBox.critical(self, "Error", f"Error clearing all data: {e}")
                finally:
                    progress_dialog.close()
    
    def delete_database(self):
        """Delete the entire database"""
        reply = QMessageBox.critical(
            self, 
            "CONFIRM DATABASE DELETION",
            "WARNING: This will DELETE THE ENTIRE DATABASE including all structure and data.\n\n"
            "This action CANNOT be undone and will require reinstallation.\n\n"
            "Are you ABSOLUTELY sure you want to continue?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # Triple-check with password
            admin_password, ok = QInputDialog.getText(
                self, 
                "Admin Authentication Required", 
                "Enter admin password to confirm database deletion:",
                QLineEdit.Password
            )
            
            if ok and admin_password:
                # Verify admin password
                if self.db_manager.verify_admin_password(admin_password):
                    # Final confirmation
                    confirmation, ok = QInputDialog.getText(
                        self, 
                        "FINAL CONFIRMATION", 
                        "Type 'DELETE DATABASE PERMANENTLY' to confirm:"
                    )
                    
                    if ok and confirmation == "DELETE DATABASE PERMANENTLY":
                        try:
                            # Delete database
                            success = self.db_manager.delete_database()
                            
                            if success:
                                self.log_message.emit("Deleted entire database")
                                
                                QMessageBox.critical(
                                    self,
                                    "Database Deleted",
                                    "The database has been permanently deleted.\n\n"
                                    "The application will now close. Reinstallation will be required."
                                )
                                
                                # Close application
                                QApplication.quit()
                            else:
                                QMessageBox.warning(
                                    self, 
                                    "Deletion Failed", 
                                    "Failed to delete database."
                                )
                        except Exception as e:
                            self.logger.error(f"Error deleting database: {e}")
                            QMessageBox.critical(self, "Error", f"Error deleting database: {e}")
                else:
                    QMessageBox.warning(
                        self, 
                        "Authentication Failed", 
                        "Incorrect admin password. Database deletion canceled."
                    )

    # Settings Methods
    def on_settings_category_changed(self, row):
        """Change the settings page when category is selected"""
        self.settings_details.setCurrentIndex(row)
    
    def load_settings(self):
        """Load settings from database"""
        try:
            settings = self.db_manager.get_system_settings()
            
            # General Settings
            self.app_name.setText(settings.get('app_name', 'CMMS'))
            self.company_name.setText(settings.get('company_name', ''))
            
            timezone = settings.get('timezone', 'UTC')
            timezone_index = self.timezone.findText(timezone)
            self.timezone.setCurrentIndex(timezone_index if timezone_index >= 0 else 0)
            
            # Security Settings
            password_expiry = settings.get('password_expiry', 'Never')
            expiry_index = self.password_expiry.findText(password_expiry)
            self.password_expiry.setCurrentIndex(expiry_index if expiry_index >= 0 else 0)
            
            self.min_password_length.setValue(settings.get('min_password_length', 8))
            self.require_special_chars.setChecked(settings.get('require_special_chars', False))
            self.password_history.setValue(settings.get('password_history', 5))
            self.max_login_attempts.setValue(settings.get('max_login_attempts', 5))
            
            session_timeout = settings.get('session_timeout', '1 hour')
            timeout_index = self.session_timeout.findText(session_timeout)
            self.session_timeout.setCurrentIndex(timeout_index if timeout_index >= 0 else 2)  # Default to 1 hour
            
            # Email Settings
            self.email_enabled.setChecked(settings.get('email_enabled', False))
            self.email_server.setText(settings.get('email_server', ''))
            self.email_port.setValue(settings.get('email_port', 587))
            self.email_use_tls.setChecked(settings.get('email_use_tls', True))
            self.email_username.setText(settings.get('email_username', ''))
            self.email_password.setText(settings.get('email_password', ''))
            self.email_from_address.setText(settings.get('email_from_address', ''))
            
            # Data Retention Settings
            work_order_retention = settings.get('work_order_retention', 'Forever')
            self.work_order_retention.setCurrentText(work_order_retention)
            
            report_retention = settings.get('report_retention', 'Forever')
            self.report_retention.setCurrentText(report_retention)
            
            log_retention = settings.get('log_retention', '90 days')
            self.log_retention.setCurrentText(log_retention)
            
            equipment_history_retention = settings.get('equipment_history_retention', 'Forever')
            self.equipment_history_retention.setCurrentText(equipment_history_retention)
            
            # Interface Settings
            default_theme = settings.get('default_theme', 'Dark')
            self.default_theme.setCurrentText(default_theme)
            
            default_page = settings.get('default_page', 'Welcome Page')
            self.default_page.setCurrentText(default_page)
            
            self.table_row_limit.setValue(settings.get('table_row_limit', 100))
            
            # Integration Settings
            self.enable_web_api.setChecked(settings.get('enable_web_api', False))
            self.api_key.setText(settings.get('api_key', ''))
            self.allowed_origins.setPlainText(settings.get('allowed_origins', ''))
            
            # Advanced Settings
            self.debug_mode.setChecked(settings.get('debug_mode', False))
            
            logging_level = settings.get('logging_level', 'INFO')
            self.logging_level.setCurrentText(logging_level)
            
            self.backup_auto.setChecked(settings.get('backup_auto', False))
            
            backup_frequency = settings.get('backup_frequency', 'Weekly')
            self.backup_frequency.setCurrentText(backup_frequency)
            
            self.max_upload_size.setValue(settings.get('max_upload_size', 10))
            
        except Exception as e:
            self.logger.error(f"Error loading settings: {e}")
            self.status_bar.showMessage(f"Error loading settings: {e}", 5000)
    
    def save_settings(self):
        """Save settings to database"""
        try:
            # Collect settings from all pages
            settings = {
                # General Settings
                'app_name': self.app_name.text(),
                'company_name': self.company_name.text(),
                'timezone': self.timezone.currentText(),
                
                # Security Settings
                'password_expiry': self.password_expiry.currentText(),
                'min_password_length': self.min_password_length.value(),
                'require_special_chars': self.require_special_chars.isChecked(),
                'password_history': self.password_history.value(),
                'max_login_attempts': self.max_login_attempts.value(),
                'session_timeout': self.session_timeout.currentText(),
                
                # Email Settings
                'email_enabled': self.email_enabled.isChecked(),
                'email_server': self.email_server.text(),
                'email_port': self.email_port.value(),
                'email_use_tls': self.email_use_tls.isChecked(),
                'email_username': self.email_username.text(),
                'email_password': self.email_password.text(),
                'email_from_address': self.email_from_address.text(),
                
                # Data Retention Settings
                'work_order_retention': self.work_order_retention.currentText(),
                'report_retention': self.report_retention.currentText(),
                'log_retention': self.log_retention.currentText(),
                'equipment_history_retention': self.equipment_history_retention.currentText(),
                
                # Interface Settings
                'default_theme': self.default_theme.currentText(),
                'default_page': self.default_page.currentText(),
                'table_row_limit': self.table_row_limit.value(),
                
                # Integration Settings
                'enable_web_api': self.enable_web_api.isChecked(),
                'api_key': self.api_key.text(),
                'allowed_origins': self.allowed_origins.toPlainText(),
                
                # Advanced Settings
                'debug_mode': self.debug_mode.isChecked(),
                'logging_level': self.logging_level.currentText(),
                'backup_auto': self.backup_auto.isChecked(),
                'backup_frequency': self.backup_frequency.currentText(),
                'max_upload_size': self.max_upload_size.value()
            }
            
            # Save settings to database
            success = self.db_manager.save_system_settings(settings)
            
            if success:
                self.status_bar.showMessage("Settings saved successfully", 3000)
                self.log_message.emit("Updated system settings")
                
                # Apply certain settings immediately
                if settings['debug_mode']:
                    logging.getLogger().setLevel(
                        getattr(logging, settings['logging_level'])
                    )
                
                # Notify user about some settings requiring restart
                QMessageBox.information(
                    self,
                    "Settings Saved",
                    "Settings have been saved successfully.\n\n"
                    "Note: Some settings (like theme changes) will take effect after restarting the application."
                )
            else:
                QMessageBox.warning(self, "Error", "Failed to save settings")
        except Exception as e:
            self.logger.error(f"Error saving settings: {e}")
            QMessageBox.critical(self, "Error", f"Error saving settings: {e}")
    
    def generate_api_key(self):
        """Generate a new API key"""
        # Generate a random key
        api_key = hashlib.sha256(os.urandom(32)).hexdigest()
        
        # Set the key in the text field
        self.api_key.setText(api_key)
        
        # Notify user
        self.status_bar.showMessage("New API key generated (remember to save settings)", 5000)
    
    def test_email_settings(self):
        """Test email settings by sending a test email"""
        # Get email address for test
        test_email = self.test_email_address.text().strip()
        if not test_email:
            QMessageBox.warning(
                self,
                "Missing Information",
                "Please enter an email address for testing."
            )
            return
        
        # Validate email format
        import re
        if not re.match(r"[^@]+@[^@]+\.[^@]+", test_email):
            QMessageBox.warning(
                self,
                "Invalid Email",
                "Please enter a valid email address."
            )
            return
        
        # Get email settings
        settings = {
            'enabled': self.email_enabled.isChecked(),
            'server': self.email_server.text(),
            'port': self.email_port.value(),
            'use_tls': self.email_use_tls.isChecked(),
            'username': self.email_username.text(),
            'password': self.email_password.text(),
            'from_address': self.email_from_address.text()
        }
        
        # Validate settings
        if not settings['server'] or not settings['from_address']:
            QMessageBox.warning(
                self,
                "Missing Information",
                "Please enter SMTP server and From email address."
            )
            return
        
        # Show progress dialog
        progress = QProgressDialog("Sending test email...", "Cancel", 0, 100, self)
        progress.setWindowTitle("Email Test")
        progress.setWindowModality(Qt.WindowModal)
        progress.show()
        
        try:
            # Send test email
            for i in range(1, 101):
                if progress.wasCanceled():
                    break
                progress.setValue(i)
                
                if i == 25:
                    progress.setLabelText("Connecting to mail server...")
                elif i == 50:
                    progress.setLabelText("Authenticating...")
                elif i == 75:
                    progress.setLabelText("Sending test message...")
                    
                time.sleep(0.03)  # Simulate work
                
                # Actual send at 80%
                if i == 80:
                    result = self.db_manager.send_test_email(settings, test_email)
            
            progress.setValue(100)
            
            # Show result
            if not progress.wasCanceled():
                if result['success']:
                    QMessageBox.information(
                        self,
                        "Test Successful",
                        f"Test email successfully sent to {test_email}.\n\n"
                        "If you don't receive it, please check your spam folder."
                    )
                else:
                    QMessageBox.warning(
                        self,
                        "Test Failed",
                        f"Failed to send test email: {result.get('error', 'Unknown error')}"
                    )
        except Exception as e:
            self.logger.error(f"Error sending test email: {e}")
            QMessageBox.critical(self, "Error", f"Error sending test email: {e}")
        finally:
            progress.close()
    
    # Audit Log Methods
    def load_audit_log_users(self):
        """Load the list of users for the audit log filter"""
        try:
            # Clear existing items
            self.user_filter.clear()
            self.user_filter.addItem("All Users")
            
            # Get users from database
            users = self.db_manager.get_audit_log_users()
            for user in users:
                self.user_filter.addItem(user)
        except Exception as e:
            self.logger.error(f"Error loading audit log users: {e}")
    
    def load_audit_logs(self):
        """Load audit logs based on filter settings"""
        try:
            # Get filter values
            from_date = self.date_from.date().toString("yyyy-MM-dd")
            to_date = self.date_to.date().toString("yyyy-MM-dd")
            user = self.user_filter.currentText()
            action = self.action_filter.currentText()
            
            # Apply filters
            if user == "All Users":
                user = None
            if action == "All Actions":
                action = None
            
            # Get logs from database
            logs = self.db_manager.get_audit_logs(from_date, to_date, user, action)
            
            # Clear existing items
            self.audit_log.clear()
            
            # Add logs to treeview
            for log in logs:
                item = QTreeWidgetItem(self.audit_log)
                item.setText(0, log.get('timestamp', ''))
                item.setText(1, log.get('username', ''))
                item.setText(2, log.get('ip_address', ''))
                item.setText(3, log.get('action', ''))
                item.setText(4, log.get('details', ''))
                
                # Style status based on success/failure
                status = log.get('status', '')
                item.setText(5, status)
                if status.lower() == 'success':
                    item.setForeground(5, QColor("#4CAF50"))  # Green
                elif status.lower() == 'failure':
                    item.setForeground(5, QColor("#F44336"))  # Red
            
            # Auto-resize columns
            for i in range(6):
                self.audit_log.resizeColumnToContents(i)
            
            # Update status
            self.status_bar.showMessage(f"Loaded {len(logs)} audit log entries", 3000)
        except Exception as e:
            self.logger.error(f"Error loading audit logs: {e}")
            self.status_bar.showMessage(f"Error loading audit logs: {e}", 5000)
    
    def export_audit_log(self):
        """Export the audit log to CSV or Excel"""
        # Open file dialog to get save location
        file_path, file_filter = QFileDialog.getSaveFileName(
            self,
            "Export Audit Log",
            "",
            "CSV Files (*.csv);;Excel Files (*.xlsx)"
        )
        
        if not file_path:
            return
        
        # Determine export format
        export_format = "csv" if file_filter.startswith("CSV") else "excel"
        
        try:
            # Get filter values
            from_date = self.date_from.date().toString("yyyy-MM-dd")
            to_date = self.date_to.date().toString("yyyy-MM-dd")
            user = self.user_filter.currentText()
            action = self.action_filter.currentText()
            
            # Apply filters
            if user == "All Users":
                user = None
            if action == "All Actions":
                action = None
            
            # Show progress dialog
            progress = QProgressDialog("Exporting audit log...", "Cancel", 0, 100, self)
            progress.setWindowTitle("Export Progress")
            progress.setWindowModality(Qt.WindowModal)
            progress.show()
            
            # Export the log
            for i in range(1, 101):
                if progress.wasCanceled():
                    break
                progress.setValue(i)
                
                if i == 25:
                    progress.setLabelText("Fetching log data...")
                elif i == 50:
                    progress.setLabelText("Processing data...")
                elif i == 75:
                    progress.setLabelText(f"Writing {export_format.upper()} file...")
                
                time.sleep(0.03)  # Simulate work
                
                # Actual export at 80%
                if i == 80:
                    result = self.db_manager.export_audit_log(
                        file_path, export_format, from_date, to_date, user, action
                    )
            
            progress.setValue(100)
            
            # Show result
            if not progress.wasCanceled():
                if result['success']:
                    self.status_bar.showMessage(f"Audit log exported to {file_path}", 5000)
                    self.log_message.emit(f"Exported audit log to {export_format.upper()} file")
                    
                    QMessageBox.information(
                        self,
                        "Export Successful",
                        f"Audit log successfully exported to {file_path}"
                    )
                else:
                    QMessageBox.warning(
                        self,
                        "Export Failed",
                        f"Failed to export audit log: {result.get('error', 'Unknown error')}"
                    )
        except Exception as e:
            self.logger.error(f"Error exporting audit log: {e}")
            QMessageBox.critical(self, "Error", f"Error exporting audit log: {e}")
        finally:
            progress.close()
    
    def clear_audit_log(self):
        """Clear the audit log entries"""
        reply = QMessageBox.warning(
            self, 
            "Confirm Clear Audit Log",
            "Are you sure you want to clear the audit log?\n\n"
            "This will permanently delete all audit log entries matching your current filter.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # Ask for retention option
            options = ["Delete all audit logs", "Keep the last 30 days", "Keep the last 90 days"]
            option, ok = QInputDialog.getItem(
                self,
                "Clear Options",
                "Select which log entries to delete:",
                options,
                0,
                False
            )
            
            if ok:
                try:
                    # Determine retention period
                    retention_days = 0
                    if option == options[1]:  # Keep the last 30 days
                        retention_days = 30
                    elif option == options[2]:  # Keep the last 90 days
                        retention_days = 90
                    
                    # Clear the logs
                    success = self.db_manager.clear_audit_logs(retention_days)
                    
                    if success:
                        self.status_bar.showMessage("Audit log cleared successfully", 3000)
                        self.log_message.emit(f"Cleared audit log with retention: {option}")
                        
                        # Reload logs
                        self.load_audit_logs()
                    else:
                        QMessageBox.warning(self, "Error", "Failed to clear audit log")
                except Exception as e:
                    self.logger.error(f"Error clearing audit log: {e}")
                    QMessageBox.critical(self, "Error", f"Error clearing audit log: {e}")
    
    def log_to_audit(self, message):
        """Add a message to the audit log"""
        try:
            # Log admin action
            self.db_manager.add_audit_log_entry(
                username="Admin",
                action="Admin Action",
                details=message,
                status="Success"
            )
        except Exception as e:
            self.logger.error(f"Error logging to audit: {e}")
    
    # Backup and Restore Methods
    def load_backup_history(self):
        """Load backup history from database"""
        try:
            # Clear existing items
            self.backup_history.clear()
            
            # Get backup history from database
            backups = self.db_manager.get_backup_history()
            
            # Add backups to tree
            for backup in backups:
                item = QTreeWidgetItem(self.backup_history)
                item.setText(0, backup.get('date', ''))
                item.setText(1, backup.get('time', ''))
                item.setText(2, backup.get('size', ''))
                item.setText(3, backup.get('type', ''))
                
                # Style status based on success/failure
                status = backup.get('status', '')
                item.setText(4, status)
                if status.lower() == 'success':
                    item.setForeground(4, QColor("#4CAF50"))  # Green
                elif status.lower() == 'failure':
                    item.setForeground(4, QColor("#F44336"))  # Red
            
            # Resize columns to contents
            for i in range(5):
                self.backup_history.resizeColumnToContents(i)
                
        except Exception as e:
            self.logger.error(f"Error loading backup history: {e}")
    
    def browse_backup_path(self):
        """Open file dialog to select backup location"""
        directory = QFileDialog.getExistingDirectory(
            self,
            "Select Backup Location",
            self.backup_path.text(),
            QFileDialog.ShowDirsOnly
        )
        
        if directory:
            self.backup_path.setText(directory)
    
    def browse_restore_file(self):
        """Open file dialog to select backup file for restore"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Backup File",
            self.backup_path.text(),
            "Backup Files (*.cmmsbackup *.sql *.zip);;All Files (*.*)"
        )
        
        if file_path:
            self.restore_path.setText(file_path)
    
    def backup_database(self):
        """Perform a database backup"""
        # Get backup options
        backup_options = {
            'path': self.backup_path.text(),
            'compression': self.compression_level.currentText().lower(),
            'include_attachments': self.include_attachments.isChecked()
        }
        
        # Validate backup path
        if not backup_options['path'] or not os.path.isdir(backup_options['path']):
            QMessageBox.warning(
                self,
                "Invalid Path",
                "Please select a valid backup location."
            )
            return
        
        # Generate backup filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = f"cmms_backup_{timestamp}.cmmsbackup"
        backup_options['filename'] = backup_file
        backup_options['full_path'] = os.path.join(backup_options['path'], backup_file)
        
        # Show progress dialog
        progress = QProgressDialog("Starting backup...", "Cancel", 0, 100, self)
        progress.setWindowTitle("Database Backup")
        progress.setWindowModality(Qt.WindowModal)
        progress.show()
        
        try:
            backup_result = {'success': False, 'message': ''}
            
            for i in range(1, 101):
                if progress.wasCanceled():
                    break
                progress.setValue(i)
                
                if i == 10:
                    progress.setLabelText("Preparing database for backup...")
                elif i == 30:
                    progress.setLabelText("Exporting database structure...")
                elif i == 50:
                    progress.setLabelText("Exporting data...")
                elif i == 70:
                    progress.setLabelText("Compressing backup file...")
                    if backup_options['include_attachments']:
                        progress.setLabelText("Including attachments...")
                
                time.sleep(0.05)  # Simulate work
                
                # Actual backup at 80%
                if i == 80:
                    backup_result = self.db_manager.backup_database(backup_options)
            
            progress.setValue(100)
            
            # Show result
            if not progress.wasCanceled():
                if backup_result['success']:
                    # Add to backup history
                    self.load_backup_history()
                    
                    # Get backup file size
                    file_size = os.path.getsize(backup_options['full_path'])
                    file_size_str = self.format_file_size(file_size)
                    
                    self.status_bar.showMessage(f"Backup completed: {file_size_str}", 5000)
                    self.log_message.emit(f"Created database backup: {backup_file} ({file_size_str})")
                    
                    QMessageBox.information(
                        self,
                        "Backup Complete",
                        f"Database backup completed successfully.\n\n"
                        f"Location: {backup_options['full_path']}\n"
                        f"Size: {file_size_str}"
                    )
                else:
                    QMessageBox.warning(
                        self,
                        "Backup Failed",
                        f"Failed to backup database: {backup_result.get('message', 'Unknown error')}"
                    )
        except Exception as e:
            self.logger.error(f"Error backing up database: {e}")
            QMessageBox.critical(self, "Error", f"Error backing up database: {e}")
        finally:
            progress.close()
    
    def format_file_size(self, size_bytes):
        """Format file size in bytes to human-readable format"""
        if size_bytes < 1024:
            return f"{size_bytes} bytes"
        elif size_bytes < 1024 * 1024:
            return f"{size_bytes / 1024:.2f} KB"
        elif size_bytes < 1024 * 1024 * 1024:
            return f"{size_bytes / (1024 * 1024):.2f} MB"
        else:
            return f"{size_bytes / (1024 * 1024 * 1024):.2f} GB"
    
    def schedule_backup(self):
        """Show dialog to schedule automatic backups"""
        dialog = BackupScheduleDialog(self, self.db_manager)
        if dialog.exec():
            # Get schedule settings
            schedule_settings = dialog.get_schedule_settings()
            
            try:
                # Save schedule settings
                success = self.db_manager.save_backup_schedule(schedule_settings)
                
                if success:
                    self.status_bar.showMessage("Backup schedule saved", 3000)
                    self.log_message.emit(f"Updated backup schedule: {schedule_settings['frequency']}")
                else:
                    QMessageBox.warning(self, "Error", "Failed to save backup schedule")
            except Exception as e:
                self.logger.error(f"Error saving backup schedule: {e}")
                QMessageBox.critical(self, "Error", f"Error saving backup schedule: {e}")
    
    def restore_database(self):
        """Restore database from backup file"""
        # Get restore file path
        restore_file = self.restore_path.text()
        
        # Validate file path
        if not restore_file or not os.path.isfile(restore_file):
            QMessageBox.warning(
                self,
                "Invalid File",
                "Please select a valid backup file."
            )
            return
        
        # Get restore options
        restore_option = self.restore_options.currentText()
        
        # Confirm restore
        reply = QMessageBox.warning(
            self,
            "Confirm Restore",
            f"Are you sure you want to restore the database from:\n{restore_file}\n\n"
            f"Option: {restore_option}\n\n"
            "WARNING: This will overwrite your current database. This action cannot be undone.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # Double-check with password
            admin_password, ok = QInputDialog.getText(
                self,
                "Admin Authentication Required",
                "Enter admin password to confirm database restore:",
                QLineEdit.Password
            )
            
            if ok and admin_password:
                # Verify admin password
                if not self.db_manager.verify_admin_password(admin_password):
                    QMessageBox.warning(
                        self,
                        "Authentication Failed",
                        "Incorrect admin password. Database restore canceled."
                    )
                    return
                
                # Set up restore options
                restore_options = {
                    'file_path': restore_file,
                    'restore_attachments': 'attachments' in restore_option.lower(),
                    'specific_tables': []
                }
                
                # If restore specific tables, show table selection dialog
                if 'specific tables' in restore_option.lower():
                    tables = self.db_manager.get_database_tables()
                    selected_tables, ok = TableSelectionDialog.get_selected_tables(self, tables)
                    
                    if not ok or not selected_tables:
                        return
                    
                    restore_options['specific_tables'] = selected_tables
                
                # Show progress dialog
                progress = QProgressDialog("Starting restore...", "Cancel", 0, 100, self)
                progress.setWindowTitle("Database Restore")
                progress.setWindowModality(Qt.WindowModal)
                progress.show()
                
                try:
                    restore_result = {'success': False, 'message': ''}
                    
                    for i in range(1, 101):
                        if progress.wasCanceled():
                            break
                        progress.setValue(i)
                        
                        if i == 10:
                            progress.setLabelText("Validating backup file...")
                        elif i == 20:
                            progress.setLabelText("Creating backup of current database...")
                        elif i == 40:
                            progress.setLabelText("Preparing to restore...")
                        elif i == 60:
                            progress.setLabelText("Restoring database structure...")
                        elif i == 80:
                            progress.setLabelText("Restoring data...")
                            if restore_options['restore_attachments']:
                                progress.setLabelText("Restoring attachments...")
                        
                        time.sleep(0.05)  # Simulate work
                        
                        # Actual restore at 90%
                        if i == 90:
                            restore_result = self.db_manager.restore_database(restore_options)
                    
                    progress.setValue(100)
                    
                    # Show result
                    if not progress.wasCanceled():
                        if restore_result['success']:
                            self.status_bar.showMessage("Database restored successfully", 5000)
                            self.log_message.emit(f"Restored database from backup: {restore_file}")
                            
                            QMessageBox.information(
                                self,
                                "Restore Complete",
                                "Database restored successfully.\n\n"
                                "The application will now restart to apply changes."
                            )
                            
                            # Restart application (simulated)
                            QApplication.quit()
                        else:
                            QMessageBox.warning(
                                self,
                                "Restore Failed",
                                f"Failed to restore database: {restore_result.get('message', 'Unknown error')}"
                            )
                except Exception as e:
                    self.logger.error(f"Error restoring database: {e}")
                    QMessageBox.critical(self, "Error", f"Error restoring database: {e}")
                finally:
                    progress.close()


class AdminUserDialog(QDialog):
    """Dialog for adding or editing admin users"""
    
    def __init__(self, parent=None, user_data=None):
        super().__init__(parent)
        
        self.user_data = user_data  # None for new user, dict for editing
        self.setWindowTitle("Add Admin User" if not user_data else "Edit Admin User")
        self.setMinimumWidth(400)
        
        # Create layout
        layout = QVBoxLayout(self)
        
        # Form layout for user details
        form_layout = QFormLayout()
        
        # Username
        self.username = QLineEdit()
        if user_data:
            self.username.setText(user_data.get('username', ''))
            self.username.setReadOnly(True)  # Don't allow username changes
        form_layout.addRow("Username:", self.username)
        
        # Full name
        self.full_name = QLineEdit()
        if user_data:
            self.full_name.setText(user_data.get('full_name', ''))
        form_layout.addRow("Full Name:", self.full_name)
        
        # Email
        self.email = QLineEdit()
        if user_data:
            self.email.setText(user_data.get('email', ''))
        form_layout.addRow("Email:", self.email)
        
        # Role
        self.role = QComboBox()
        self.role.addItems(["Administrator", "Super Admin", "System Admin", "Read-Only Admin"])
        if user_data:
            role_index = self.role.findText(user_data.get('role', 'Administrator'))
            self.role.setCurrentIndex(role_index if role_index >= 0 else 0)
        form_layout.addRow("Role:", self.role)
        
        # Password fields (only for new users or password reset)
        if not user_data:
            self.password = QLineEdit()
            self.password.setEchoMode(QLineEdit.Password)
            self.confirm_password = QLineEdit()
            self.confirm_password.setEchoMode(QLineEdit.Password)
            form_layout.addRow("Password:", self.password)
            form_layout.addRow("Confirm Password:", self.confirm_password)
        
        layout.addLayout(form_layout)
        
        # Permission section for editing users
        if user_data:
            permission_group = QGroupBox("Permissions")
            permission_layout = QVBoxLayout(permission_group)
            
            # Create permission tree widget
            self.permission_tree = QTreeWidget()
            self.permission_tree.setHeaderLabels(["Permission", "Status"])
            self.permission_tree.setAlternatingRowColors(True)
            permission_layout.addWidget(self.permission_tree)
            
            # Load permissions
            self.load_permissions(user_data.get('user_id'))
            
            layout.addWidget(permission_group)
        
        # Button box
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.validate_and_accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
    
    def load_permissions(self, user_id):
        """Load permissions for the user being edited"""
        try:
            # Get user permissions from the database manager
            permissions = self.parent().db_manager.get_admin_permissions(user_id)
            
            # Create permission items
            for perm_category, perm_list in permissions.items():
                # Add category as parent item
                category_item = QTreeWidgetItem(self.permission_tree)
                category_item.setText(0, perm_category)
                category_item.setFont(0, QFont("Arial", weight=QFont.Bold))
                
                # Add permissions as child items
                for perm in perm_list:
                    perm_item = QTreeWidgetItem(category_item)
                    perm_item.setText(0, perm['name'])
                    
                    # Add checkbox for permission
                    checkbox = QCheckBox()
                    checkbox.setChecked(perm['granted'])
                    self.permission_tree.setItemWidget(perm_item, 1, checkbox)
                    
                    # Store permission id in item data
                    perm_item.setData(0, Qt.UserRole, perm['id'])
            
            # Expand all items
            self.permission_tree.expandAll()
            
        except Exception as e:
            print(f"Error loading permissions: {e}")
    
    def validate_and_accept(self):
        """Validate the form and accept if valid"""
        # Get values
        username = self.username.text().strip()
        full_name = self.full_name.text().strip()
        email = self.email.text().strip()
        role = self.role.currentText()
        
        # Validate username
        if not username:
            QMessageBox.warning(self, "Validation Error", "Username is required")
            return
        
        # Validate email
        import re
        if email and not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            QMessageBox.warning(self, "Validation Error", "Please enter a valid email address")
            return
        
        # Validate password for new users
        if not self.user_data:
            password = self.password.text()
            confirm_password = self.confirm_password.text()
            
            if not password:
                QMessageBox.warning(self, "Validation Error", "Password is required for new users")
                return
            
            if password != confirm_password:
                QMessageBox.warning(self, "Validation Error", "Passwords do not match")
                return
            
            if len(password) < 8:
                QMessageBox.warning(self, "Validation Error", "Password must be at least 8 characters long")
                return
        
        # Get updated permissions if editing
        permissions = []
        if self.user_data:
            for i in range(self.permission_tree.topLevelItemCount()):
                category_item = self.permission_tree.topLevelItem(i)
                
                for j in range(category_item.childCount()):
                    perm_item = category_item.child(j)
                    perm_id = perm_item.data(0, Qt.UserRole)
                    checkbox = self.permission_tree.itemWidget(perm_item, 1)
                    
                    permissions.append({
                        'id': perm_id,
                        'granted': checkbox.isChecked()
                    })
        
        # Accept the dialog
        self.accept()
    
    def get_user_data(self):
        """Get the user data from the form"""
        data = {
            'username': self.username.text().strip(),
            'full_name': self.full_name.text().strip(),
            'email': self.email.text().strip(),
            'role': self.role.currentText()
        }
        
        # Add password for new users
        if not self.user_data:
            data['password'] = self.password.text()
        
        # Add permissions for existing users
        if self.user_data:
            permissions = []
            for i in range(self.permission_tree.topLevelItemCount()):
                category_item = self.permission_tree.topLevelItem(i)
                
                for j in range(category_item.childCount()):
                    perm_item = category_item.child(j)
                    perm_id = perm_item.data(0, Qt.UserRole)
                    checkbox = self.permission_tree.itemWidget(perm_item, 1)
                    
                    permissions.append({
                        'id': perm_id,
                        'granted': checkbox.isChecked()
                    })
            
            data['permissions'] = permissions
        
        return data


class PasswordResetDialog(QDialog):
    """Dialog for resetting user passwords"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.setWindowTitle("Reset Password")
        self.setMinimumWidth(400)
        
        # Create layout
        layout = QVBoxLayout(self)
        
        # Form layout for password fields
        form_layout = QFormLayout()
        
        # Password fields
        self.password = QLineEdit()
        self.password.setEchoMode(QLineEdit.Password)
        self.confirm_password = QLineEdit()
        self.confirm_password.setEchoMode(QLineEdit.Password)
        
        form_layout.addRow("New Password:", self.password)
        form_layout.addRow("Confirm Password:", self.confirm_password)
        
        layout.addLayout(form_layout)
        
        # Password strength indicator
        strength_layout = QHBoxLayout()
        strength_label = QLabel("Password Strength:")
        self.strength_indicator = QProgressBar()
        self.strength_indicator.setRange(0, 100)
        self.strength_indicator.setValue(0)
        self.strength_indicator.setTextVisible(False)
        self.strength_text = QLabel("Very Weak")
        
        strength_layout.addWidget(strength_label)
        strength_layout.addWidget(self.strength_indicator, 1)
        strength_layout.addWidget(self.strength_text)
        
        layout.addLayout(strength_layout)
        
        # Password requirements
        requirements_group = QGroupBox("Password Requirements")
        requirements_layout = QVBoxLayout(requirements_group)
        
        self.req_length = QLabel("✘ At least 8 characters")
        self.req_upper = QLabel("✘ At least one uppercase letter")
        self.req_lower = QLabel("✘ At least one lowercase letter")
        self.req_digit = QLabel("✘ At least one digit")
        self.req_special = QLabel("✘ At least one special character")
        
        requirements_layout.addWidget(self.req_length)
        requirements_layout.addWidget(self.req_upper)
        requirements_layout.addWidget(self.req_lower)
        requirements_layout.addWidget(self.req_digit)
        requirements_layout.addWidget(self.req_special)
        
        layout.addWidget(requirements_group)
        
        # Add generate password button
        generate_btn = QPushButton("Generate Strong Password")
        generate_btn.clicked.connect(self.generate_password)
        layout.addWidget(generate_btn)
        
        # Button box
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.validate_and_accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
        # Connect password field to strength checker
        self.password.textChanged.connect(self.check_password_strength)
    
    def check_password_strength(self):
        """Check password strength and update indicator"""
        password = self.password.text()
        
        # Initialize score and check requirements
        score = 0
        
        # Check length
        if len(password) >= 8:
            score += 20
            self.req_length.setText("✓ At least 8 characters")
        else:
            self.req_length.setText("✘ At least 8 characters")
        
        # Check for uppercase
        if any(c.isupper() for c in password):
            score += 20
            self.req_upper.setText("✓ At least one uppercase letter")
        else:
            self.req_upper.setText("✘ At least one uppercase letter")
        
        # Check for lowercase
        if any(c.islower() for c in password):
            score += 20
            self.req_lower.setText("✓ At least one lowercase letter")
        else:
            self.req_lower.setText("✘ At least one lowercase letter")
        
        # Check for digits
        if any(c.isdigit() for c in password):
            score += 20
            self.req_digit.setText("✓ At least one digit")
        else:
            self.req_digit.setText("✘ At least one digit")
        
        # Check for special characters
        if any(not c.isalnum() for c in password):
            score += 20
            self.req_special.setText("✓ At least one special character")
        else:
            self.req_special.setText("✘ At least one special character")
        
        # Update strength indicator
        self.strength_indicator.setValue(score)
        
        # Set color based on score
        if score < 40:
            self.strength_indicator.setStyleSheet("QProgressBar::chunk { background-color: #F44336; }")
            self.strength_text.setText("Very Weak")
        elif score < 60:
            self.strength_indicator.setStyleSheet("QProgressBar::chunk { background-color: #FFC107; }")
            self.strength_text.setText("Weak")
        elif score < 80:
            self.strength_indicator.setStyleSheet("QProgressBar::chunk { background-color: #4CAF50; }")
            self.strength_text.setText("Good")
        else:
            self.strength_indicator.setStyleSheet("QProgressBar::chunk { background-color: #2196F3; }")
            self.strength_text.setText("Strong")
    
    def generate_password(self):
        """Generate a strong random password"""
        import random
        import string
        
        # Define character sets
        uppercase = string.ascii_uppercase
        lowercase = string.ascii_lowercase
        digits = string.digits
        special = "!@#$%^&*()-_=+[]{}|;:,.<>?"
        
        # Generate password with at least one of each character type
        password = []
        password.append(random.choice(uppercase))
        password.append(random.choice(lowercase))
        password.append(random.choice(digits))
        password.append(random.choice(special))
        
        # Add remaining characters (total length 12)
        all_chars = uppercase + lowercase + digits + special
        password.extend(random.choice(all_chars) for _ in range(8))
        
        # Shuffle the characters
        random.shuffle(password)
        password = ''.join(password)
        
        # Set the password
        self.password.setText(password)
        self.confirm_password.setText(password)
    
    def validate_and_accept(self):
        """Validate the form and accept if valid"""
        password = self.password.text()
        confirm_password = self.confirm_password.text()
        
        # Validate password
        if not password:
            QMessageBox.warning(self, "Validation Error", "Password is required")
            return
        
        if password != confirm_password:
            QMessageBox.warning(self, "Validation Error", "Passwords do not match")
            return
        
        if len(password) < 8:
            QMessageBox.warning(self, "Validation Error", "Password must be at least 8 characters long")
            return
        
        # Accept the dialog
        self.accept()
    
    def get_password(self):
        """Get the password from the form"""
        return self.password.text()


class TableDataDialog(QDialog):
    """Dialog for viewing table data"""
    
    def __init__(self, parent, db_manager, table_name):
        super().__init__(parent)
        
        self.db_manager = db_manager
        self.table_name = table_name
        
        self.setWindowTitle(f"Table Data: {table_name}")
        self.resize(800, 600)
        
        # Create layout
        layout = QVBoxLayout(self)
        
        # Search and filter controls
        filter_layout = QHBoxLayout()
        
        search_label = QLabel("Search:")
        self.search_field = QLineEdit()
        self.search_field.setPlaceholderText("Enter search term")
        self.search_field.returnPressed.connect(self.apply_filter)
        
        column_label = QLabel("Column:")
        self.column_combo = QComboBox()
        self.column_combo.addItem("All Columns")
        
        self.limit_spin = QSpinBox()
        self.limit_spin.setRange(10, 1000)
        self.limit_spin.setValue(100)
        self.limit_spin.setSuffix(" rows")
        
        filter_btn = QPushButton("Apply Filter")
        filter_btn.clicked.connect(self.apply_filter)
        
        reset_btn = QPushButton("Reset")
        reset_btn.clicked.connect(self.reset_filter)
        
        filter_layout.addWidget(search_label)
        filter_layout.addWidget(self.search_field)
        filter_layout.addWidget(column_label)
        filter_layout.addWidget(self.column_combo)
        filter_layout.addWidget(self.limit_spin)
        filter_layout.addWidget(filter_btn)
        filter_layout.addWidget(reset_btn)
        
        layout.addLayout(filter_layout)
        
        # Create table widget
        self.table_widget = QTableWidget()
        layout.addWidget(self.table_widget)
        
        # Statistics
        stats_layout = QHBoxLayout()
        self.stats_label = QLabel("Showing 0 of 0 rows")
        export_btn = QPushButton("Export to CSV")
        export_btn.clicked.connect(self.export_data)
        
        stats_layout.addWidget(self.stats_label)
        stats_layout.addStretch()
        stats_layout.addWidget(export_btn)
        
        layout.addLayout(stats_layout)
        
        # Close button
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)
        
        # Load data
        self.load_data()
    
    def load_data(self):
        """Load data from the table"""
        try:
            # Get table structure (for column names)
            table_info = self.db_manager.get_table_info(self.table_name)
            columns = [col['name'] for col in table_info.get('columns', [])]
            
            # Populate column combo
            self.column_combo.clear()
            self.column_combo.addItem("All Columns")
            self.column_combo.addItems(columns)
            
            # Get data
            limit = self.limit_spin.value()
            search = self.search_field.text()
            column = self.column_combo.currentText()
            if column == "All Columns":
                column = None
            
            data = self.db_manager.get_table_data(
                self.table_name, limit=limit, search=search, column=column)
            
            # Set up table
            self.table_widget.setRowCount(len(data))
            self.table_widget.setColumnCount(len(columns))
            self.table_widget.setHorizontalHeaderLabels(columns)
            
            # Populate table
            for i, row in enumerate(data):
                for j, col in enumerate(columns):
                    value = row.get(col, "")
                    # Convert value to string (handle JSON, datetime, etc.)
                    if value is None:
                        value = ""
                    elif isinstance(value, (dict, list)):
                        import json
                        value = json.dumps(value, indent=2)
                    else:
                        value = str(value)
                    
                    item = QTableWidgetItem(value)
                    self.table_widget.setItem(i, j, item)
            
            # Auto-adjust column widths
            self.table_widget.resizeColumnsToContents()
            
            # Update statistics
            total_rows = table_info.get('rows', 0)
            self.stats_label.setText(f"Showing {len(data)} of {total_rows} rows")
            
        except Exception as e:
            print(f"Error loading table data: {e}")
            QMessageBox.critical(self, "Error", f"Error loading data: {e}")
    
    def apply_filter(self):
        """Apply search and filter"""
        self.load_data()
    
    def reset_filter(self):
        """Reset search and filter"""
        self.search_field.clear()
        self.column_combo.setCurrentIndex(0)
        self.limit_spin.setValue(100)
        self.load_data()
    
    def export_data(self):
        """Export table data to CSV"""
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export Table Data",
            f"{self.table_name}.csv",
            "CSV Files (*.csv)"
        )
        
        if not file_path:
            return
        
        try:
            # Get data
            limit = 0  # No limit for export
            search = self.search_field.text()
            column = self.column_combo.currentText()
            if column == "All Columns":
                column = None
            
            # Export data
            success = self.db_manager.export_table_data(
                self.table_name, file_path, 
                search=search, column=column, limit=limit
            )
            
            if success:
                QMessageBox.information(
                    self,
                    "Export Successful",
                    f"Table data exported to {file_path}"
                )
            else:
                QMessageBox.warning(
                    self,
                    "Export Failed",
                    "Failed to export table data"
                )
        except Exception as e:
            print(f"Error exporting data: {e}")
            QMessageBox.critical(self, "Error", f"Error exporting data: {e}")


class TableSelectionDialog(QDialog):
    """Dialog for selecting tables to restore"""
    
    @staticmethod
    def get_selected_tables(parent, tables):
        """Static method to get selected tables"""
        dialog = TableSelectionDialog(parent, tables)
        result = dialog.exec()
        return dialog.get_selected_tables(), result == QDialog.Accepted
    
    def __init__(self, parent, tables):
        super().__init__(parent)
        
        self.tables = tables
        
        self.setWindowTitle("Select Tables to Restore")
        self.resize(400, 500)
        
        # Create layout
        layout = QVBoxLayout(self)
        
        # Instructions
        layout.addWidget(QLabel("Select tables to restore:"))
        
        # Create table list with checkboxes
        self.table_list = QTreeWidget()
        self.table_list.setHeaderLabels(["Table Name", "Include"])
        self.table_list.setAlternatingRowColors(True)
        layout.addWidget(self.table_list)
        
        # Add tables to list
        for table in tables:
            item = QTreeWidgetItem(self.table_list)
            item.setText(0, table)
            
            checkbox = QCheckBox()
            checkbox.setChecked(True)
            self.table_list.setItemWidget(item, 1, checkbox)
        
        # Select/deselect all buttons
        button_layout = QHBoxLayout()
        select_all_btn = QPushButton("Select All")
        select_all_btn.clicked.connect(self.select_all)
        deselect_all_btn = QPushButton("Deselect All")
        deselect_all_btn.clicked.connect(self.deselect_all)
        
        button_layout.addWidget(select_all_btn)
        button_layout.addWidget(deselect_all_btn)
        layout.addLayout(button_layout)
        
        # Button box
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.validate_and_accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
    
    def select_all(self):
        """Select all tables"""
        for i in range(self.table_list.topLevelItemCount()):
            item = self.table_list.topLevelItem(i)
            checkbox = self.table_list.itemWidget(item, 1)
            checkbox.setChecked(True)
    
    def deselect_all(self):
        """Deselect all tables"""
        for i in range(self.table_list.topLevelItemCount()):
            item = self.table_list.topLevelItem(i)
            checkbox = self.table_list.itemWidget(item, 1)
            checkbox.setChecked(False)
    
    def validate_and_accept(self):
        """Validate selection and accept"""
        # Ensure at least one table is selected
        selected = False
        for i in range(self.table_list.topLevelItemCount()):
            item = self.table_list.topLevelItem(i)
            checkbox = self.table_list.itemWidget(item, 1)
            if checkbox.isChecked():
                selected = True
                break
        
        if not selected:
            QMessageBox.warning(
                self,
                "Selection Error",
                "Please select at least one table to restore"
            )
            return
        
        self.accept()
    
    def get_selected_tables(self):
        """Get list of selected tables"""
        selected_tables = []
        for i in range(self.table_list.topLevelItemCount()):
            item = self.table_list.topLevelItem(i)
            checkbox = self.table_list.itemWidget(item, 1)
            if checkbox.isChecked():
                selected_tables.append(item.text(0))
        
        return selected_tables


class BackupScheduleDialog(QDialog):
    """Dialog for scheduling automatic backups"""
    
    def __init__(self, parent, db_manager):
        super().__init__(parent)
        
        self.db_manager = db_manager
        
        self.setWindowTitle("Schedule Automatic Backups")
        self.resize(500, 400)
        
        # Create layout
        layout = QVBoxLayout(self)
        
        # Schedule settings
        schedule_group = QGroupBox("Backup Schedule")
        schedule_layout = QFormLayout(schedule_group)
        
        self.enable_auto = QCheckBox("Enable automatic backups")
        schedule_layout.addRow("", self.enable_auto)
        
        self.frequency = QComboBox()
        self.frequency.addItems(["Daily", "Weekly", "Monthly"])
        schedule_layout.addRow("Frequency:", self.frequency)
        
        self.time = QTimeEdit()
        self.time.setTime(QTime(1, 0))  # Default to 1:00 AM
        self.time.setDisplayFormat("HH:mm")
        schedule_layout.addRow("Time:", self.time)
        
        self.day_of_week = QComboBox()
        self.day_of_week.addItems([
            "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"
        ])
        schedule_layout.addRow("Day of week:", self.day_of_week)
        
        self.day_of_month = QSpinBox()
        self.day_of_month.setRange(1, 28)
        self.day_of_month.setValue(1)
        schedule_layout.addRow("Day of month:", self.day_of_month)
        
        layout.addWidget(schedule_group)
        
        # Backup options
        options_group = QGroupBox("Backup Options")
        options_layout = QFormLayout(options_group)
        
        self.backup_location = QLineEdit()
        self.backup_location.setText(os.path.join(os.path.dirname(os.path.abspath(__file__)), "backups"))
        backup_path_layout = QHBoxLayout()
        backup_path_layout.addWidget(self.backup_location)
        browse_btn = QPushButton("Browse")
        browse_btn.clicked.connect(self.browse_backup_path)
        backup_path_layout.addWidget(browse_btn)
        options_layout.addRow("Backup Location:", backup_path_layout)
        
        self.compression_level = QComboBox()
        self.compression_level.addItems(["None", "Low", "Medium", "High"])
        self.compression_level.setCurrentIndex(2)  # Default to Medium
        options_layout.addRow("Compression:", self.compression_level)
        
        self.include_attachments = QCheckBox("Include equipment attachments")
        self.include_attachments.setChecked(True)
        options_layout.addRow("", self.include_attachments)
        
        self.keep_backups = QSpinBox()
        self.keep_backups.setRange(1, 100)
        self.keep_backups.setValue(10)
        self.keep_backups.setSuffix(" backups")
        options_layout.addRow("Keep last:", self.keep_backups)
        
        layout.addWidget(options_group)
        
        # Notification options
        notification_group = QGroupBox("Notifications")
        notification_layout = QFormLayout(notification_group)
        
        self.notify_on_success = QCheckBox("Notify on successful backup")
        self.notify_on_success.setChecked(True)
        notification_layout.addRow("", self.notify_on_success)
        
        self.notify_on_failure = QCheckBox("Notify on backup failure")
        self.notify_on_failure.setChecked(True)
        notification_layout.addRow("", self.notify_on_failure)
        
        self.notification_email = QLineEdit()
        notification_layout.addRow("Email address:", self.notification_email)
        
        layout.addWidget(notification_group)
        
        # Button box
        button_box = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
        # Connect signals
        self.frequency.currentIndexChanged.connect(self.update_ui)
        
        # Load existing schedule
        self.load_schedule()
        
        # Update UI
        self.update_ui()
    
    def update_ui(self):
        """Update UI based on frequency selection"""
        frequency = self.frequency.currentText()
        
        # Show/hide day selectors
        if frequency == "Weekly":
            self.day_of_week.setEnabled(True)
            self.day_of_month.setEnabled(False)
        elif frequency == "Monthly":
            self.day_of_week.setEnabled(False)
            self.day_of_month.setEnabled(True)
        else:  # Daily
            self.day_of_week.setEnabled(False)
            self.day_of_month.setEnabled(False)
    
    def browse_backup_path(self):
        """Open file dialog to select backup location"""
        directory = QFileDialog.getExistingDirectory(
            self,
            "Select Backup Location",
            self.backup_location.text(),
            QFileDialog.ShowDirsOnly
        )
        
        if directory:
            self.backup_location.setText(directory)
    
    def load_schedule(self):
        """Load existing backup schedule"""
        try:
            schedule = self.db_manager.get_backup_schedule()
            
            if schedule:
                self.enable_auto.setChecked(schedule.get('enabled', False))
                
                frequency = schedule.get('frequency', 'Weekly')
                index = self.frequency.findText(frequency)
                if index >= 0:
                    self.frequency.setCurrentIndex(index)
                
                time_str = schedule.get('time', '01:00')
                time = QTime.fromString(time_str, "HH:mm")
                if time.isValid():
                    self.time.setTime(time)
                
                day_of_week = schedule.get('day_of_week', 'Monday')
                index = self.day_of_week.findText(day_of_week)
                if index >= 0:
                    self.day_of_week.setCurrentIndex(index)
                
                self.day_of_month.setValue(schedule.get('day_of_month', 1))
                
                self.backup_location.setText(schedule.get('backup_location', self.backup_location.text()))
                
                compression = schedule.get('compression', 'Medium')
                index = self.compression_level.findText(compression)
                if index >= 0:
                    self.compression_level.setCurrentIndex(index)
                
                self.include_attachments.setChecked(schedule.get('include_attachments', True))
                self.keep_backups.setValue(schedule.get('keep_backups', 10))
                
                self.notify_on_success.setChecked(schedule.get('notify_on_success', True))
                self.notify_on_failure.setChecked(schedule.get('notify_on_failure', True))
                self.notification_email.setText(schedule.get('notification_email', ''))
        except Exception as e:
            print(f"Error loading backup schedule: {e}")

    def get_schedule_settings(self):
        """Get backup schedule settings"""
        return {
            'enabled': self.enable_auto.isChecked(),
            'frequency': self.frequency.currentText(),
            'time': self.time.time().toString("HH:mm"),
            'day_of_week': self.day_of_week.currentText(),
            'day_of_month': self.day_of_month.value(),
            'backup_location': self.backup_location.text(),
            'compression': self.compression_level.currentText(),
            'include_attachments': self.include_attachments.isChecked(),
            'keep_backups': self.keep_backups.value(),
            'notify_on_success': self.notify_on_success.isChecked(),
            'notify_on_failure': self.notify_on_failure.isChecked(),
            'notification_email': self.notification_email.text()
        }
