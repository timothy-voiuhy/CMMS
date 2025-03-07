from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                              QPushButton, QLabel, QTabWidget, QLineEdit,
                              QComboBox, QDateEdit, QTableWidget, QTableWidgetItem,
                              QDialog, QFormLayout, QMessageBox, QScrollArea,
                              QSplitter, QTextEdit, QMenuBar, QMenu, QSizePolicy,
                              QTimeEdit, QCalendarWidget, QStackedWidget, QGridLayout,
                              QCheckBox, QSpinBox, QToolButton, QFrame, QListWidget,
                              QListWidgetItem, QProgressBar, QFileDialog, QProgressDialog,
                              QInputDialog)
from PySide6.QtCore import Qt, Signal, QDate, QTime, QDateTime, QSize, QTimer, QRect
from PySide6.QtGui import QColor, QPainter, QFont, QIcon, QPixmap, QPalette, QBrush
from datetime import datetime, timedelta
import json
import os

from .work_order_dialog import WorkOrderDialog
from .report_dialog import CustomReportDialog
from .calendar_widgets import MonthCalendarView, WeekCalendarView, DayCalendarView
from ui.card_table_widget import CardTableWidget
from config import WORK_ORDER_SETTINGS_FILE

class WorkOrdersWindow(QMainWindow):
    def __init__(self, db_manager, parent=None):
        super().__init__(parent)
        self.db_manager = db_manager
        self.setWindowTitle("Work Orders Management")
        
        # Create central widget and layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)
        
        # Create tab widget
        self.tab_widget = QTabWidget()
        self.main_layout.addWidget(self.tab_widget)
        
        # Setup tabs
        self.setup_dashboard_tab()
        self.setup_work_orders_tab()
        self.setup_calendar_tab()
        self.setup_reports_tab()
        self.setup_settings_tab()
        
        # Setup menu bar
        self.setup_menu_bar()
        
        # Load settings
        self.load_settings()
        
        # Initialize timer for auto-refresh
        self.refresh_timer = QTimer(self)
        self.refresh_timer.timeout.connect(self.refresh_data)
        self.refresh_timer.start(60000)  # Refresh every minute
        
        # Load initial data
        self.refresh_data()

    def setup_dashboard_tab(self):
        """Setup the dashboard tab with overview and statistics"""
        dashboard_widget = QWidget()
        layout = QVBoxLayout(dashboard_widget)
        
        # Create scroll area for dashboard content
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        
        # Create content widget for scroll area
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(15, 15, 15, 15)
        content_layout.setSpacing(15)
        
        # Header
        header = QLabel("Work Orders Dashboard")
        header.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        content_layout.addWidget(header)
        
        # Statistics section
        stats_container = QWidget()
        stats_layout = QGridLayout(stats_container)
        
        # Create stat boxes
        self.total_wo_label = self.create_stat_box("Total Work Orders", "0")
        self.open_wo_label = self.create_stat_box("Open Work Orders", "0", "#2196F3")
        self.overdue_wo_label = self.create_stat_box("Overdue", "0", "#F44336")
        self.completed_wo_label = self.create_stat_box("Completed", "0", "#4CAF50")
        
        # Add stat boxes to grid
        stats_layout.addWidget(self.total_wo_label, 0, 0)
        stats_layout.addWidget(self.open_wo_label, 0, 1)
        stats_layout.addWidget(self.overdue_wo_label, 1, 0)
        stats_layout.addWidget(self.completed_wo_label, 1, 1)
        
        content_layout.addWidget(stats_container)
        
        # Recent work orders section
        recent_label = QLabel("Recent Work Orders")
        recent_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        content_layout.addWidget(recent_label)
        
        self.recent_wo_table = QTableWidget()
        self.recent_wo_table.setColumnCount(5)
        self.recent_wo_table.setHorizontalHeaderLabels([
            "ID", "Title", "Equipment", "Assigned To", "Status"
        ])
        
        # Set column widths
        self.recent_wo_table.setColumnWidth(0, 80)   # ID
        self.recent_wo_table.setColumnWidth(1, 200)  # Title
        self.recent_wo_table.setColumnWidth(2, 150)  # Equipment
        self.recent_wo_table.setColumnWidth(3, 150)  # Assigned To
        self.recent_wo_table.setColumnWidth(4, 100)  # Status
        
        # Make table stretch to fill available space
        self.recent_wo_table.horizontalHeader().setStretchLastSection(True)
        self.recent_wo_table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        content_layout.addWidget(self.recent_wo_table)
        
        # Upcoming maintenance section
        upcoming_label = QLabel("Upcoming Scheduled Maintenance")
        upcoming_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        content_layout.addWidget(upcoming_label)
        
        self.upcoming_maintenance_table = QTableWidget()
        self.upcoming_maintenance_table.setColumnCount(4)
        self.upcoming_maintenance_table.setHorizontalHeaderLabels([
            "Equipment", "Task", "Due Date", "Priority"
        ])
        
        # Set column widths
        self.upcoming_maintenance_table.setColumnWidth(0, 150)  # Equipment
        self.upcoming_maintenance_table.setColumnWidth(1, 200)  # Task
        self.upcoming_maintenance_table.setColumnWidth(2, 100)  # Due Date
        self.upcoming_maintenance_table.setColumnWidth(3, 80)   # Priority
        
        # Make table stretch to fill available space
        self.upcoming_maintenance_table.horizontalHeader().setStretchLastSection(True)
        self.upcoming_maintenance_table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        content_layout.addWidget(self.upcoming_maintenance_table)
        
        # Add refresh button
        refresh_btn = QPushButton("Refresh Dashboard")
        refresh_btn.clicked.connect(self.refresh_data)
        content_layout.addWidget(refresh_btn)
        
        # Set the content widget as the scroll area's widget
        scroll.setWidget(content_widget)
        
        # Add scroll area to main layout
        layout.addWidget(scroll)
        
        self.tab_widget.addTab(dashboard_widget, "Dashboard")

    def create_stat_box(self, title, value, color="#607D8B"):
        """Create a styled statistics box"""
        box = QFrame()
        box.setFrameShape(QFrame.Shape.StyledPanel)
        box.setStyleSheet(f"""
            QFrame {{
                background-color: {color};
                border-radius: 8px;
                padding: 10px;
                color: white;
            }}
        """)
        
        layout = QVBoxLayout(box)
        
        title_label = QLabel(title)
        title_label.setFont(QFont("Arial", 12))
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        value_label = QLabel(value)
        value_label.setFont(QFont("Arial", 24, QFont.Weight.Bold))
        value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        layout.addWidget(title_label)
        layout.addWidget(value_label)
        
        return box

    def setup_work_orders_tab(self):
        """Setup the work orders tab with list and management features"""
        work_orders_widget = QWidget()
        layout = QVBoxLayout(work_orders_widget)
        
        # Create search and filter section
        filter_container = QWidget()
        filter_layout = QHBoxLayout(filter_container)
        
        self.wo_search = QLineEdit()
        self.wo_search.setPlaceholderText("Search work orders...")
        self.wo_search.textChanged.connect(self.filter_work_orders)
        
        self.wo_status_filter = QComboBox()
        self.wo_status_filter.addItems(["All Statuses", "Open", "In Progress", "On Hold", "Completed", "Cancelled"])
        self.wo_status_filter.currentTextChanged.connect(self.filter_work_orders)
        
        self.wo_priority_filter = QComboBox()
        self.wo_priority_filter.addItems(["All Priorities", "Low", "Medium", "High", "Critical"])
        self.wo_priority_filter.currentTextChanged.connect(self.filter_work_orders)
        
        self.wo_assignment_filter = QComboBox()
        self.wo_assignment_filter.addItems(["All Assignments", "Individual", "Team"])
        self.wo_assignment_filter.currentTextChanged.connect(self.filter_work_orders)
        
        self.wo_date_filter = QComboBox()
        self.wo_date_filter.addItems(["All Dates", "Today", "This Week", "This Month", "Overdue"])
        self.wo_date_filter.currentTextChanged.connect(self.filter_work_orders)
        
        filter_layout.addWidget(QLabel("Search:"))
        filter_layout.addWidget(self.wo_search, 3)
        filter_layout.addWidget(QLabel("Status:"))
        filter_layout.addWidget(self.wo_status_filter, 1)
        filter_layout.addWidget(QLabel("Priority:"))
        filter_layout.addWidget(self.wo_priority_filter, 1)
        filter_layout.addWidget(QLabel("Assignment:"))
        filter_layout.addWidget(self.wo_assignment_filter, 1)
        filter_layout.addWidget(QLabel("Date:"))
        filter_layout.addWidget(self.wo_date_filter, 1)
        
        layout.addWidget(filter_container)
        
        # Create card table widget for work orders
        self.work_orders_cards = CardTableWidget()
        
        # Define display fields
        display_fields = [
            {'field': 'title', 'display': 'Title'},
            {'field': 'equipment_name', 'display': 'Equipment'},
            {'field': 'assigned_to', 'display': 'Assigned To'},
            {'field': 'due_date', 'display': 'Due Date', 'type': 'date'},
            {'field': 'status', 'display': 'Status', 'type': 'status', 
             'colors': {
                 'Open': '#2196F3',  # Blue
                 'In Progress': '#FF9800',  # Orange
                 'On Hold': '#9C27B0',  # Purple
                 'Completed': '#4CAF50',  # Green
                 'Cancelled': '#9E9E9E',  # Grey
                 'Overdue': '#F44336'  # Red
             }},
            {'field': 'priority', 'display': 'Priority', 'type': 'priority',
             'colors': {
                 'Low': '#8BC34A',  # Light Green
                 'Medium': '#FFC107',  # Amber
                 'High': '#FF5722',  # Deep Orange
                 'Critical': '#F44336'  # Red
             }}
        ]
        self.work_orders_cards.set_display_fields(display_fields)
        
        # Connect signals
        self.work_orders_cards.itemClicked.connect(self.handle_work_order_click)
        self.work_orders_cards.itemEditClicked.connect(self.edit_work_order)
        self.work_orders_cards.itemContextMenuRequested.connect(self.show_work_order_context_menu)
        
        layout.addWidget(self.work_orders_cards)
        
        # Create hidden table for compatibility
        self.work_orders_table = QTableWidget()
        self.work_orders_table.setColumnCount(9)
        self.work_orders_table.setHorizontalHeaderLabels([
            "ID", "Title", "Equipment", "Assignment Type", "Assigned To", "Due Date", 
            "Status", "Priority", "Created Date"
        ])
        self.work_orders_table.hide()
        layout.addWidget(self.work_orders_table)
        
        # Action buttons
        buttons_container = QWidget()
        buttons_layout = QHBoxLayout(buttons_container)
        
        create_btn = QPushButton("Create Work Order")
        create_btn.clicked.connect(self.create_work_order)
        
        refresh_btn = QPushButton("Refresh")
        refresh_btn.clicked.connect(self.load_work_orders)
        
        buttons_layout.addWidget(create_btn)
        buttons_layout.addWidget(refresh_btn)
        
        layout.addWidget(buttons_container)
        
        self.tab_widget.addTab(work_orders_widget, "Work Orders")

    def setup_calendar_tab(self):
        """Setup the calendar tab with custom calendar view"""
        calendar_widget = QWidget()
        layout = QVBoxLayout(calendar_widget)
        
        # Create scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        
        # Create content widget for scroll area
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(15, 15, 15, 15)
        content_layout.setSpacing(15)
        
        # Calendar view controls
        controls_container = QWidget()
        controls_layout = QHBoxLayout(controls_container)
        
        self.calendar_view_type = QComboBox()
        self.calendar_view_type.addItems(["Month View", "Week View", "Day View"])
        self.calendar_view_type.currentTextChanged.connect(self.change_calendar_view)
        
        prev_btn = QPushButton("Previous")
        prev_btn.clicked.connect(self.previous_calendar_period)
        
        next_btn = QPushButton("Next")
        next_btn.clicked.connect(self.next_calendar_period)
        
        today_btn = QPushButton("Today")
        today_btn.clicked.connect(self.go_to_today)
        
        self.calendar_title = QLabel("Calendar")
        self.calendar_title.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        self.calendar_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        controls_layout.addWidget(self.calendar_view_type)
        controls_layout.addWidget(prev_btn)
        controls_layout.addWidget(today_btn)
        controls_layout.addWidget(next_btn)
        controls_layout.addStretch()
        controls_layout.addWidget(self.calendar_title)
        controls_layout.addStretch()
        
        content_layout.addWidget(controls_container)
        
        # Calendar view stacked widget
        self.calendar_stack = QStackedWidget()
        
        # Create different calendar views
        self.month_view = MonthCalendarView(self.db_manager)
        self.week_view = WeekCalendarView(self.db_manager)
        self.day_view = DayCalendarView(self.db_manager)
        
        # Connect signals
        self.month_view.date_clicked.connect(self.handle_calendar_date_clicked)
        self.week_view.date_clicked.connect(self.handle_calendar_date_clicked)
        self.day_view.date_clicked.connect(self.handle_calendar_date_clicked)
        
        self.month_view.work_order_clicked.connect(self.view_work_order_from_calendar)
        self.week_view.work_order_clicked.connect(self.view_work_order_from_calendar)
        self.day_view.work_order_clicked.connect(self.view_work_order_from_calendar)
        
        # Add views to stack
        self.calendar_stack.addWidget(self.month_view)
        self.calendar_stack.addWidget(self.week_view)
        self.calendar_stack.addWidget(self.day_view)
        
        content_layout.addWidget(self.calendar_stack, 1)  # Give it a stretch factor
        
        # Legend section
        legend_container = QWidget()
        legend_layout = QHBoxLayout(legend_container)
        
        # Create legend items
        legend_items = [
            ("Open", "#2196F3"),
            ("In Progress", "#FF9800"),
            ("On Hold", "#9C27B0"),
            ("Completed", "#4CAF50"),
            ("Overdue", "#F44336"),
            ("Preventive Maintenance", "#607D8B")
        ]
        
        for label, color in legend_items:
            item_widget = QWidget()
            item_layout = QHBoxLayout(item_widget)
            item_layout.setContentsMargins(0, 0, 0, 0)
            
            color_box = QFrame()
            color_box.setFixedSize(16, 16)
            color_box.setStyleSheet(f"background-color: {color}; border: 1px solid #333;")
            
            item_layout.addWidget(color_box)
            item_layout.addWidget(QLabel(label))
            
            legend_layout.addWidget(item_widget)
        
        legend_layout.addStretch()
        
        content_layout.addWidget(legend_container)
        
        # Set the content widget as the scroll area's widget
        scroll.setWidget(content_widget)
        
        # Add scroll area to main layout
        layout.addWidget(scroll)
        
        self.tab_widget.addTab(calendar_widget, "Calendar")
        
        # Initialize with month view
        self.calendar_view_type.setCurrentIndex(0)
        self.change_calendar_view("Month View")

    def setup_reports_tab(self):
        """Setup the reports tab with various report options"""
        reports_widget = QWidget()
        layout = QVBoxLayout(reports_widget)
        
        # Create scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        
        # Create content widget
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(15, 15, 15, 15)
        content_layout.setSpacing(15)
        
        # Header
        header = QLabel("Work Order Reports")
        header.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        content_layout.addWidget(header)
        
        # Report types section
        reports_label = QLabel("Available Reports")
        reports_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        content_layout.addWidget(reports_label)
        
        # Create report buttons grid
        reports_grid = QGridLayout()
        reports_grid.setSpacing(10)
        
        # Add report buttons
        summary_btn = self.create_report_button(
            "Work Order Summary",
            "Summary of all work orders with status and completion statistics",
            self.generate_summary_report
        )
        
        completion_btn = self.create_report_button(
            "Completion Time Analysis",
            "Analysis of work order completion times and efficiency",
            self.generate_completion_report
        )
        
        craftsmen_btn = self.create_report_button(
            "Craftsmen Performance",
            "Performance metrics for craftsmen handling work orders",
            self.generate_craftsmen_report
        )
        
        equipment_btn = self.create_report_button(
            "Equipment Maintenance",
            "Maintenance history for specific equipment",
            self.generate_equipment_report
        )
        
        cost_btn = self.create_report_button(
            "Cost Analysis",
            "Analysis of maintenance costs by equipment and category",
            self.generate_cost_report
        )
        
        custom_btn = self.create_report_button(
            "Custom Report",
            "Create a custom report with selected fields and filters",
            self.generate_custom_report
        )
        
        # Add buttons to grid
        reports_grid.addWidget(summary_btn, 0, 0)
        reports_grid.addWidget(completion_btn, 0, 1)
        reports_grid.addWidget(craftsmen_btn, 1, 0)
        reports_grid.addWidget(equipment_btn, 1, 1)
        reports_grid.addWidget(cost_btn, 2, 0)
        reports_grid.addWidget(custom_btn, 2, 1)
        
        content_layout.addLayout(reports_grid)
        
        # Report parameters section
        params_label = QLabel("Report Parameters")
        params_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        content_layout.addWidget(params_label)
        
        # Create parameters form
        params_container = QWidget()
        params_layout = QFormLayout(params_container)
        
        self.report_date_from = QDateEdit()
        self.report_date_from.setCalendarPopup(True)
        self.report_date_from.setDate(QDate.currentDate().addMonths(-1))
        
        self.report_date_to = QDateEdit()
        self.report_date_to.setCalendarPopup(True)
        self.report_date_to.setDate(QDate.currentDate())
        
        self.report_status_filter = QComboBox()
        self.report_status_filter.addItems(["All Statuses", "Open", "In Progress", "On Hold", "Completed", "Cancelled"])
        
        self.report_format = QComboBox()
        self.report_format.addItems(["PDF", "CSV", "Excel"])
        
        params_layout.addRow("Date From:", self.report_date_from)
        params_layout.addRow("Date To:", self.report_date_to)
        params_layout.addRow("Status:", self.report_status_filter)
        params_layout.addRow("Format:", self.report_format)
        
        content_layout.addWidget(params_container)
        
        # Recent reports section
        recent_label = QLabel("Recent Reports")
        recent_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        content_layout.addWidget(recent_label)
        
        self.recent_reports_list = QListWidget()
        self.recent_reports_list.setMaximumHeight(200)  # Limit height
        content_layout.addWidget(self.recent_reports_list)
        
        # Set the content widget as the scroll area's widget
        scroll.setWidget(content_widget)
        
        # Add scroll area to main layout
        layout.addWidget(scroll)
        
        self.tab_widget.addTab(reports_widget, "Reports")

    def create_report_button(self, title, description, callback):
        """Create a styled report button"""
        button = QPushButton()
        button.setMinimumHeight(100)
        button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        
        # Create layout for button content
        content_layout = QVBoxLayout(button)
        
        title_label = QLabel(title)
        title_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        desc_label = QLabel(description)
        desc_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        desc_label.setWordWrap(True)
        
        content_layout.addWidget(title_label)
        content_layout.addWidget(desc_label)
        
        button.clicked.connect(callback)
        
        return button

    def setup_settings_tab(self):
        """Setup the settings tab for work order configuration"""
        settings_widget = QWidget()
        layout = QVBoxLayout(settings_widget)
        
        # Create scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        
        # Create content widget
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(15, 15, 15, 15)
        content_layout.setSpacing(15)
        
        # Header
        header = QLabel("Work Order Settings")
        header.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        content_layout.addWidget(header)
        
        # Create form for settings
        form_layout = QFormLayout()
        form_layout.setVerticalSpacing(10)
        
        # Notification settings section
        notif_label = QLabel("Notification Settings")
        notif_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        content_layout.addWidget(notif_label)
        
        self.notify_on_new = QCheckBox("Notify on new work orders")
        self.notify_on_new.setChecked(True)
        
        self.notify_on_update = QCheckBox("Notify on work order updates")
        self.notify_on_update.setChecked(True)
        
        self.notify_on_due = QCheckBox("Notify on approaching due dates")
        self.notify_on_due.setChecked(True)
        
        self.due_date_days = QSpinBox()
        self.due_date_days.setRange(1, 14)
        self.due_date_days.setValue(3)
        
        form_layout.addRow("", self.notify_on_new)
        form_layout.addRow("", self.notify_on_update)
        form_layout.addRow("", self.notify_on_due)
        form_layout.addRow("Days before due date:", self.due_date_days)
        
        # Assignment settings section
        assign_label = QLabel("Assignment Settings")
        assign_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        content_layout.addWidget(assign_label)
        content_layout.addLayout(form_layout)
        
        form_layout2 = QFormLayout()
        form_layout2.setVerticalSpacing(10)
        
        self.auto_assign = QCheckBox("Enable automatic assignment")
        self.auto_assign.setChecked(False)
        
        self.assignment_method = QComboBox()
        self.assignment_method.addItems([
            "Based on workload", 
            "Based on skills", 
            "Round-robin", 
            "Based on equipment history"
        ])
        
        # Default values
        self.default_priority = QComboBox()
        self.default_priority.addItems(["Low", "Medium", "High", "Critical"])
        self.default_priority.setCurrentText("Medium")
        
        form_layout2.addRow("", self.auto_assign)
        form_layout2.addRow("Assignment method:", self.assignment_method)
        form_layout2.addRow("Default priority:", self.default_priority)
        
        content_layout.addLayout(form_layout2)
        
        # Email notification settings
        email_label = QLabel("Email Notification Settings")
        email_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        content_layout.addWidget(email_label)
        
        form_layout3 = QFormLayout()
        form_layout3.setVerticalSpacing(10)
        
        self.email_notifications = QCheckBox("Enable email notifications")
        self.email_notifications.setChecked(False)
        
        self.email_server = QLineEdit()
        self.email_server.setPlaceholderText("SMTP Server")
        
        self.email_port = QLineEdit()
        self.email_port.setPlaceholderText("Port")
        
        self.email_username = QLineEdit()
        self.email_username.setPlaceholderText("Username")
        
        self.email_password = QLineEdit()
        self.email_password.setPlaceholderText("Password")
        self.email_password.setEchoMode(QLineEdit.EchoMode.Password)
        
        form_layout3.addRow("", self.email_notifications)
        form_layout3.addRow("SMTP Server:", self.email_server)
        form_layout3.addRow("Port:", self.email_port)
        form_layout3.addRow("Username:", self.email_username)
        form_layout3.addRow("Password:", self.email_password)
        
        content_layout.addLayout(form_layout3)
        
        # Add test email button
        test_email_btn = QPushButton("Test Email Settings")
        test_email_btn.clicked.connect(self.test_email_settings)
        content_layout.addWidget(test_email_btn)
        
        # Add save button
        save_btn = QPushButton("Save Settings")
        save_btn.clicked.connect(self.save_settings)
        content_layout.addWidget(save_btn)
        
        # Set the content widget as the scroll area's widget
        scroll.setWidget(content_widget)
        
        # Add scroll area to main layout
        layout.addWidget(scroll)
        
        self.tab_widget.addTab(settings_widget, "Settings")

    def test_email_settings(self):
        """Test email settings by sending a test email"""
        # Get email settings from form
        settings = {
            'enabled': self.email_notifications.isChecked(),
            'server': self.email_server.text(),
            'port': self.email_port.text(),
            'username': self.email_username.text(),
            'password': self.email_password.text(),
            'from_address': self.email_username.text(),
            'use_tls': True
        }
        
        # Validate settings
        if not settings['enabled']:
            QMessageBox.warning(self, "Warning", "Email notifications are not enabled.")
            return
        
        if not settings['server'] or not settings['port'] or not settings['username'] or not settings['password']:
            QMessageBox.warning(self, "Warning", "Please fill in all email settings fields.")
            return
        
        # Ask for test recipient email
        recipient, ok = QInputDialog.getText(
            self, "Test Email", "Enter recipient email address:"
        )
        
        if not ok or not recipient:
            return
        
        try:
            # Save settings temporarily
            self.db_manager.save_email_settings(settings)
            
            # Send test email
            import smtplib
            from email.mime.text import MIMEText
            from email.mime.multipart import MIMEMultipart
            
            # Create message
            msg = MIMEMultipart()
            msg['From'] = settings['from_address']
            msg['To'] = recipient
            msg['Subject'] = "CMMS Test Email"
            
            body = """
            <html>
            <body>
                <h2>CMMS Email Test</h2>
                <p>This is a test email from your CMMS system.</p>
                <p>If you received this email, your email settings are configured correctly.</p>
                <p><b>Congratulations!</b></p>
            </body>
            </html>
            """
            
            msg.attach(MIMEText(body, 'html'))
            
            # Connect to server
            server = smtplib.SMTP(settings['server'], int(settings['port']))
            server.starttls()
            server.login(settings['username'], settings['password'])
            
            # Send email
            server.send_message(msg)
            server.quit()
            
            QMessageBox.information(
                self,
                "Success",
                f"Test email sent successfully to {recipient}!"
            )
            
        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                f"Failed to send test email: {str(e)}"
            )

    def setup_menu_bar(self):
        """Setup the menu bar with various options"""
        menu_bar = self.menuBar()
        
        # Work Orders menu
        wo_menu = menu_bar.addMenu("Work Orders")
        
        create_action = wo_menu.addAction("Create New Work Order")
        create_action.triggered.connect(self.create_work_order)
        
        wo_menu.addSeparator()
        
        import_action = wo_menu.addAction("Import Work Orders")
        import_action.triggered.connect(self.import_work_orders)
        
        export_action = wo_menu.addAction("Export Work Orders")
        export_action.triggered.connect(self.export_work_orders)
        
        # View menu
        view_menu = menu_bar.addMenu("View")
        
        refresh_action = view_menu.addAction("Refresh Data")
        refresh_action.triggered.connect(self.refresh_data)
        
        view_menu.addSeparator()
        
        calendar_submenu = view_menu.addMenu("Calendar View")
        
        month_action = calendar_submenu.addAction("Month View")
        month_action.triggered.connect(lambda: self.change_calendar_view("Month View"))
        
        week_action = calendar_submenu.addAction("Week View")
        week_action.triggered.connect(lambda: self.change_calendar_view("Week View"))
        
        day_action = calendar_submenu.addAction("Day View")
        day_action.triggered.connect(lambda: self.change_calendar_view("Day View"))
        
        # Reports menu
        reports_menu = menu_bar.addMenu("Reports")
        
        summary_action = reports_menu.addAction("Work Order Summary")
        summary_action.triggered.connect(self.generate_summary_report)
        
        completion_action = reports_menu.addAction("Completion Time Analysis")
        completion_action.triggered.connect(self.generate_completion_report)
        
        craftsmen_action = reports_menu.addAction("Craftsmen Performance")
        craftsmen_action.triggered.connect(self.generate_craftsmen_report)
        
        equipment_action = reports_menu.addAction("Equipment Maintenance History")
        equipment_action.triggered.connect(self.generate_equipment_report)
        
        cost_action = reports_menu.addAction("Cost Analysis")
        cost_action.triggered.connect(self.generate_cost_report)
        
        reports_menu.addSeparator()
        
        custom_action = reports_menu.addAction("Custom Report")
        custom_action.triggered.connect(self.generate_custom_report)

    def refresh_data(self):
        """Refresh all data in the window"""
        self.load_dashboard_data()
        self.load_work_orders()
        self.refresh_calendar_views()
        self.load_recent_reports()

    def load_dashboard_data(self):
        """Load data for the dashboard tab"""
        # Get work order statistics
        stats = self.db_manager.get_work_order_statistics()
        
        # Update stat boxes
        if stats:
            # Find the value labels within each stat box
            for box, key in [
                (self.total_wo_label, 'total'),
                (self.open_wo_label, 'open'),
                (self.overdue_wo_label, 'overdue'),
                (self.completed_wo_label, 'completed')
            ]:
                # Find all child labels
                labels = box.findChildren(QLabel)
                # The second label should be the value label
                if len(labels) >= 2:
                    value_label = labels[1]  # Use index 1 instead of -1
                    value_label.setText(str(stats.get(key, 0)))
        
        # Load recent work orders
        recent_orders = self.db_manager.get_recent_work_orders(10)  # Get 10 most recent
        self.recent_wo_table.setRowCount(len(recent_orders))
        
        for row, order in enumerate(recent_orders):
            self.recent_wo_table.setItem(row, 0, QTableWidgetItem(str(order['work_order_id'])))
            self.recent_wo_table.setItem(row, 1, QTableWidgetItem(order['title']))
            self.recent_wo_table.setItem(row, 2, QTableWidgetItem(order['equipment_name']))
            self.recent_wo_table.setItem(row, 3, QTableWidgetItem(order['assigned_to']))
            
            # Set status with color
            status_item = QTableWidgetItem(order['status'])
            status_item.setBackground(self.get_status_color(order['status']))
            self.recent_wo_table.setItem(row, 4, status_item)
        
        # Load upcoming maintenance
        upcoming = self.db_manager.get_upcoming_maintenance(10)  # Get 10 upcoming tasks
        self.upcoming_maintenance_table.setRowCount(len(upcoming))
        
        for row, task in enumerate(upcoming):
            self.upcoming_maintenance_table.setItem(row, 0, QTableWidgetItem(task['equipment_name']))
            self.upcoming_maintenance_table.setItem(row, 1, QTableWidgetItem(task['task_name']))
            self.upcoming_maintenance_table.setItem(row, 2, QTableWidgetItem(str(task['due_date'])))
            
            # Set priority with color
            priority_item = QTableWidgetItem(task['priority'])
            priority_item.setBackground(self.get_priority_color(task['priority']))
            self.upcoming_maintenance_table.setItem(row, 3, priority_item)

    def get_status_color(self, status):
        """Get color for work order status"""
        colors = {
            "Open": QColor("#2196F3"),
            "In Progress": QColor("#FF9800"),
            "On Hold": QColor("#9C27B0"),
            "Completed": QColor("#4CAF50"),
            "Cancelled": QColor("#9E9E9E"),
            "Overdue": QColor("#F44336")
        }
        return colors.get(status, QColor("#607D8B"))

    def get_priority_color(self, priority):
        """Get color for priority level"""
        colors = {
            "Low": QColor("#8BC34A"),
            "Medium": QColor("#FFC107"),
            "High": QColor("#FF5722"),
            "Critical": QColor("#F44336")
        }
        return colors.get(priority, QColor("#607D8B"))

    def load_work_orders(self):
        """Load all work orders"""
        work_orders = self.db_manager.get_all_work_orders()
        
        # Keep the table code for compatibility
        self.work_orders_table.setRowCount(len(work_orders))
        
        # Prepare data for card view
        card_data = []
        
        for row, order in enumerate(work_orders):
            # Update table
            self.work_orders_table.setItem(row, 0, QTableWidgetItem(str(order['work_order_id'])))
            self.work_orders_table.setItem(row, 1, QTableWidgetItem(order['title']))
            self.work_orders_table.setItem(row, 2, QTableWidgetItem(order['equipment_name']))
            self.work_orders_table.setItem(row, 3, QTableWidgetItem(order.get('assignment_type', 'Individual')))
            
            # Format assigned to
            assigned_to = ""
            if order.get('assignment_type') == 'Team':
                team_name = self.db_manager.get_team_name(order['team_id'])
                assigned_to = f"Team: {team_name}"
            else:
                craftsman = self.db_manager.get_craftsman_by_id(order.get('craftsman_id'))
                if craftsman:
                    assigned_to = f"{craftsman['first_name']} {craftsman['last_name']}"
            
            self.work_orders_table.setItem(row, 4, QTableWidgetItem(assigned_to))
            self.work_orders_table.setItem(row, 5, QTableWidgetItem(str(order['due_date'])))
            self.work_orders_table.setItem(row, 6, QTableWidgetItem(order['status']))
            self.work_orders_table.setItem(row, 7, QTableWidgetItem(order['priority']))
            self.work_orders_table.setItem(row, 8, QTableWidgetItem(str(order['created_date'])))
            
            # Prepare card data
            card_item = {
                'work_order_id': order['work_order_id'],
                'title': order['title'],
                'equipment_name': order['equipment_name'],
                'assigned_to': assigned_to,
                'due_date': str(order['due_date']),
                'status': order['status'],
                'priority': order['priority'],
                'created_date': str(order['created_date']),
                'description': order.get('description', ''),
                'assignment_type': order.get('assignment_type', 'Individual'),
                'craftsman_id': order.get('craftsman_id'),
                'team_id': order.get('team_id'),
                'estimated_hours': order.get('estimated_hours', 0),
                'actual_hours': order.get('actual_hours', 0)
            }
            card_data.append(card_item)
        
        # Update card view
        self.work_orders_cards.set_data(card_data)

    def filter_work_orders(self):
        """Filter work orders based on search and filter criteria"""
        search_text = self.wo_search.text().lower()
        status_filter = self.wo_status_filter.currentText()
        priority_filter = self.wo_priority_filter.currentText()
        assignment_filter = self.wo_assignment_filter.currentText()
        date_filter = self.wo_date_filter.currentText()
        
        # Get current date for date filtering
        current_date = QDate.currentDate()
        
        def filter_func(work_order):
            show = True
            
            # Apply text search
            if search_text:
                # Search through all searchable fields
                searchable_fields = [
                    'title', 'equipment_name', 'assigned_to', 
                    'status', 'priority', 'description'
                ]
                found = False
                for field in searchable_fields:
                    if field in work_order and str(work_order[field]).lower().find(search_text) != -1:
                        found = True
                        break
                if not found:
                    show = False
            
            # Apply status filter
            if status_filter != "All Statuses" and show:
                if work_order['status'] != status_filter:
                    show = False
            
            # Apply priority filter
            if priority_filter != "All Priorities" and show:
                if work_order['priority'] != priority_filter:
                    show = False
            
            # Apply assignment filter
            if assignment_filter != "All Assignments" and show:
                if work_order['assignment_type'] != assignment_filter:
                    show = False
            
            # Apply date filter
            if date_filter != "All Dates" and show:
                due_date = QDate.fromString(work_order['due_date'], "yyyy-MM-dd")
                if date_filter == "Today" and due_date != current_date:
                    show = False
                elif date_filter == "This Week" and (due_date < current_date or due_date > current_date.addDays(7)):
                    show = False
                elif date_filter == "This Month" and (due_date < current_date or due_date > current_date.addMonths(1)):
                    show = False
                elif date_filter == "Overdue" and due_date >= current_date:
                    show = False
            
            return show
        
        # Apply the filter function to the card view
        self.work_orders_cards.filter_data(filter_func)

    def create_work_order(self):
        """Open dialog to create a new work order"""
        dialog = WorkOrderDialog(self.db_manager, parent=self)
        if dialog.exec():
            # Immediately refresh the work orders table after creation
            self.load_work_orders()
            # Also refresh other related data
            self.load_dashboard_data()
            self.refresh_calendar_views()

    def view_work_order_details(self, index):
        """View details of the selected work order"""
        row = index.row()
        work_order_id = int(self.work_orders_cards.item(row, 0).text())
        
        # Get work order data
        work_order = self.db_manager.get_work_order_by_id(work_order_id)
        if work_order:
            dialog = WorkOrderDialog(self.db_manager, work_order, parent=self)
            if dialog.exec():
                self.refresh_data()

    def show_work_order_context_menu(self, data, position):
        """Show context menu for work orders"""
        menu = QMenu(self)
        
        view_action = menu.addAction("View Details")
        edit_action = menu.addAction("Edit Work Order")
        
        menu.addSeparator()
        
        status_menu = menu.addMenu("Change Status")
        status_actions = {}
        
        for status in ["Open", "In Progress", "On Hold", "Completed", "Cancelled"]:
            action = status_menu.addAction(status)
            status_actions[action] = status
        
        menu.addSeparator()
        
        delete_action = menu.addAction("Delete Work Order")
        
        # Show menu and handle actions
        action = menu.exec(position)
        
        if action:
            work_order_id = data['work_order_id']
            
            if action == view_action:
                work_order = self.db_manager.get_work_order_by_id(work_order_id)
                if work_order:
                    dialog = WorkOrderDialog(self.db_manager, work_order, parent=self)
                    if dialog.exec():
                        self.refresh_data()
            
            elif action == edit_action:
                work_order = self.db_manager.get_work_order_by_id(work_order_id)
                if work_order:
                    dialog = WorkOrderDialog(self.db_manager, work_order, parent=self)
                    if dialog.exec():
                        self.refresh_data()
            
            elif action == delete_action:
                self.delete_work_order(work_order_id)
            
            elif action in status_actions:
                self.change_work_order_status(work_order_id, status_actions[action])

    def delete_work_order(self, work_order_id):
        """Delete a work order after confirmation"""
        reply = QMessageBox.question(
            self,
            "Confirm Deletion",
            "Are you sure you want to delete this work order?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            if self.db_manager.delete_work_order(work_order_id):
                QMessageBox.information(self, "Success", "Work order deleted successfully!")
                self.refresh_data()
            else:
                QMessageBox.critical(self, "Error", "Failed to delete work order!")

    def change_work_order_status(self, work_order_id, new_status):
        """Change the status of a work order"""
        if self.db_manager.update_work_order_status(work_order_id, new_status):
            QMessageBox.information(self, "Success", f"Work order status changed to {new_status}!")
            self.refresh_data()
        else:
            QMessageBox.critical(self, "Error", "Failed to update work order status!")

    def change_calendar_view(self, view_type):
        """Change the calendar view type"""
        if view_type == "Month View":
            self.calendar_stack.setCurrentWidget(self.month_view)
            self.calendar_title.setText(f"Month View - {self.month_view.current_date.toString('MMMM yyyy')}")
        elif view_type == "Week View":
            self.calendar_stack.setCurrentWidget(self.week_view)
            start_date = self.week_view.week_start_date
            end_date = start_date.addDays(6)
            self.calendar_title.setText(f"Week View - {start_date.toString('MMM d')} to {end_date.toString('MMM d, yyyy')}")
        elif view_type == "Day View":
            self.calendar_stack.setCurrentWidget(self.day_view)
            self.calendar_title.setText(f"Day View - {self.day_view.current_date.toString('dddd, MMMM d, yyyy')}")

    def previous_calendar_period(self):
        """Go to previous period in calendar view"""
        current_view = self.calendar_view_type.currentText()
        
        if current_view == "Month View":
            self.month_view.previous_month()
            self.calendar_title.setText(f"Month View - {self.month_view.current_date.toString('MMMM yyyy')}")
        elif current_view == "Week View":
            self.week_view.previous_week()
            start_date = self.week_view.week_start_date
            end_date = start_date.addDays(6)
            self.calendar_title.setText(f"Week View - {start_date.toString('MMM d')} to {end_date.toString('MMM d, yyyy')}")
        elif current_view == "Day View":
            self.day_view.previous_day()
            self.calendar_title.setText(f"Day View - {self.day_view.current_date.toString('dddd, MMMM d, yyyy')}")

    def next_calendar_period(self):
        """Go to next period in calendar view"""
        current_view = self.calendar_view_type.currentText()
        
        if current_view == "Month View":
            self.month_view.next_month()
            self.calendar_title.setText(f"Month View - {self.month_view.current_date.toString('MMMM yyyy')}")
        elif current_view == "Week View":
            self.week_view.next_week()
            start_date = self.week_view.week_start_date
            end_date = start_date.addDays(6)
            self.calendar_title.setText(f"Week View - {start_date.toString('MMM d')} to {end_date.toString('MMM d, yyyy')}")
        elif current_view == "Day View":
            self.day_view.next_day()
            self.calendar_title.setText(f"Day View - {self.day_view.current_date.toString('dddd, MMMM d, yyyy')}")

    def go_to_today(self):
        """Go to today in calendar view"""
        current_view = self.calendar_view_type.currentText()
        
        if current_view == "Month View":
            self.month_view.go_to_today()
            self.calendar_title.setText(f"Month View - {self.month_view.current_date.toString('MMMM yyyy')}")
        elif current_view == "Week View":
            self.week_view.go_to_today()
            start_date = self.week_view.week_start_date
            end_date = start_date.addDays(6)
            self.calendar_title.setText(f"Week View - {start_date.toString('MMM d')} to {end_date.toString('MMM d, yyyy')}")
        elif current_view == "Day View":
            self.day_view.go_to_today()
            self.calendar_title.setText(f"Day View - {self.day_view.current_date.toString('dddd, MMMM d, yyyy')}")

    def refresh_calendar_views(self):
        """Refresh all calendar views"""
        self.month_view.refresh_view()
        self.week_view.refresh_view()
        self.day_view.refresh_view()
        
        # Update calendar title
        self.change_calendar_view(self.calendar_view_type.currentText())

    def handle_calendar_date_clicked(self, date):
        """Handle when a date is clicked in the calendar"""
        # If in month view, switch to day view for the clicked date
        if self.calendar_stack.currentWidget() == self.month_view:
            self.day_view.set_date(date)
            self.calendar_view_type.setCurrentText("Day View")
            self.change_calendar_view("Day View")
        
        # If in week view, switch to day view for the clicked date
        elif self.calendar_stack.currentWidget() == self.week_view:
            self.day_view.set_date(date)
            self.calendar_view_type.setCurrentText("Day View")
            self.change_calendar_view("Day View")

    def view_work_order_from_calendar(self, work_order_id):
        """View work order details from calendar"""
        work_order = self.db_manager.get_work_order_by_id(work_order_id)
        if work_order:
            dialog = WorkOrderDialog(self.db_manager, work_order, parent=self)
            if dialog.exec():
                self.refresh_data()

    def generate_summary_report(self):
        """Generate a summary report of work orders"""
        try:
            # Get date range from UI
            start_date = self.report_date_from.date().toPython()
            end_date = self.report_date_to.date().toPython()
            
            # Get status filter
            status = self.report_status_filter.currentText()
            if status == "All Statuses":
                status = None
            
            # Get report format
            report_format = self.report_format.currentText()
            
            # Use the new reporting module to generate the report
            from reporting import create_work_order_report, open_containing_folder, open_report_file
            
            # Generate the report
            report_path = create_work_order_report(
                self.db_manager, 
                start_date, 
                end_date, 
                status, 
                "summary"
            )
            
            if report_path:
                # Show success message
                msg = QMessageBox(self)
                msg.setIcon(QMessageBox.Information)
                msg.setWindowTitle("Report Generated")
                msg.setText("Summary report generated successfully!")
                msg.setInformativeText(f"The report has been saved to:\n{report_path}")
                
                open_folder_button = msg.addButton("Open Folder", QMessageBox.ActionRole)
                open_report_button = msg.addButton("Open Report", QMessageBox.ActionRole)
                msg.addButton(QMessageBox.Ok)
                
                result = msg.exec()
                
                if msg.clickedButton() == open_folder_button:
                    open_containing_folder(report_path)
                elif msg.clickedButton() == open_report_button:
                    open_report_file(report_path)
            else:
                QMessageBox.critical(self, "Error", "Failed to generate report!")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to generate summary report: {str(e)}")

    def generate_completion_report(self):
        """Generate completion time analysis report"""
        start_date = self.report_date_from.date().toPython()
        end_date = self.report_date_to.date().toPython()
        report_format = self.report_format.currentText()
        
        report_path = self.db_manager.generate_completion_time_report(
            start_date, end_date, report_format
        )
        
        if report_path:
            self.show_report_success_message(report_path)
            self.load_recent_reports()
        else:
            QMessageBox.critical(self, "Error", "Failed to generate report!")

    def generate_craftsmen_report(self):
        """Generate craftsmen performance report"""
        try:
            # Open dialog to select craftsman
            from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QComboBox, QPushButton, QHBoxLayout, QCheckBox
            
            dialog = QDialog(self)
            dialog.setWindowTitle("Craftsman Report")
            layout = QVBoxLayout(dialog)
            
            # Add option to generate report for all craftsmen
            all_craftsmen_checkbox = QCheckBox("Generate report for all craftsmen")
            layout.addWidget(all_craftsmen_checkbox)
            
            # Add craftsman selection
            craftsman_label = QLabel("Select Craftsman:")
            layout.addWidget(craftsman_label)
            craftsman_combo = QComboBox()
            
            # Get all craftsmen from database
            craftsmen_list = self.db_manager.get_all_craftsmen()
            for craftsman in craftsmen_list:
                display_name = f"{craftsman['first_name']} {craftsman['last_name']}"
                craftsman_combo.addItem(display_name, craftsman['craftsman_id'])
            
            layout.addWidget(craftsman_combo)
            
            # Add report type selection
            layout.addWidget(QLabel("Report Type:"))
            report_type_combo = QComboBox()
            report_type_combo.addItems(["performance", "complete", "skills", "training"])
            layout.addWidget(report_type_combo)
            
            # Connect checkbox to disable/enable craftsman selection
            def toggle_craftsman_selection(checked):
                craftsman_label.setEnabled(not checked)
                craftsman_combo.setEnabled(not checked)
            
            all_craftsmen_checkbox.toggled.connect(toggle_craftsman_selection)
            
            # Add buttons
            button_layout = QHBoxLayout()
            generate_btn = QPushButton("Generate Report")
            cancel_btn = QPushButton("Cancel")
            button_layout.addWidget(generate_btn)
            button_layout.addWidget(cancel_btn)
            layout.addLayout(button_layout)
            
            generate_btn.clicked.connect(dialog.accept)
            cancel_btn.clicked.connect(dialog.reject)
            
            if not dialog.exec():
                return
            
            # Import reporting functions
            from reporting import create_craftsman_report, open_containing_folder, open_report_file
            from reportlab.lib.pagesizes import letter
            from reportlab.platypus import SimpleDocTemplate, PageBreak
            import os
            from datetime import datetime
            
            report_type = report_type_combo.currentText()
            
            if all_craftsmen_checkbox.isChecked():
                # Generate a combined report for all craftsmen
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                report_filename = f"all_craftsmen_{report_type}_{timestamp}.pdf"
                report_path = os.path.join(os.path.expanduser("~"), "CMMS_Reports", report_filename)
                
                # Create a document for the combined report
                doc = SimpleDocTemplate(report_path, pagesize=letter)
                all_elements = []
                
                # Show progress dialog
                progress = QProgressDialog("Generating reports for all craftsmen...", "Cancel", 0, len(craftsmen_list), self)
                progress.setWindowTitle("Generating Report")
                progress.setMinimumDuration(0)
                progress.setValue(0)
                
                # Generate report for each craftsman
                for i, craftsman in enumerate(craftsmen_list):
                    progress.setValue(i)
                    if progress.wasCanceled():
                        break
                    
                    # Get craftsman data and create a temporary report
                    craftsman_id = craftsman['craftsman_id']
                    temp_report_path = create_craftsman_report(self.db_manager, craftsman_id, report_type, return_elements=True)
                    
                    if temp_report_path and isinstance(temp_report_path, list):
                        # Add elements to the combined report
                        all_elements.extend(temp_report_path)
                        all_elements.append(PageBreak())
                
                progress.setValue(len(craftsmen_list))
                
                # Build the combined report
                if all_elements:
                    doc.build(all_elements)
                    
                    # Show success message
                    msg = QMessageBox(self)
                    msg.setIcon(QMessageBox.Information)
                    msg.setWindowTitle("Report Generated")
                    msg.setText("Combined craftsmen report generated successfully!")
                    msg.setInformativeText(f"The report has been saved to:\n{report_path}")
                    
                    open_folder_button = msg.addButton("Open Folder", QMessageBox.ActionRole)
                    open_report_button = msg.addButton("Open Report", QMessageBox.ActionRole)
                    msg.addButton(QMessageBox.Ok)
                    
                    result = msg.exec()
                    
                    if msg.clickedButton() == open_folder_button:
                        open_containing_folder(report_path)
                    elif msg.clickedButton() == open_report_button:
                        open_report_file(report_path)
                else:
                    QMessageBox.critical(self, "Error", "Failed to generate combined report!")
            else:
                # Generate report for a single craftsman
                craftsman_id = craftsman_combo.currentData()
                
                if not craftsman_id:
                    QMessageBox.warning(self, "Warning", "Please select a craftsman first!")
                    return
                
                # Generate the report
                report_path = create_craftsman_report(self.db_manager, craftsman_id, report_type)
                
                if report_path:
                    # Show success message
                    msg = QMessageBox(self)
                    msg.setIcon(QMessageBox.Information)
                    msg.setWindowTitle("Report Generated")
                    msg.setText("Craftsman report generated successfully!")
                    msg.setInformativeText(f"The report has been saved to:\n{report_path}")
                    
                    open_folder_button = msg.addButton("Open Folder", QMessageBox.ActionRole)
                    open_report_button = msg.addButton("Open Report", QMessageBox.ActionRole)
                    msg.addButton(QMessageBox.Ok)
                    
                    result = msg.exec()
                    
                    if msg.clickedButton() == open_folder_button:
                        open_containing_folder(report_path)
                    elif msg.clickedButton() == open_report_button:
                        open_report_file(report_path)
                else:
                    QMessageBox.critical(self, "Error", "Failed to generate report!")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to generate craftsman report: {str(e)}")

    def generate_equipment_report(self):
        """Generate a report for specific equipment"""
        try:
            # Open dialog to select equipment
            from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QComboBox, QPushButton, QHBoxLayout
            
            dialog = QDialog(self)
            dialog.setWindowTitle("Select Equipment for Report")
            layout = QVBoxLayout(dialog)
            
            # Add equipment selection
            layout.addWidget(QLabel("Select Equipment:"))
            equipment_combo = QComboBox()
            
            # Get all equipment from database
            equipment_list = self.db_manager.get_all_equipment()
            for equipment in equipment_list:
                equipment_combo.addItem(equipment['equipment_name'], equipment['equipment_id'])
            
            layout.addWidget(equipment_combo)
            
            # Add buttons
            button_layout = QHBoxLayout()
            generate_btn = QPushButton("Generate Report")
            cancel_btn = QPushButton("Cancel")
            button_layout.addWidget(generate_btn)
            button_layout.addWidget(cancel_btn)
            layout.addLayout(button_layout)
            
            generate_btn.clicked.connect(dialog.accept)
            cancel_btn.clicked.connect(dialog.reject)
            
            if not dialog.exec():
                return
            
            # Get selected equipment ID
            equipment_id = equipment_combo.currentData()
            if not equipment_id:
                QMessageBox.warning(self, "Warning", "Please select equipment first!")
                return
            
            # Use the reporting module to generate the report
            from reporting import create_equipment_report, open_containing_folder, open_report_file
            
            # Generate the report
            report_path = create_equipment_report(self.db_manager, equipment_id, "maintenance")
            
            if report_path:
                # Show success message
                msg = QMessageBox(self)
                msg.setIcon(QMessageBox.Information)
                msg.setWindowTitle("Report Generated")
                msg.setText("Equipment maintenance report generated successfully!")
                msg.setInformativeText(f"The report has been saved to:\n{report_path}")
                
                open_folder_button = msg.addButton("Open Folder", QMessageBox.ActionRole)
                open_report_button = msg.addButton("Open Report", QMessageBox.ActionRole)
                msg.addButton(QMessageBox.Ok)
                
                result = msg.exec()
                
                if msg.clickedButton() == open_folder_button:
                    open_containing_folder(report_path)
                elif msg.clickedButton() == open_report_button:
                    open_report_file(report_path)
            else:
                QMessageBox.critical(self, "Error", "Failed to generate report!")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to generate equipment report: {str(e)}")

    def generate_cost_report(self):
        """Generate a cost analysis report of work orders"""
        try:
            # Get date range from UI
            start_date = self.report_date_from.date().toPython()
            end_date = self.report_date_to.date().toPython()
            
            # Get status filter
            status = self.report_status_filter.currentText()
            if status == "All Statuses":
                status = None
            
            # Get report format
            report_format = self.report_format.currentText()
            
            # Use the new reporting module to generate the report
            from reporting import create_work_order_report, open_containing_folder, open_report_file
            
            # Generate the report
            report_path = create_work_order_report(
                self.db_manager, 
                start_date, 
                end_date, 
                status, 
                "cost"
            )
            
            if report_path:
                # Show success message
                msg = QMessageBox(self)
                msg.setIcon(QMessageBox.Information)
                msg.setWindowTitle("Report Generated")
                msg.setText("Cost analysis report generated successfully!")
                msg.setInformativeText(f"The report has been saved to:\n{report_path}")
                
                open_folder_button = msg.addButton("Open Folder", QMessageBox.ActionRole)
                open_report_button = msg.addButton("Open Report", QMessageBox.ActionRole)
                msg.addButton(QMessageBox.Ok)
                
                result = msg.exec()
                
                if msg.clickedButton() == open_folder_button:
                    open_containing_folder(report_path)
                elif msg.clickedButton() == open_report_button:
                    open_report_file(report_path)
            else:
                QMessageBox.critical(self, "Error", "Failed to generate report!")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to generate cost report: {str(e)}")

    def generate_custom_report(self):
        """Generate custom report with selected fields"""
        try:
            # Open dialog to select fields
            from workOrders.report_dialog import CustomReportDialog
            dialog = CustomReportDialog(self)
            if not dialog.exec():
                return
            
            selected_fields = dialog.get_selected_fields()
            if not selected_fields:
                QMessageBox.warning(self, "Warning", "No fields selected for the report!")
                return
            
            # Get date range from UI
            start_date = self.report_date_from.date().toPython()
            end_date = self.report_date_to.date().toPython()
            
            # Get status filter
            status = self.report_status_filter.currentText()
            if status == "All Statuses":
                status = None
            
            # Use the new reporting module to generate the report
            from reporting import create_work_order_report, open_containing_folder, open_report_file
            
            # Generate the report with selected fields
            report_path = create_work_order_report(
                self.db_manager, 
                start_date, 
                end_date, 
                status, 
                "custom",
                selected_fields
            )
            
            if report_path:
                # Show success message
                msg = QMessageBox(self)
                msg.setIcon(QMessageBox.Information)
                msg.setWindowTitle("Report Generated")
                msg.setText("Custom report generated successfully!")
                msg.setInformativeText(f"The report has been saved to:\n{report_path}")
                
                open_folder_button = msg.addButton("Open Folder", QMessageBox.ActionRole)
                open_report_button = msg.addButton("Open Report", QMessageBox.ActionRole)
                msg.addButton(QMessageBox.Ok)
                
                result = msg.exec()
                
                if msg.clickedButton() == open_folder_button:
                    open_containing_folder(report_path)
                elif msg.clickedButton() == open_report_button:
                    open_report_file(report_path)
            else:
                QMessageBox.critical(self, "Error", "Failed to generate report!")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to generate custom report: {str(e)}")
    
    def show_report_success_message(self, report_path):
        """Show success message with option to open report"""
        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Information)
        msg.setWindowTitle("Report Generated")
        msg.setText("Report generated successfully!")
        msg.setInformativeText(f"The report has been saved to:\n{report_path}")
        
        open_btn = msg.addButton("Open Report", QMessageBox.ActionRole)
        open_folder_btn = msg.addButton("Open Folder", QMessageBox.ActionRole)
        msg.addButton(QMessageBox.Close)
        
        msg.exec()
        
        clicked_button = msg.clickedButton()
        if clicked_button == open_btn:
            self.open_file(report_path)
        elif clicked_button == open_folder_btn:
            self.open_folder(os.path.dirname(report_path))

    def open_file(self, file_path):
        """Open a file with the default application"""
        import platform
        import subprocess
        
        try:
            if platform.system() == "Windows":
                os.startfile(file_path)
            elif platform.system() == "Darwin":  # macOS
                subprocess.run(["open", file_path])
            else:  # Linux
                subprocess.run(["xdg-open", file_path])
        except Exception as e:
            QMessageBox.warning(self, "Warning", f"Could not open file: {str(e)}")

    def open_folder(self, folder_path):
        """Open a folder in the file explorer"""
        import platform
        import subprocess
        
        try:
            if platform.system() == "Windows":
                os.startfile(folder_path)
            elif platform.system() == "Darwin":  # macOS
                subprocess.run(["open", folder_path])
            else:  # Linux
                subprocess.run(["xdg-open", folder_path])
        except Exception as e:
            QMessageBox.warning(self, "Warning", f"Could not open folder: {str(e)}")

    def load_recent_reports(self):
        """Load recent reports into the list"""
        reports = self.db_manager.get_recent_reports(10)  # Get 10 most recent reports
        self.recent_reports_list.clear()
        
        for report in reports:
            item = QListWidgetItem(f"{report['report_name']} - {report['created_date']}")
            item.setData(Qt.UserRole, report['file_path'])
            self.recent_reports_list.addItem(item)
        
        # Connect double-click to open report
        self.recent_reports_list.itemDoubleClicked.connect(
            lambda item: self.open_file(item.data(Qt.UserRole)))

    def import_work_orders(self):
        """Import work orders from CSV or JSON file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Import Work Orders",
            "",
            "CSV Files (*.csv);;JSON Files (*.json)"
        )
        
        if not file_path:
            return
        
        try:
            if file_path.endswith('.csv'):
                success_count = self.db_manager.import_work_orders_from_csv(file_path)
            else:
                success_count = self.db_manager.import_work_orders_from_json(file_path)
            
            QMessageBox.information(
                self,
                "Import Successful",
                f"Successfully imported {success_count} work orders!"
            )
            
            self.refresh_data()
        
        except Exception as e:
            QMessageBox.critical(
                self,
                "Import Error",
                f"Failed to import work orders: {str(e)}"
            )

    def export_work_orders(self):
        """Export work orders to CSV or JSON file"""
        # Get export options
        dialog = QDialog(self)
        dialog.setWindowTitle("Export Work Orders")
        layout = QVBoxLayout(dialog)
        
        # Export format
        format_layout = QHBoxLayout()
        format_layout.addWidget(QLabel("Export Format:"))
        
        format_combo = QComboBox()
        format_combo.addItems(["CSV", "JSON"])
        format_layout.addWidget(format_combo)
        
        layout.addLayout(format_layout)
        
        # Filter options
        filter_group = QWidget()
        filter_layout = QFormLayout(filter_group)
        
        status_filter = QComboBox()
        status_filter.addItems(["All Statuses", "Open", "In Progress", "On Hold", "Completed", "Cancelled"])
        
        date_from = QDateEdit()
        date_from.setCalendarPopup(True)
        date_from.setDate(QDate.currentDate().addMonths(-1))
        
        date_to = QDateEdit()
        date_to.setCalendarPopup(True)
        date_to.setDate(QDate.currentDate())
        
        filter_layout.addRow("Status:", status_filter)
        filter_layout.addRow("Date From:", date_from)
        filter_layout.addRow("Date To:", date_to)
        
        layout.addWidget(filter_group)
        
        # Buttons
        buttons = QHBoxLayout()
        export_btn = QPushButton("Export")
        cancel_btn = QPushButton("Cancel")
        buttons.addWidget(export_btn)
        buttons.addWidget(cancel_btn)
        
        layout.addLayout(buttons)
        
        export_btn.clicked.connect(dialog.accept)
        cancel_btn.clicked.connect(dialog.reject)
        
        if not dialog.exec():
            return
        
        # Get export file path
        export_format = format_combo.currentText().lower()
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export Work Orders",
            f"work_orders_export_{datetime.now().strftime('%Y%m%d')}.{export_format}",
            f"{format_combo.currentText()} Files (*.{export_format})"
        )
        
        if not file_path:
            return
        
        # Get filter values
        status = status_filter.currentText()
        if status == "All Statuses":
            status = None
        
        start_date = date_from.date().toPython()
        end_date = date_to.date().toPython()
        
        # try:
        #     if export_format == "csv":
        #         success = self.db_manager.export_work_orders_to_csv(file_path, status, start_date, end_date)
        #     else:
        #         success = self.db_manager.export_work_orders_to_json(file_path, status, start_date, end_date)
            
            # if success:
            #     QMessageBox.information(
            #         self,
            #         "Export Successful",
            #         f"Work orders exported successfully to {file_path}")
            # else:
            #     QMessageBox.critical(self, "Error", "Failed to export work orders!")

    def save_settings(self):
        """Save work order settings"""
        # Create settings dictionary
        settings = {
            'notifications': {
                'new_work_orders': self.notify_on_new.isChecked(),
                'work_order_updates': self.notify_on_update.isChecked(),
                'approaching_due_dates': self.notify_on_due.isChecked(),
                'due_date_days': self.due_date_days.value()
            },
            'assignment': {
                'auto_assign': self.auto_assign.isChecked(),
                'assignment_method': self.assignment_method.currentText()
            },
            'defaults': {
                'priority': self.default_priority.currentText()
            },
            'email': {
                'enabled': self.email_notifications.isChecked(),
                'server': self.email_server.text(),
                'port': self.email_port.text(),
                'username': self.email_username.text(),
                'password': self.email_password.text(),
                'from_address': self.email_username.text()  # Use username as from address by default
            }
        }
        
        # Save settings to file
        try:
            from config import save_work_order_settings
            
            if save_work_order_settings(settings):
                QMessageBox.information(
                    self,
                    "Success",
                    "Settings saved successfully!"
                )
            else:
                QMessageBox.critical(
                    self,
                    "Error",
                    "Failed to save settings."
                )
        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                f"Failed to save settings: {str(e)}"
            )

    def load_settings(self):
        """Load work order settings"""
        try:
            from config import load_work_order_settings
            
            settings = load_work_order_settings()
            
            # Apply notification settings
            if 'notifications' in settings:
                notif = settings['notifications']
                self.notify_on_new.setChecked(notif.get('new_work_orders', True))
                self.notify_on_update.setChecked(notif.get('work_order_updates', True))
                self.notify_on_due.setChecked(notif.get('approaching_due_dates', True))
                self.due_date_days.setValue(notif.get('due_date_days', 2))
            
            # Apply assignment settings
            if 'assignment' in settings:
                assign = settings['assignment']
                self.auto_assign.setChecked(assign.get('auto_assign', False))
                method = assign.get('assignment_method', "Based on workload")
                index = self.assignment_method.findText(method)
                if index >= 0:
                    self.assignment_method.setCurrentIndex(index)
            
            # Apply default values
            if 'defaults' in settings:
                defaults = settings['defaults']
                priority = defaults.get('priority', "Medium")
                index = self.default_priority.findText(priority)
                if index >= 0:
                    self.default_priority.setCurrentIndex(index)
            
            # Apply email settings
            if 'email' in settings:
                email = settings['email']
                self.email_notifications.setChecked(email.get('enabled', False))
                self.email_server.setText(email.get('server', ''))
                self.email_port.setText(email.get('port', ''))
                self.email_username.setText(email.get('username', ''))
                self.email_password.setText(email.get('password', ''))
        
        except Exception as e:
            print(f"Error loading settings: {e}")

    def handle_work_order_click(self, data):
        """Handle single click on work order card - just select the card"""
        # Selection is handled internally by the CardTableWidget
        pass

    def edit_work_order(self, data):
        """Show edit dialog for a work order"""
        work_order_id = data.get('work_order_id')
        # Get the work order data first
        work_order = self.db_manager.get_work_order_by_id(work_order_id)
        if work_order:
            dialog = WorkOrderDialog(self.db_manager, work_order, parent=self)
            if dialog.exec_():
                self.load_work_orders()  # Refresh the list if changes were made
        else:
            QMessageBox.warning(self, "Error", "Could not find work order details!")