"""
Craftsman Portal - Interface for craftsmen to view and update their work orders
"""

import os
import sys
import json
from datetime import datetime, timedelta

from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                              QPushButton, QLabel, QTabWidget, QTableWidget, QTableWidgetItem,
                              QDialog, QFormLayout, QLineEdit, QTextEdit, QComboBox, QMessageBox,
                              QDateEdit, QTimeEdit, QScrollArea, QFrame, QGridLayout, QSpinBox,
                              QCheckBox, QFileDialog, QListWidget, QListWidgetItem, QSplitter,
                              QStackedWidget, QToolBar, QStatusBar, QProgressBar)
from PySide6.QtCore import Qt, QSize, QTimer, QDate, QTime, Signal, Slot
from PySide6.QtGui import QIcon, QPixmap, QFont, QColor

from config import WORK_ORDER_SETTINGS_FILE, load_work_order_settings
from maintenance_report import MaintenanceReportDialog

class CraftsmanPortal(QMainWindow):
    """Main window for the craftsman portal"""
    
    def __init__(self, db_manager, craftsman_id=None, parent=None):
        super().__init__(parent)
        self.db_manager = db_manager
        self.craftsman_id = craftsman_id
        self.craftsman_data = None
        
        if craftsman_id:
            self.craftsman_data = self.db_manager.get_craftsman_by_id(craftsman_id)
        
        self.setWindowTitle("CMMS - Craftsman Portal")
        self.setMinimumSize(1000, 700)
        
        # Create central widget and main layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)
        
        # Create header with craftsman info
        self.create_header()
        
        # Create tab widget
        self.tab_widget = QTabWidget()
        self.main_layout.addWidget(self.tab_widget)
        
        # Setup tabs
        self.setup_dashboard_tab()
        self.setup_work_orders_tab()
        self.setup_maintenance_history_tab()
        self.setup_skills_tab()
        
        # Create status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")
        
        # Setup refresh timer
        self.refresh_timer = QTimer(self)
        self.refresh_timer.timeout.connect(self.refresh_data)
        self.refresh_timer.start(60000)  # Refresh every minute
        
        # Load initial data
        self.refresh_data()
    
    def create_header(self):
        """Create header with craftsman information"""
        header_widget = QWidget()
        header_widget.setStyleSheet("""
            QWidget {
                background-color: #2c3e50;
                color: white;
                padding: 10px;
            }
            QLabel {
                color: white;
            }
        """)
        header_layout = QHBoxLayout(header_widget)
        
        # Add craftsman avatar placeholder
        avatar_label = QLabel()
        avatar_label.setFixedSize(64, 64)
        avatar_label.setStyleSheet("""
            background-color: #34495e;
            border-radius: 32px;
            padding: 5px;
        """)
        
        # Try to load avatar image, use placeholder if not available
        if self.craftsman_data and hasattr(self.craftsman_data, 'avatar_path'):
            pixmap = QPixmap(self.craftsman_data.avatar_path)
            if not pixmap.isNull():
                avatar_label.setPixmap(pixmap.scaled(64, 64, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        
        # If no avatar loaded, show initials
        if self.craftsman_data and not avatar_label.pixmap():
            initials = f"{self.craftsman_data['first_name'][0]}{self.craftsman_data['last_name'][0]}"
            avatar_label.setText(initials)
            avatar_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            avatar_label.setFont(QFont("Arial", 20, QFont.Weight.Bold))
        
        header_layout.addWidget(avatar_label)
        
        # Add craftsman info
        info_layout = QVBoxLayout()
        
        if self.craftsman_data:
            name_label = QLabel(f"{self.craftsman_data['first_name']} {self.craftsman_data['last_name']}")
            name_label.setFont(QFont("Arial", 16, QFont.Weight.Bold))
            
            position_label = QLabel(self.craftsman_data['specialization'])
            position_label.setFont(QFont("Arial", 12))
            
            info_layout.addWidget(name_label)
            info_layout.addWidget(position_label)
        else:
            name_label = QLabel("Welcome, Craftsman")
            name_label.setFont(QFont("Arial", 16, QFont.Weight.Bold))
            info_layout.addWidget(name_label)
        
        header_layout.addLayout(info_layout)
        header_layout.addStretch()
        
        # Add notifications button
        self.notification_btn = QPushButton("Notifications")
        self.notification_btn.setIcon(QIcon("icons/notification.png"))
        self.notification_btn.clicked.connect(self.show_notifications)
        header_layout.addWidget(self.notification_btn)
        
        # Add logout button
        logout_btn = QPushButton("Logout")
        logout_btn.setIcon(QIcon("icons/logout.png"))
        logout_btn.clicked.connect(self.logout)
        header_layout.addWidget(logout_btn)
        
        self.main_layout.addWidget(header_widget)
    
    def setup_dashboard_tab(self):
        """Setup the dashboard tab with overview and statistics"""
        dashboard_widget = QWidget()
        layout = QVBoxLayout(dashboard_widget)
        
        # Create scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        # Create content widget
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(20, 20, 20, 20)
        content_layout.setSpacing(20)
        
        # Welcome section
        welcome_label = QLabel("My Dashboard")
        welcome_label.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        content_layout.addWidget(welcome_label)
        
        # Today's summary section
        summary_frame = QFrame()
        summary_frame.setFrameShape(QFrame.Shape.StyledPanel)
        summary_frame.setStyleSheet("""
            QFrame {
                background-color: #f5f5f5;
                border-radius: 10px;
                padding: 15px;
            }
        """)
        summary_layout = QVBoxLayout(summary_frame)
        
        summary_title = QLabel("Today's Summary")
        summary_title.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        summary_layout.addWidget(summary_title)
        
        # Create grid for summary stats
        stats_grid = QGridLayout()
        stats_grid.setSpacing(15)
        
        # Create stat boxes
        self.assigned_wo_box = self.create_stat_box("Assigned Work Orders", "0", "#3498db")
        self.due_today_box = self.create_stat_box("Due Today", "0", "#e74c3c")
        self.completed_box = self.create_stat_box("Completed Today", "0", "#2ecc71")
        self.pending_box = self.create_stat_box("Pending Reports", "0", "#f39c12")
        
        stats_grid.addWidget(self.assigned_wo_box, 0, 0)
        stats_grid.addWidget(self.due_today_box, 0, 1)
        stats_grid.addWidget(self.completed_box, 1, 0)
        stats_grid.addWidget(self.pending_box, 1, 1)
        
        summary_layout.addLayout(stats_grid)
        content_layout.addWidget(summary_frame)
        
        # Work orders due today section
        due_today_label = QLabel("Work Orders Due Today")
        due_today_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        content_layout.addWidget(due_today_label)
        
        self.due_today_table = QTableWidget()
        self.due_today_table.setColumnCount(5)
        self.due_today_table.setHorizontalHeaderLabels([
            "ID", "Title", "Equipment", "Priority", "Status"
        ])
        self.due_today_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.due_today_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.due_today_table.doubleClicked.connect(self.view_work_order)
        
        content_layout.addWidget(self.due_today_table)
        
        # Recent activity section
        activity_label = QLabel("Recent Activity")
        activity_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        content_layout.addWidget(activity_label)
        
        self.activity_list = QListWidget()
        content_layout.addWidget(self.activity_list)
        
        # Set the content widget as the scroll area's widget
        scroll.setWidget(content_widget)
        layout.addWidget(scroll)
        
        self.tab_widget.addTab(dashboard_widget, "Dashboard")
    
    def create_stat_box(self, title, value, color):
        """Create a styled statistics box"""
        box = QFrame()
        box.setFrameShape(QFrame.Shape.StyledPanel)
        box.setStyleSheet(f"""
            QFrame {{
                background-color: {color};
                border-radius: 8px;
                padding: 15px;
                color: white;
            }}
        """)
        
        layout = QVBoxLayout(box)
        
        title_label = QLabel(title)
        title_label.setFont(QFont("Arial", 12))
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("color: white;")
        
        value_label = QLabel(value)
        value_label.setFont(QFont("Arial", 24, QFont.Weight.Bold))
        value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        value_label.setStyleSheet("color: white;")
        
        layout.addWidget(title_label)
        layout.addWidget(value_label)
        
        return box
    
    def setup_work_orders_tab(self):
        """Setup the work orders tab with list and management features"""
        work_orders_widget = QWidget()
        layout = QVBoxLayout(work_orders_widget)
        
        # Create filter section
        filter_widget = QWidget()
        filter_layout = QHBoxLayout(filter_widget)
        
        self.wo_search = QLineEdit()
        self.wo_search.setPlaceholderText("Search work orders...")
        self.wo_search.textChanged.connect(self.filter_work_orders)
        
        self.wo_status_filter = QComboBox()
        self.wo_status_filter.addItems(["All Statuses", "Open", "In Progress", "On Hold", "Completed", "Cancelled"])
        self.wo_status_filter.currentTextChanged.connect(self.filter_work_orders)
        
        self.wo_priority_filter = QComboBox()
        self.wo_priority_filter.addItems(["All Priorities", "Low", "Medium", "High", "Critical"])
        self.wo_priority_filter.currentTextChanged.connect(self.filter_work_orders)
        
        filter_layout.addWidget(QLabel("Search:"))
        filter_layout.addWidget(self.wo_search, 3)
        filter_layout.addWidget(QLabel("Status:"))
        filter_layout.addWidget(self.wo_status_filter, 1)
        filter_layout.addWidget(QLabel("Priority:"))
        filter_layout.addWidget(self.wo_priority_filter, 1)
        
        layout.addWidget(filter_widget)
        
        # Create work orders table
        self.work_orders_table = QTableWidget()
        self.work_orders_table.setColumnCount(7)
        self.work_orders_table.setHorizontalHeaderLabels([
            "ID", "Title", "Equipment", "Due Date", "Priority", "Status", "Actions"
        ])
        self.work_orders_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.work_orders_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.work_orders_table.doubleClicked.connect(self.view_work_order)
        
        # Set column widths
        self.work_orders_table.setColumnWidth(0, 60)   # ID
        self.work_orders_table.setColumnWidth(1, 200)  # Title
        self.work_orders_table.setColumnWidth(2, 150)  # Equipment
        self.work_orders_table.setColumnWidth(3, 100)  # Due Date
        self.work_orders_table.setColumnWidth(4, 80)   # Priority
        self.work_orders_table.setColumnWidth(5, 100)  # Status
        self.work_orders_table.setColumnWidth(6, 150)  # Actions
        
        layout.addWidget(self.work_orders_table)
        
        # Add refresh button
        refresh_btn = QPushButton("Refresh")
        refresh_btn.clicked.connect(self.load_work_orders)
        layout.addWidget(refresh_btn)
        
        self.tab_widget.addTab(work_orders_widget, "Work Orders")
    
    def setup_maintenance_history_tab(self):
        """Setup the maintenance history tab"""
        history_widget = QWidget()
        layout = QVBoxLayout(history_widget)
        
        # Create filter section
        filter_widget = QWidget()
        filter_layout = QHBoxLayout(filter_widget)
        
        self.history_search = QLineEdit()
        self.history_search.setPlaceholderText("Search maintenance history...")
        self.history_search.textChanged.connect(self.filter_maintenance_history)
        
        self.history_date_from = QDateEdit()
        self.history_date_from.setCalendarPopup(True)
        self.history_date_from.setDate(QDate.currentDate().addMonths(-1))
        self.history_date_from.dateChanged.connect(self.filter_maintenance_history)
        
        self.history_date_to = QDateEdit()
        self.history_date_to.setCalendarPopup(True)
        self.history_date_to.setDate(QDate.currentDate())
        self.history_date_to.dateChanged.connect(self.filter_maintenance_history)
        
        filter_layout.addWidget(QLabel("Search:"))
        filter_layout.addWidget(self.history_search, 3)
        filter_layout.addWidget(QLabel("From:"))
        filter_layout.addWidget(self.history_date_from)
        filter_layout.addWidget(QLabel("To:"))
        filter_layout.addWidget(self.history_date_to)
        
        layout.addWidget(filter_widget)
        
        # Create maintenance history table
        self.history_table = QTableWidget()
        self.history_table.setColumnCount(6)
        self.history_table.setHorizontalHeaderLabels([
            "Date", "Equipment", "Work Order", "Type", "Description", "View Report"
        ])
        self.history_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.history_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        
        layout.addWidget(self.history_table)
        
        self.tab_widget.addTab(history_widget, "Maintenance History")
    
    def setup_skills_tab(self):
        """Setup the skills and certifications tab"""
        skills_widget = QWidget()
        layout = QVBoxLayout(skills_widget)
        
        # Create scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        # Create content widget
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(20, 20, 20, 20)
        content_layout.setSpacing(20)
        
        # Skills section
        skills_label = QLabel("My Skills & Certifications")
        skills_label.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        content_layout.addWidget(skills_label)
        
        # Skills table
        self.skills_table = QTableWidget()
        self.skills_table.setColumnCount(5)
        self.skills_table.setHorizontalHeaderLabels([
            "Skill", "Level", "Certification", "Date Obtained", "Expiry Date"
        ])
        self.skills_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.skills_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        
        content_layout.addWidget(self.skills_table)
        
        # Training section
        training_label = QLabel("Training & Development")
        training_label.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        content_layout.addWidget(training_label)
        
        # Training table
        self.training_table = QTableWidget()
        self.training_table.setColumnCount(5)
        self.training_table.setHorizontalHeaderLabels([
            "Training", "Provider", "Start Date", "Completion Date", "Status"
        ])
        self.training_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.training_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        
        content_layout.addWidget(self.training_table)
        
        # Set the content widget as the scroll area's widget
        scroll.setWidget(content_widget)
        layout.addWidget(scroll)
        
        self.tab_widget.addTab(skills_widget, "Skills & Training")
    
    def refresh_data(self):
        """Refresh all data in the portal"""
        if not self.craftsman_id:
            return
        
        self.load_dashboard_data()
        self.load_work_orders()
        self.load_maintenance_history()
        self.load_skills_data()
        
        self.status_bar.showMessage(f"Data refreshed at {datetime.now().strftime('%H:%M:%S')}")
    
    def load_dashboard_data(self):
        """Load data for the dashboard tab"""
        if not self.craftsman_id:
            return
        
        # Get today's date
        today = datetime.now().date()
        
        # Get work order statistics
        assigned_count = self.db_manager.get_craftsman_work_order_count(self.craftsman_id, status=None)
        due_today_count = self.db_manager.get_craftsman_work_order_count(self.craftsman_id, due_date=today)
        completed_today_count = self.db_manager.get_craftsman_work_order_count(
            self.craftsman_id, status="Completed", completion_date=today
        )
        pending_reports_count = self.db_manager.get_craftsman_pending_reports_count(self.craftsman_id)
        
        # Update stat boxes
        self.update_stat_box(self.assigned_wo_box, assigned_count)
        self.update_stat_box(self.due_today_box, due_today_count)
        self.update_stat_box(self.completed_box, completed_today_count)
        self.update_stat_box(self.pending_box, pending_reports_count)
        
        # Load work orders due today
        due_today_orders = self.db_manager.get_craftsman_work_orders(
            self.craftsman_id, due_date=today
        )
        self.due_today_table.setRowCount(len(due_today_orders))
        
        for row, order in enumerate(due_today_orders):
            self.due_today_table.setItem(row, 0, QTableWidgetItem(str(order['work_order_id'])))
            self.due_today_table.setItem(row, 1, QTableWidgetItem(order['title']))
            self.due_today_table.setItem(row, 2, QTableWidgetItem(order['equipment_name']))
            
            # Set priority with color
            priority_item = QTableWidgetItem(order['priority'])
            priority_item.setBackground(self.get_priority_color(order['priority']))
            self.due_today_table.setItem(row, 3, priority_item)
            
            # Set status with color
            status_item = QTableWidgetItem(order['status'])
            status_item.setBackground(self.get_status_color(order['status']))
            self.due_today_table.setItem(row, 4, status_item)
        
        # Load recent activity
        self.activity_list.clear()
        activities = self.db_manager.get_craftsman_recent_activity(self.craftsman_id, limit=10)
        
        for activity in activities:
            item = QListWidgetItem(f"{activity['date']} - {activity['description']}")
            self.activity_list.addItem(item)
    
    def update_stat_box(self, box, value):
        """Update the value in a stat box"""
        # Find the value label (second label in the box)
        labels = box.findChildren(QLabel)
        if len(labels) >= 2:
            value_label = labels[1]
            value_label.setText(str(value))
    
    def load_work_orders(self):
        """Load all work orders assigned to the craftsman"""
        if not self.craftsman_id:
            return
        
        work_orders = self.db_manager.get_craftsman_work_orders(self.craftsman_id)
        self.work_orders_table.setRowCount(len(work_orders))
        
        for row, order in enumerate(work_orders):
            self.work_orders_table.setItem(row, 0, QTableWidgetItem(str(order['work_order_id'])))
            self.work_orders_table.setItem(row, 1, QTableWidgetItem(order['title']))
            self.work_orders_table.setItem(row, 2, QTableWidgetItem(order['equipment_name']))
            self.work_orders_table.setItem(row, 3, QTableWidgetItem(str(order['due_date'])))
            
            # Set priority with color
            priority_item = QTableWidgetItem(order['priority'])
            priority_item.setBackground(self.get_priority_color(order['priority']))
            self.work_orders_table.setItem(row, 4, priority_item)
            
            # Set status with color
            status_item = QTableWidgetItem(order['status'])
            status_item.setBackground(self.get_status_color(order['status']))
            self.work_orders_table.setItem(row, 5, status_item)
            
            # Add action buttons
            actions_widget = QWidget()
            actions_layout = QHBoxLayout(actions_widget)
            actions_layout.setContentsMargins(2, 2, 2, 2)
            
            # View button
            view_btn = QPushButton("View")
            view_btn.setProperty("work_order_id", order['work_order_id'])
            view_btn.clicked.connect(lambda checked, btn=view_btn: self.view_work_order_by_id(btn.property("work_order_id")))
            actions_layout.addWidget(view_btn)
            
            # Add report button if work order is in progress or completed without report
            if order['status'] in ["In Progress", "Completed"] and not order.get('has_report', False):
                report_btn = QPushButton("Add Report")
                report_btn.setProperty("work_order_id", order['work_order_id'])
                report_btn.clicked.connect(lambda checked, btn=report_btn: self.add_maintenance_report(btn.property("work_order_id")))
                actions_layout.addWidget(report_btn)
            
            # Add update status button if not completed or cancelled
            if order['status'] not in ["Completed", "Cancelled"]:
                update_btn = QPushButton("Update")
                update_btn.setProperty("work_order_id", order['work_order_id'])
                update_btn.clicked.connect(lambda checked, btn=update_btn: self.update_work_order_status(btn.property("work_order_id")))
                actions_layout.addWidget(update_btn)
            
            self.work_orders_table.setCellWidget(row, 6, actions_widget)
    
    def filter_work_orders(self):
        """Filter work orders based on search and filter criteria"""
        search_text = self.wo_search.text().lower()
        status_filter = self.wo_status_filter.currentText()
        priority_filter = self.wo_priority_filter.currentText()
        
        for row in range(self.work_orders_table.rowCount()):
            show_row = True
            
            # Apply text search
            if search_text:
                text_match = False
                for col in range(self.work_orders_table.columnCount() - 1):  # Exclude actions column
                    item = self.work_orders_table.item(row, col)
                    if item and search_text in item.text().lower():
                        text_match = True
                        break
                if not text_match:
                    show_row = False
            
            # Apply status filter
            if status_filter != "All Statuses":
                status_item = self.work_orders_table.item(row, 5)
                if status_item and status_item.text() != status_filter:
                    show_row = False
            
            # Apply priority filter
            if priority_filter != "All Priorities":
                priority_item = self.work_orders_table.item(row, 4)
                if priority_item and priority_item.text() != priority_filter:
                    show_row = False
            
            self.work_orders_table.setRowHidden(row, not show_row)
    
    def load_maintenance_history(self):
        """Load maintenance history for the craftsman"""
        if not self.craftsman_id:
            return
        
        from_date = self.history_date_from.date().toPython()
        to_date = self.history_date_to.date().toPython()
        
        history = self.db_manager.get_craftsman_maintenance_history(
            self.craftsman_id, from_date, to_date
        )
        self.history_table.setRowCount(len(history))
        
        for row, entry in enumerate(history):
            self.history_table.setItem(row, 0, QTableWidgetItem(str(entry['date'])))
            self.history_table.setItem(row, 1, QTableWidgetItem(entry['equipment_name']))
            self.history_table.setItem(row, 2, QTableWidgetItem(str(entry['work_order_id'])))
            self.history_table.setItem(row, 3, QTableWidgetItem(entry['maintenance_type']))
            self.history_table.setItem(row, 4, QTableWidgetItem(entry['description']))
            
            # Add view report button if report exists
            if entry.get('report_id'):
                view_btn = QPushButton("View Report")
                view_btn.setProperty("report_id", entry['report_id'])
                view_btn.clicked.connect(lambda checked, btn=view_btn: self.view_maintenance_report(btn.property("report_id")))
                self.history_table.setCellWidget(row, 5, view_btn)
    
    def filter_maintenance_history(self):
        """Filter maintenance history based on search and date criteria"""
        search_text = self.history_search.text().lower()
        
        for row in range(self.history_table.rowCount()):
            show_row = True
            
            # Apply text search
            if search_text:
                text_match = False
                for col in range(5):  # Exclude view report column
                    item = self.history_table.item(row, col)
                    if item and search_text in item.text().lower():
                        text_match = True
                        break
                if not text_match:
                    show_row = False
            
            self.history_table.setRowHidden(row, not show_row)
    
    def load_skills_data(self):
        """Load skills and training data for the craftsman"""
        if not self.craftsman_id:
            return
        
        # Load skills
        skills = self.db_manager.get_craftsman_skills(self.craftsman_id)
        self.skills_table.setRowCount(len(skills))
        
        for row, skill in enumerate(skills):
            self.skills_table.setItem(row, 0, QTableWidgetItem(skill['skill_name']))
            self.skills_table.setItem(row, 1, QTableWidgetItem(skill['skill_level']))
            self.skills_table.setItem(row, 2, QTableWidgetItem(skill.get('certification', 'N/A')))
            self.skills_table.setItem(row, 3, QTableWidgetItem(str(skill.get('certification_date', 'N/A'))))
            
            # Set expiry date with color if approaching
            expiry_date = skill.get('expiry_date')
            expiry_item = QTableWidgetItem(str(expiry_date) if expiry_date else 'N/A')
            
            # Color code expiry dates
            if expiry_date:
                today = datetime.now().date()
                days_until_expiry = (expiry_date - today).days
                
                if days_until_expiry < 0:
                    # Expired
                    expiry_item.setBackground(QColor("#ffcccc"))  # Light red
                elif days_until_expiry < 30:
                    # Expiring soon
                    expiry_item.setBackground(QColor("#fff2cc"))  # Light yellow
            
            self.skills_table.setItem(row, 4, expiry_item)
        
        # Load training
        training = self.db_manager.get_craftsman_training(self.craftsman_id)
        self.training_table.setRowCount(len(training))
        
        for row, course in enumerate(training):
            self.training_table.setItem(row, 0, QTableWidgetItem(course['training_name']))
            self.training_table.setItem(row, 1, QTableWidgetItem(course['training_provider']))
            self.training_table.setItem(row, 2, QTableWidgetItem(str(course['training_date'])))
            self.training_table.setItem(row, 3, QTableWidgetItem(str(course['completion_date'])))
            
            # Set status with color
            status_item = QTableWidgetItem(course['training_status'])
            if course['training_status'] == 'Completed':
                status_item.setBackground(QColor("#d9ead3"))  # Light green
            elif course['training_status'] == 'In Progress':
                status_item.setBackground(QColor("#fff2cc"))  # Light yellow
            elif course['training_status'] == 'Scheduled':
                status_item.setBackground(QColor("#d0e0e3"))  # Light blue
            elif course['training_status'] == 'Failed':
                status_item.setBackground(QColor("#f4cccc"))  # Light red
            
            self.training_table.setItem(row, 4, status_item)
    
    def get_priority_color(self, priority):
        """Get background color for priority"""
        if priority == "Critical":
            return QColor("#f4cccc")  # Light red
        elif priority == "High":
            return QColor("#fce5cd")  # Light orange
        elif priority == "Medium":
            return QColor("#fff2cc")  # Light yellow
        elif priority == "Low":
            return QColor("#d9ead3")  # Light green
        return QColor("white")
    
    def get_status_color(self, status):
        """Get background color for status"""
        if status == "Open":
            return QColor("#d0e0e3")  # Light blue
        elif status == "In Progress":
            return QColor("#fff2cc")  # Light yellow
        elif status == "On Hold":
            return QColor("#d9d2e9")  # Light purple
        elif status == "Completed":
            return QColor("#d9ead3")  # Light green
        elif status == "Cancelled":
            return QColor("#efefef")  # Light gray
        return QColor("white")
    
    def view_work_order(self, index):
        """View work order details when double-clicked in table"""
        row = index.row()
        work_order_id = self.work_orders_table.item(row, 0).text()
        self.view_work_order_by_id(work_order_id)
    
    def view_work_order_by_id(self, work_order_id):
        """View work order details by ID"""
        work_order = self.db_manager.get_work_order_by_id(work_order_id)
        if not work_order:
            QMessageBox.warning(self, "Error", "Work order not found!")
            return
        
        dialog = WorkOrderDetailsDialog(work_order, self.db_manager, self)
        dialog.exec()
    
    def update_work_order_status(self, work_order_id):
        """Update the status of a work order"""
        work_order = self.db_manager.get_work_order_by_id(work_order_id)
        if not work_order:
            QMessageBox.warning(self, "Error", "Work order not found!")
            return
        
        dialog = UpdateStatusDialog(work_order, self.db_manager, self)
        if dialog.exec():
            self.refresh_data()
    
    def add_maintenance_report(self, work_order_id):
        """Add a maintenance report for a work order"""
        work_order = self.db_manager.get_work_order_by_id(work_order_id)
        if not work_order:
            QMessageBox.warning(self, "Error", "Work order not found!")
            return
        
        # Get equipment details to determine report fields
        equipment = self.db_manager.get_equipment_by_id(work_order['equipment_id'])
        if not equipment:
            QMessageBox.warning(self, "Error", "Equipment information not found!")
            return
        
        dialog = MaintenanceReportDialog(work_order, equipment, self.craftsman_id, self.db_manager, self)
        if dialog.exec():
            self.refresh_data()
            QMessageBox.information(self, "Success", "Maintenance report submitted successfully!")
    
    def view_maintenance_report(self, report_id):
        """View a maintenance report"""
        report = self.db_manager.get_maintenance_report(report_id)
        if not report:
            QMessageBox.warning(self, "Error", "Report not found!")
            return
        
        dialog = ViewReportDialog(report, self.db_manager, self)
        dialog.exec()
    
    def show_notifications(self):
        """Show notifications for the craftsman"""
        dialog = NotificationsDialog(self.craftsman_id, self.db_manager, self)
        dialog.exec()
    
    def logout(self):
        """Logout from the portal"""
        reply = QMessageBox.question(
            self, "Logout", "Are you sure you want to logout?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.close()


class WorkOrderDetailsDialog(QDialog):
    """Dialog to view work order details"""
    
    def __init__(self, work_order, db_manager, parent=None):
        super().__init__(parent)
        self.work_order = work_order
        self.db_manager = db_manager
        
        self.setWindowTitle(f"Work Order #{work_order['work_order_id']}")
        self.setMinimumSize(600, 500)
        
        layout = QVBoxLayout(self)
        
        # Create scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        # Create content widget
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(20, 20, 20, 20)
        content_layout.setSpacing(20)
        
        # Title section
        title_label = QLabel(work_order['title'])
        title_label.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        content_layout.addWidget(title_label)
        
        # Status and priority section
        status_widget = QWidget()
        status_layout = QHBoxLayout(status_widget)
        
        status_label = QLabel(f"Status: {work_order['status']}")
        status_label.setStyleSheet(f"background-color: {self.parent().get_status_color(work_order['status']).name()}; padding: 5px; border-radius: 3px;")
        
        priority_label = QLabel(f"Priority: {work_order['priority']}")
        priority_label.setStyleSheet(f"background-color: {self.parent().get_priority_color(work_order['priority']).name()}; padding: 5px; border-radius: 3px;")
        
        status_layout.addWidget(status_label)
        status_layout.addWidget(priority_label)
        status_layout.addStretch()
        
        content_layout.addWidget(status_widget)
        
        # Details section
        details_frame = QFrame()
        details_frame.setFrameShape(QFrame.Shape.StyledPanel)
        details_frame.setStyleSheet("background-color: #f5f5f5; padding: 10px; border-radius: 5px;")
        details_layout = QFormLayout(details_frame)
        
        # Get equipment details
        equipment = self.db_manager.get_equipment_by_id(work_order['equipment_id'])
        equipment_name = equipment['equipment_name'] if equipment else "Unknown"
        
        details_layout.addRow("Equipment:", QLabel(equipment_name))
        details_layout.addRow("Created Date:", QLabel(str(work_order['created_date'])))
        details_layout.addRow("Due Date:", QLabel(str(work_order['due_date'])))
        
        if work_order['completed_date']:
            details_layout.addRow("Completed Date:", QLabel(str(work_order['completed_date'])))
        
        details_layout.addRow("Estimated Hours:", QLabel(str(work_order.get('estimated_hours', 'N/A'))))
        
        content_layout.addWidget(details_frame)
        
        # Description section
        description_label = QLabel("Description:")
        description_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        content_layout.addWidget(description_label)
        
        description_text = QTextEdit()
        description_text.setPlainText(work_order['description'])
        description_text.setReadOnly(True)
        content_layout.addWidget(description_text)
        
        # Notes section
        if work_order.get('notes'):
            notes_label = QLabel("Notes:")
            notes_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
            content_layout.addWidget(notes_label)
            
            notes_text = QTextEdit()
            notes_text.setPlainText(work_order['notes'])
            notes_text.setReadOnly(True)
            content_layout.addWidget(notes_text)
        
        # Set the content widget as the scroll area's widget
        scroll.setWidget(content_widget)
        layout.addWidget(scroll)
        
        # Add close button
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)


class UpdateStatusDialog(QDialog):
    """Dialog to update work order status"""
    
    def __init__(self, work_order, db_manager, parent=None):
        super().__init__(parent)
        self.work_order = work_order
        self.db_manager = db_manager
        
        self.setWindowTitle(f"Update Status - Work Order #{work_order['work_order_id']}")
        self.setMinimumWidth(400)
        
        layout = QVBoxLayout(self)
        
        # Work order info
        info_label = QLabel(f"<b>{work_order['title']}</b>")
        layout.addWidget(info_label)
        
        # Current status
        current_status = QLabel(f"Current Status: {work_order['status']}")
        layout.addWidget(current_status)
        
        # Form layout
        form_layout = QFormLayout()
        
        # New status selection
        self.status_combo = QComboBox()
        available_statuses = ["Open", "In Progress", "On Hold", "Completed"]
        self.status_combo.addItems(available_statuses)
        
        # Set current status as selected
        current_index = available_statuses.index(work_order['status']) if work_order['status'] in available_statuses else 0
        self.status_combo.setCurrentIndex(current_index)
        
        form_layout.addRow("New Status:", self.status_combo)
        
        # Actual hours (show only when changing to Completed)
        self.hours_spin = QSpinBox()
        self.hours_spin.setRange(0, 100)
        self.hours_spin.setValue(work_order.get('actual_hours', 0) or 0)
        self.hours_label = QLabel("Actual Hours:")
        
        form_layout.addRow(self.hours_label, self.hours_spin)
        
        # Notes
        self.notes_text = QTextEdit()
        self.notes_text.setPlaceholderText("Enter any notes about this status update...")
        if work_order.get('notes'):
            self.notes_text.setPlainText(work_order['notes'])
        
        form_layout.addRow("Notes:", self.notes_text)
        
        layout.addLayout(form_layout)
        
        # Connect status change to show/hide fields
        self.status_combo.currentTextChanged.connect(self.on_status_changed)
        self.on_status_changed(self.status_combo.currentText())
        
        # Add buttons
        buttons_layout = QHBoxLayout()
        
        save_btn = QPushButton("Save")
        save_btn.clicked.connect(self.save_status)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        
        buttons_layout.addWidget(save_btn)
        buttons_layout.addWidget(cancel_btn)
        
        layout.addLayout(buttons_layout)
    
    def on_status_changed(self, status):
        """Show/hide fields based on selected status"""
        show_hours = (status == "Completed")
        self.hours_label.setVisible(show_hours)
        self.hours_spin.setVisible(show_hours)
    
    def save_status(self):
        """Save the updated status"""
        new_status = self.status_combo.currentText()
        actual_hours = self.hours_spin.value() if new_status == "Completed" else None
        notes = self.notes_text.toPlainText()
        
        # Prepare data for update
        update_data = {
            'work_order_id': self.work_order['work_order_id'],
            'status': new_status,
            'notes': notes
        }
        
        if new_status == "Completed":
            update_data['actual_hours'] = actual_hours
            update_data['completed_date'] = datetime.now().date()
        
        # Update work order
        if self.db_manager.update_work_order_status(update_data):
            QMessageBox.information(self, "Success", "Work order status updated successfully!")
            self.accept()
        else:
            QMessageBox.warning(self, "Error", "Failed to update work order status!")


class ViewReportDialog(QDialog):
    """Dialog to view a maintenance report"""
    
    def __init__(self, report, db_manager, parent=None):
        super().__init__(parent)
        self.report = report
        self.db_manager = db_manager
        
        self.setWindowTitle(f"Maintenance Report #{report['report_id']}")
        self.setMinimumSize(700, 600)
        
        layout = QVBoxLayout(self)
        
        # Create scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        # Create content widget
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(20, 20, 20, 20)
        content_layout.setSpacing(20)
        
        # Header section
        header_widget = QWidget()
        header_layout = QHBoxLayout(header_widget)
        
        # Get work order and equipment details
        work_order = self.db_manager.get_work_order_by_id(report['work_order_id'])
        equipment = self.db_manager.get_equipment_by_id(work_order['equipment_id']) if work_order else None
        
        # Title and equipment info
        title_layout = QVBoxLayout()
        
        title_label = QLabel(f"Maintenance Report")
        title_label.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        title_layout.addWidget(title_label)
        
        if work_order:
            wo_label = QLabel(f"Work Order: #{work_order['work_order_id']} - {work_order['title']}")
            title_layout.addWidget(wo_label)
        
        if equipment:
            equip_label = QLabel(f"Equipment: {equipment['equipment_name']}")
            title_layout.addWidget(equip_label)
        
        header_layout.addLayout(title_layout)
        header_layout.addStretch()
        
        # Report date and craftsman
        date_layout = QVBoxLayout()
        
        date_label = QLabel(f"Report Date: {report['report_date']}")
        date_layout.addWidget(date_label)
        
        # Get craftsman name
        craftsman = self.db_manager.get_craftsman_by_id(report['craftsman_id'])
        if craftsman:
            craftsman_name = f"{craftsman['first_name']} {craftsman['last_name']}"
            craftsman_label = QLabel(f"Craftsman: {craftsman_name}")
            date_layout.addWidget(craftsman_label)
        
        header_layout.addLayout(date_layout)
        
        content_layout.addWidget(header_widget)
        
        # Add separator line
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setFrameShadow(QFrame.Shadow.Sunken)
        content_layout.addWidget(line)
        
        # Report content
        # This will vary based on the report type and equipment
        report_data = json.loads(report['report_data']) if isinstance(report['report_data'], str) else report['report_data']
        
        # Create sections based on report data
        for section_name, section_data in report_data.items():
            # Skip metadata section
            if section_name == "metadata":
                continue
                
            # Create section header
            section_label = QLabel(section_name.replace('_', ' ').title())
            section_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
            content_layout.addWidget(section_label)
            
            # Create section frame
            section_frame = QFrame()
            section_frame.setFrameShape(QFrame.Shape.StyledPanel)
            section_frame.setStyleSheet("background-color: #f5f5f5; padding: 10px; border-radius: 5px;")
            section_layout = QFormLayout(section_frame)
            
            # Add fields
            for field_name, field_value in section_data.items():
                # Format field name
                display_name = field_name.replace('_', ' ').title()
                
                # Format field value based on type
                if isinstance(field_value, bool):
                    display_value = "Yes" if field_value else "No"
                elif isinstance(field_value, list):
                    display_value = ", ".join(field_value)
                else:
                    display_value = str(field_value)
                
                section_layout.addRow(f"{display_name}:", QLabel(display_value))
            
            content_layout.addWidget(section_frame)
        
        # Add comments section if available
        if report.get('comments'):
            comments_label = QLabel("Comments")
            comments_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
            content_layout.addWidget(comments_label)
            
            comments_text = QTextEdit()
            comments_text.setPlainText(report['comments'])
            comments_text.setReadOnly(True)
            content_layout.addWidget(comments_text)
        
        # Set the content widget as the scroll area's widget
        scroll.setWidget(content_widget)
        layout.addWidget(scroll)
        
        # Add buttons
        buttons_layout = QHBoxLayout()
        
        print_btn = QPushButton("Print Report")
        print_btn.clicked.connect(self.print_report)
        
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        
        buttons_layout.addWidget(print_btn)
        buttons_layout.addWidget(close_btn)
        
        layout.addLayout(buttons_layout)
    
    def print_report(self):
        """Print the maintenance report"""
        # This would typically open a print dialog
        QMessageBox.information(self, "Print", "Printing functionality would be implemented here.")


class NotificationsDialog(QDialog):
    """Dialog to show notifications for a craftsman"""
    
    def __init__(self, craftsman_id, db_manager, parent=None):
        super().__init__(parent)
        self.craftsman_id = craftsman_id
        self.db_manager = db_manager
        
        self.setWindowTitle("Notifications")
        self.setMinimumSize(500, 400)
        
        layout = QVBoxLayout(self)
        
        # Create notifications list
        self.notifications_list = QListWidget()
        layout.addWidget(self.notifications_list)
        
        # Add close button
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)
        
        # Load notifications
        self.load_notifications()
    
    def load_notifications(self):
        """Load notifications for the craftsman"""
        notifications = self.db_manager.get_craftsman_notifications(self.craftsman_id)
        
        for notification in notifications:
            item = QListWidgetItem()
            
            # Set icon based on notification type
            if notification['type'] == 'due_today':
                item.setIcon(QIcon("icons/alert.png"))
            elif notification['type'] == 'upcoming':
                item.setIcon(QIcon("icons/info.png"))
            elif notification['type'] == 'overdue':
                item.setIcon(QIcon("icons/warning.png"))
            
            # Set text
            item.setText(f"{notification['date']} - {notification['message']}")
            
            # Set background color based on read status
            if not notification['read']:
                item.setBackground(QColor("#f0f0f0"))
            
            # Store notification ID
            item.setData(Qt.UserRole, notification['notification_id'])
            
            self.notifications_list.addItem(item)
        
        # Mark notifications as read when viewed
        if notifications:
            self.db_manager.mark_notifications_as_read(self.craftsman_id)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # For testing purposes, create a database manager
    from db_ops.db_manager import DatabaseManager
    db_manager = DatabaseManager()
    
    # For testing, use a hardcoded craftsman ID
    # In a real application, this would come from login
    craftsman_id = 1
    
    portal = CraftsmanPortal(db_manager, craftsman_id)
    portal.show()
    
    sys.exit(app.exec())