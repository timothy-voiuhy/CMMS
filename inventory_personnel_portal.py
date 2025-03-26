"""
Inventory Personnel Portal - Interface for inventory personnel to manage inventory
"""

import os
import sys
from datetime import datetime, timedelta
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                              QPushButton, QLabel, QTabWidget, QTableWidget, QTableWidgetItem,
                              QDialog, QFormLayout, QLineEdit, QTextEdit, QComboBox, QMessageBox,
                              QDateEdit, QScrollArea, QFrame, QGridLayout, QSpinBox,
                              QCheckBox, QFileDialog, QListWidget, QListWidgetItem)
from PySide6.QtCore import Qt, QTimer, QDate
from PySide6.QtGui import QFont, QColor, QIcon

from inventory_personnel_login import InventoryPersonnelLoginDialog

class InventoryPersonnelPortal(QMainWindow):
    """Main window for the inventory personnel portal"""
    
    def __init__(self, db_manager, personnel_id=None, parent=None):
        super().__init__(parent)
        self.db_manager = db_manager
        self.personnel_id = personnel_id
        self.personnel_data = None
        
        if personnel_id:
            self.personnel_data = self.db_manager.get_personnel_by_id(personnel_id)
        
        self.setWindowTitle("CMMS - Inventory Personnel Portal")
        self.setMinimumSize(1000, 700)
        
        # Create central widget and main layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)
        
        # Create header with personnel info
        self.create_header()
        
        # Create tab widget
        self.tab_widget = QTabWidget()
        self.main_layout.addWidget(self.tab_widget)
        
        # Setup tabs
        self.setup_dashboard_tab()
        self.setup_inventory_tab()
        self.setup_purchase_orders_tab()
        self.setup_reports_tab()
        
        # Create status bar
        self.status_bar = self.statusBar()
        self.status_bar.showMessage("Ready")
        
        # Setup refresh timer
        self.refresh_timer = QTimer(self)
        self.refresh_timer.timeout.connect(self.refresh_data)
        self.refresh_timer.start(60000)  # Refresh every minute
        
        # Load initial data
        self.refresh_data()
    
    def create_header(self):
        """Create header with personnel information"""
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
        
        # Add personnel avatar/initials
        avatar_label = QLabel()
        avatar_label.setFixedSize(64, 64)
        avatar_label.setStyleSheet("""
            background-color: #34495e;
            border-radius: 32px;
            padding: 5px;
        """)
        
        if self.personnel_data:
            initials = f"{self.personnel_data['first_name'][0]}{self.personnel_data['last_name'][0]}"
            avatar_label.setText(initials)
            avatar_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            avatar_label.setFont(QFont("Arial", 20, QFont.Weight.Bold))
        
        header_layout.addWidget(avatar_label)
        
        # Add personnel info
        info_layout = QVBoxLayout()
        
        if self.personnel_data:
            name_label = QLabel(f"{self.personnel_data['first_name']} {self.personnel_data['last_name']}")
            name_label.setFont(QFont("Arial", 16, QFont.Weight.Bold))
            
            role_label = QLabel(f"{self.personnel_data['role']} - {self.personnel_data['access_level']} Access")
            role_label.setFont(QFont("Arial", 12))
            
            info_layout.addWidget(name_label)
            info_layout.addWidget(role_label)
        else:
            name_label = QLabel("Welcome")
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
        
        # Create content widget
        content = QWidget()
        content_layout = QVBoxLayout(content)
        
        # Statistics section
        stats_widget = QWidget()
        stats_layout = QHBoxLayout(stats_widget)
        
        # Create stat boxes
        self.total_items_box = self.create_stat_box("Total Items", "0", "#3498db")
        self.low_stock_box = self.create_stat_box("Low Stock Items", "0", "#e74c3c")
        self.pending_orders_box = self.create_stat_box("Pending Orders", "0", "#f39c12")
        self.total_value_box = self.create_stat_box("Total Value", "$0.00", "#2ecc71")
        
        stats_layout.addWidget(self.total_items_box)
        stats_layout.addWidget(self.low_stock_box)
        stats_layout.addWidget(self.pending_orders_box)
        stats_layout.addWidget(self.total_value_box)
        
        content_layout.addWidget(stats_widget)
        
        # Recent activities section
        activities_label = QLabel("Recent Activities")
        activities_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        content_layout.addWidget(activities_label)
        
        self.activities_table = QTableWidget()
        self.activities_table.setColumnCount(4)
        self.activities_table.setHorizontalHeaderLabels([
            "Date", "Type", "Description", "Status"
        ])
        content_layout.addWidget(self.activities_table)
        
        # Low stock alerts section
        alerts_label = QLabel("Low Stock Alerts")
        alerts_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        content_layout.addWidget(alerts_label)
        
        self.alerts_table = QTableWidget()
        self.alerts_table.setColumnCount(5)
        self.alerts_table.setHorizontalHeaderLabels([
            "Item Code", "Name", "Current Stock", "Min Stock", "Status"
        ])
        content_layout.addWidget(self.alerts_table)
        
        scroll.setWidget(content)
        layout.addWidget(scroll)
        
        self.tab_widget.addTab(dashboard_widget, "Dashboard")
    
    def create_stat_box(self, title, value, color="#2196F3"):
        """Create a statistics box widget"""
        box = QFrame()
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
        title_label.setStyleSheet("font-size: 14px;")
        
        value_label = QLabel(value)
        value_label.setStyleSheet("font-size: 24px; font-weight: bold;")
        
        layout.addWidget(title_label)
        layout.addWidget(value_label)
        
        return box
    
    def setup_inventory_tab(self):
        """Setup the inventory management tab"""
        inventory_tab = QWidget()
        layout = QVBoxLayout(inventory_tab)
        
        # Search and filter section
        filter_widget = QWidget()
        filter_layout = QHBoxLayout(filter_widget)
        
        self.inventory_search = QLineEdit()
        self.inventory_search.setPlaceholderText("Search by item code, name, category...")
        self.inventory_search.textChanged.connect(self.filter_inventory)
        
        self.category_filter = QComboBox()
        self.category_filter.addItem("All Categories")
        # We'll populate categories from database in refresh_inventory
        self.category_filter.currentTextChanged.connect(self.filter_inventory)
        
        self.stock_status_filter = QComboBox()
        self.stock_status_filter.addItems(["All Status", "In Stock", "Low Stock", "Out of Stock"])
        self.stock_status_filter.currentTextChanged.connect(self.filter_inventory)
        
        filter_layout.addWidget(QLabel("Search:"))
        filter_layout.addWidget(self.inventory_search, 3)  # Give search more space
        filter_layout.addWidget(QLabel("Category:"))
        filter_layout.addWidget(self.category_filter)
        filter_layout.addWidget(QLabel("Status:"))
        filter_layout.addWidget(self.stock_status_filter)
        
        layout.addWidget(filter_widget)
        
        # Inventory table
        self.inventory_table = QTableWidget()
        self.inventory_table.setColumnCount(10)
        self.inventory_table.setHorizontalHeaderLabels([
            "Item Code", "Name", "Category", "Quantity", "Unit",
            "Location", "Min Qty", "Reorder Point", "Unit Cost", "Actions"
        ])
        self.inventory_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.inventory_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        
        layout.addWidget(self.inventory_table)
        
        # Button bar
        button_bar = QWidget()
        button_layout = QHBoxLayout(button_bar)
        
        add_item_btn = QPushButton("Add Item")
        add_item_btn.clicked.connect(self.show_add_item_dialog)
        
        update_qty_btn = QPushButton("Update Quantity")
        update_qty_btn.clicked.connect(self.show_update_quantity_dialog)
        
        export_btn = QPushButton("Export Inventory")
        export_btn.clicked.connect(self.export_inventory)
        
        refresh_btn = QPushButton("Refresh")
        refresh_btn.clicked.connect(self.refresh_inventory)
        
        button_layout.addWidget(add_item_btn)
        button_layout.addWidget(update_qty_btn)
        button_layout.addWidget(export_btn)
        button_layout.addWidget(refresh_btn)
        button_layout.addStretch()
        
        layout.addWidget(button_bar)
        
        self.tab_widget.addTab(inventory_tab, "Inventory")

    def setup_purchase_orders_tab(self):
        """Setup the purchase orders management tab"""
        po_tab = QWidget()
        layout = QVBoxLayout(po_tab)
        
        # Filter section
        filter_widget = QWidget()
        filter_layout = QHBoxLayout(filter_widget)
        
        self.po_search = QLineEdit()
        self.po_search.setPlaceholderText("Search purchase orders...")
        self.po_search.textChanged.connect(self.filter_purchase_orders)
        
        self.po_status_filter = QComboBox()
        self.po_status_filter.addItems(["All", "Pending", "Approved", "Received", "Cancelled"])
        self.po_status_filter.currentTextChanged.connect(self.filter_purchase_orders)
        
        filter_layout.addWidget(QLabel("Search:"))
        filter_layout.addWidget(self.po_search, 3)
        filter_layout.addWidget(QLabel("Status:"))
        filter_layout.addWidget(self.po_status_filter)
        
        layout.addWidget(filter_widget)
        
        # Purchase orders table
        self.po_table = QTableWidget()
        self.po_table.setColumnCount(8)
        self.po_table.setHorizontalHeaderLabels([
            "PO Number", "Supplier", "Date Created", "Expected Delivery", 
            "Total Amount", "Status", "Created By", "Actions"
        ])
        self.po_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.po_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        
        layout.addWidget(self.po_table)
        
        # Button bar
        button_bar = QWidget()
        button_layout = QHBoxLayout(button_bar)
        
        create_po_btn = QPushButton("Create Purchase Order")
        create_po_btn.clicked.connect(self.show_create_po_dialog)
        
        receive_po_btn = QPushButton("Receive Items")
        receive_po_btn.clicked.connect(self.show_receive_po_dialog)
        
        refresh_po_btn = QPushButton("Refresh")
        refresh_po_btn.clicked.connect(self.refresh_purchase_orders)
        
        button_layout.addWidget(create_po_btn)
        button_layout.addWidget(receive_po_btn)
        button_layout.addWidget(refresh_po_btn)
        button_layout.addStretch()
        
        layout.addWidget(button_bar)
        
        self.tab_widget.addTab(po_tab, "Purchase Orders")

    def setup_reports_tab(self):
        """Setup the reports tab"""
        reports_tab = QWidget()
        layout = QVBoxLayout(reports_tab)
        
        # Create a scrollable area for report options
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        
        content = QWidget()
        content_layout = QVBoxLayout(content)
        
        # Add title
        title_label = QLabel("Inventory Reports")
        title_label.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        content_layout.addWidget(title_label)
        
        # Reports section
        reports_frame = QFrame()
        reports_frame.setFrameShape(QFrame.Shape.StyledPanel)
        reports_frame.setFrameShadow(QFrame.Shadow.Raised)
        reports_frame.setStyleSheet("""
            QFrame {
                background-color: #f5f5f5;
                border-radius: 8px;
                padding: 15px;
            }
        """)
        
        reports_layout = QVBoxLayout(reports_frame)
        
        # Inventory status report
        status_report_btn = QPushButton("Inventory Status Report")
        status_report_btn.clicked.connect(lambda: self.generate_report("inventory_status"))
        reports_layout.addWidget(status_report_btn)
        
        # Low stock report
        low_stock_report_btn = QPushButton("Low Stock Report")
        low_stock_report_btn.clicked.connect(lambda: self.generate_report("low_stock"))
        reports_layout.addWidget(low_stock_report_btn)
        
        # Inventory valuation report
        valuation_report_btn = QPushButton("Inventory Valuation Report")
        valuation_report_btn.clicked.connect(lambda: self.generate_report("valuation"))
        reports_layout.addWidget(valuation_report_btn)
        
        # Inventory movement report
        movement_report_btn = QPushButton("Inventory Movement Report")
        movement_report_btn.clicked.connect(lambda: self.generate_report("movement"))
        reports_layout.addWidget(movement_report_btn)
        
        # Purchase order report
        po_report_btn = QPushButton("Purchase Order Report")
        po_report_btn.clicked.connect(lambda: self.generate_report("purchase_orders"))
        reports_layout.addWidget(po_report_btn)
        
        # Custom report
        custom_report_btn = QPushButton("Custom Report")
        custom_report_btn.clicked.connect(lambda: self.generate_report("custom"))
        reports_layout.addWidget(custom_report_btn)
        
        content_layout.addWidget(reports_frame)
        
        # Recent reports section
        recent_title = QLabel("Recent Reports")
        recent_title.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        content_layout.addWidget(recent_title)
        
        self.recent_reports_table = QTableWidget()
        self.recent_reports_table.setColumnCount(4)
        self.recent_reports_table.setHorizontalHeaderLabels([
            "Date", "Report Type", "Generated By", "Actions"
        ])
        content_layout.addWidget(self.recent_reports_table)
        
        scroll.setWidget(content)
        layout.addWidget(scroll)
        
        self.tab_widget.addTab(reports_tab, "Reports")

    def refresh_data(self):
        """Refresh all data in the portal"""
        if not self.personnel_id:
            return
        
        self.refresh_dashboard()
        self.refresh_inventory()
        self.refresh_purchase_orders()
        
        self.status_bar.showMessage(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    def show_notifications(self):
        """Show notifications dialog"""
        dialog = NotificationsDialog(self.personnel_id, self.db_manager, self)
        dialog.exec()
    
    def logout(self):
        """Handle logout"""
        reply = QMessageBox.question(
            self, "Logout", 
            "Are you sure you want to logout?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.close()

    def refresh_dashboard(self):
        """Refresh dashboard with latest data"""
        try:
            # Get inventory statistics
            items = self.db_manager.get_inventory_items()
            
            # Calculate statistics
            total_items = len(items)
            total_value = sum(float(item.get('quantity', 0)) * float(item.get('unit_cost', 0)) for item in items)
            low_stock_items = len([item for item in items if item.get('quantity', 0) <= item.get('minimum_quantity', 0)])
            
            # Get pending purchase orders
            purchase_orders = self.db_manager.get_purchase_orders(status="Pending")
            pending_orders = len(purchase_orders)
            
            # Update stat boxes
            self.update_stat_box(self.total_items_box, total_items)
            self.update_stat_box(self.low_stock_box, low_stock_items)
            self.update_stat_box(self.pending_orders_box, pending_orders)
            self.update_stat_box(self.total_value_box, f"${total_value:.2f}")
            
            # Refresh activities table
            self.refresh_activities()
            
            # Refresh alerts table
            self.refresh_alerts()
        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                f"Error refreshing dashboard: {str(e)}"
            )

    def update_stat_box(self, box, value):
        """Update the value in a stat box"""
        # Find the value label (second label in the box)
        value_label = box.findChild(QLabel, "", options=Qt.FindChildOption.FindChildrenRecursively)
        if value_label and hasattr(value_label, 'text'):
            value_label.setText(str(value))

    def refresh_activities(self):
        """Refresh recent activities table"""
        self.activities_table.setRowCount(0)
        
        # Get recent inventory transactions
        activities = self.db_manager.get_recent_inventory_activities()
        
        for row, activity in enumerate(activities):
            self.activities_table.insertRow(row)
            
            # Format date
            date_item = QTableWidgetItem(activity['date'].strftime('%Y-%m-%d %H:%M') if hasattr(activity['date'], 'strftime') else str(activity['date']))
            
            self.activities_table.setItem(row, 0, date_item)
            self.activities_table.setItem(row, 1, QTableWidgetItem(activity['type']))
            self.activities_table.setItem(row, 2, QTableWidgetItem(activity['description']))
            self.activities_table.setItem(row, 3, QTableWidgetItem(activity['status']))

    def refresh_alerts(self):
        """Refresh low stock alerts table"""
        self.alerts_table.setRowCount(0)
        
        # Get inventory items
        items = self.db_manager.get_inventory_items()
        
        # Filter to low stock items
        low_stock_items = [item for item in items if item.get('quantity', 0) <= item.get('minimum_quantity', 0)]
        
        for row, item in enumerate(low_stock_items):
            self.alerts_table.insertRow(row)
            
            # Determine status
            if item.get('quantity', 0) <= 0:
                status = "Out of Stock"
                status_color = QColor("#f44336")  # Red
            else:
                status = "Low Stock"
                status_color = QColor("#ff9800")  # Orange
            
            self.alerts_table.setItem(row, 0, QTableWidgetItem(item.get('item_code', '')))
            self.alerts_table.setItem(row, 1, QTableWidgetItem(item.get('name', '')))
            self.alerts_table.setItem(row, 2, QTableWidgetItem(str(item.get('quantity', 0))))
            self.alerts_table.setItem(row, 3, QTableWidgetItem(str(item.get('minimum_quantity', 0))))
            
            # Set status with color
            status_item = QTableWidgetItem(status)
            status_item.setBackground(status_color)
            self.alerts_table.setItem(row, 4, status_item)

    def refresh_inventory(self):
        """Refresh inventory table with latest data"""
        self.inventory_table.setRowCount(0)
        
        # Get inventory items
        items = self.db_manager.get_inventory_items()
        
        # Get categories for filter
        categories = self.db_manager.get_inventory_categories()
        
        # Update category filter while preserving current selection
        current_category = self.category_filter.currentText()
        self.category_filter.clear()
        self.category_filter.addItem("All Categories")
        
        category_names = [category['name'] for category in categories]
        self.category_filter.addItems(category_names)
        
        # Restore previous selection if it still exists
        index = self.category_filter.findText(current_category)
        if index >= 0:
            self.category_filter.setCurrentIndex(index)
        
        # Populate inventory table
        for row, item in enumerate(items):
            self.inventory_table.insertRow(row)
            
            self.inventory_table.setItem(row, 0, QTableWidgetItem(item.get('item_code', '')))
            self.inventory_table.setItem(row, 1, QTableWidgetItem(item.get('name', '')))
            self.inventory_table.setItem(row, 2, QTableWidgetItem(item.get('category', '')))
            
            # Set quantity with color based on stock level
            quantity = int(item.get('quantity', 0))
            min_quantity = int(item.get('minimum_quantity', 0))
            quantity_item = QTableWidgetItem(str(quantity))
            
            if quantity <= 0:
                quantity_item.setBackground(QColor("#f44336"))  # Red for out of stock
            elif quantity <= min_quantity:
                quantity_item.setBackground(QColor("#ff9800"))  # Orange for low stock
            
            self.inventory_table.setItem(row, 3, quantity_item)
            
            self.inventory_table.setItem(row, 4, QTableWidgetItem(item.get('unit', '')))
            self.inventory_table.setItem(row, 5, QTableWidgetItem(item.get('location', '')))
            self.inventory_table.setItem(row, 6, QTableWidgetItem(str(item.get('minimum_quantity', 0))))
            self.inventory_table.setItem(row, 7, QTableWidgetItem(str(item.get('reorder_point', 0))))
            self.inventory_table.setItem(row, 8, QTableWidgetItem(f"${float(item.get('unit_cost', 0)):.2f}"))
            
            # Add actions buttons
            actions_widget = QWidget()
            actions_layout = QHBoxLayout(actions_widget)
            actions_layout.setContentsMargins(2, 2, 2, 2)
            
            edit_btn = QPushButton("Edit")
            edit_btn.setProperty("item_id", item.get('item_id'))
            edit_btn.clicked.connect(lambda _, btn=edit_btn: self.show_edit_item_dialog(btn.property("item_id")))
            
            details_btn = QPushButton("Details")
            details_btn.setProperty("item_id", item.get('item_id'))
            details_btn.clicked.connect(lambda _, btn=details_btn: self.show_item_details(btn.property("item_id")))
            
            actions_layout.addWidget(edit_btn)
            actions_layout.addWidget(details_btn)
            
            self.inventory_table.setCellWidget(row, 9, actions_widget)

    def filter_inventory(self):
        """Filter inventory based on search text and filters"""
        search_text = self.inventory_search.text().lower()
        category = self.category_filter.currentText()
        status = self.stock_status_filter.currentText()
        
        for row in range(self.inventory_table.rowCount()):
            show_row = True
            
            # Check search text
            if search_text:
                match_found = False
                for col in [0, 1, 2, 4, 5]:  # Check item code, name, category, unit, location
                    item = self.inventory_table.item(row, col)
                    if item and search_text in item.text().lower():
                        match_found = True
                        break
                if not match_found:
                    show_row = False
            
            # Check category filter
            if category != "All Categories" and show_row:
                item = self.inventory_table.item(row, 2)  # Category column
                if item and item.text() != category:
                    show_row = False
            
            # Check status filter
            if status != "All Status" and show_row:
                quantity_item = self.inventory_table.item(row, 3)  # Quantity column
                min_quantity_item = self.inventory_table.item(row, 6)  # Min quantity column
                
                if quantity_item and min_quantity_item:
                    quantity = int(quantity_item.text())
                    min_quantity = int(min_quantity_item.text())
                    
                    item_status = "In Stock"
                    if quantity <= 0:
                        item_status = "Out of Stock"
                    elif quantity <= min_quantity:
                        item_status = "Low Stock"
                    
                    if item_status != status:
                        show_row = False
            
            self.inventory_table.setRowHidden(row, not show_row)

    def refresh_purchase_orders(self):
        """Refresh purchase orders table"""
        self.po_table.setRowCount(0)
        
        # Get purchase orders
        purchase_orders = self.db_manager.get_purchase_orders()
        
        for row, po in enumerate(purchase_orders):
            self.po_table.insertRow(row)
            
            self.po_table.setItem(row, 0, QTableWidgetItem(po.get('po_number', '')))
            self.po_table.setItem(row, 1, QTableWidgetItem(po.get('supplier_name', '')))
            
            # Format dates
            created_date = QTableWidgetItem(po['created_at'].strftime('%Y-%m-%d') if hasattr(po['created_at'], 'strftime') else str(po.get('created_at', '')))
            expected_date = QTableWidgetItem(po['expected_delivery'].strftime('%Y-%m-%d') if hasattr(po['expected_delivery'], 'strftime') else str(po.get('expected_delivery', '')))
            
            self.po_table.setItem(row, 2, created_date)
            self.po_table.setItem(row, 3, expected_date)
            self.po_table.setItem(row, 4, QTableWidgetItem(f"${float(po.get('total_amount', 0)):.2f}"))
            
            # Status with color
            status_item = QTableWidgetItem(po.get('status', ''))
            if po.get('status') == 'Pending':
                status_item.setBackground(QColor("#ffeb3b"))  # Yellow
            elif po.get('status') == 'Approved':
                status_item.setBackground(QColor("#2196f3"))  # Blue
            elif po.get('status') == 'Received':
                status_item.setBackground(QColor("#4caf50"))  # Green
            elif po.get('status') == 'Cancelled':
                status_item.setBackground(QColor("#f44336"))  # Red
            
            self.po_table.setItem(row, 5, status_item)
            self.po_table.setItem(row, 6, QTableWidgetItem(po.get('created_by_name', '')))
            
            # Add actions buttons
            actions_widget = QWidget()
            actions_layout = QHBoxLayout(actions_widget)
            actions_layout.setContentsMargins(2, 2, 2, 2)
            
            view_btn = QPushButton("View")
            view_btn.setProperty("po_id", po.get('po_id'))
            view_btn.clicked.connect(lambda _, btn=view_btn: self.show_po_details(btn.property("po_id")))
            
            # Add update status button for non-completed purchase orders
            if po.get('status') not in ['Received', 'Cancelled']:
                update_btn = QPushButton("Update")
                update_btn.setProperty("po_id", po.get('po_id'))
                update_btn.clicked.connect(lambda _, btn=update_btn: self.show_update_po_dialog(btn.property("po_id")))
                actions_layout.addWidget(update_btn)
            
            actions_layout.addWidget(view_btn)
            
            self.po_table.setCellWidget(row, 7, actions_widget)

    def filter_purchase_orders(self):
        """Filter purchase orders based on search and status"""
        search_text = self.po_search.text().lower()
        status_filter = self.po_status_filter.currentText()
        
        for row in range(self.po_table.rowCount()):
            show_row = True
            
            # Check search text
            if search_text:
                match_found = False
                for col in [0, 1, 6]:  # Check PO number, supplier, created by
                    item = self.po_table.item(row, col)
                    if item and search_text in item.text().lower():
                        match_found = True
                        break
                if not match_found:
                    show_row = False
            
            # Check status filter
            if status_filter != "All" and show_row:
                status_item = self.po_table.item(row, 5)  # Status column
                if status_item and status_item.text() != status_filter:
                    show_row = False
            
            self.po_table.setRowHidden(row, not show_row)

    def show_add_item_dialog(self):
        """Show dialog to add a new inventory item"""
        pass  # Will be implemented later

    def show_edit_item_dialog(self, item_id):
        """Show dialog to edit an inventory item"""
        pass  # Will be implemented later

    def show_item_details(self, item_id):
        """Show dialog with item details"""
        pass  # Will be implemented later

    def show_update_quantity_dialog(self):
        """Show dialog to update item quantity"""
        pass  # Will be implemented later

    def export_inventory(self):
        """Export inventory to CSV file"""
        pass  # Will be implemented later

    def show_create_po_dialog(self):
        """Show dialog to create a new purchase order"""
        pass  # Will be implemented later

    def show_receive_po_dialog(self):
        """Show dialog to receive items from a purchase order"""
        pass  # Will be implemented later

    def show_po_details(self, po_id):
        """Show purchase order details"""
        pass  # Will be implemented later

    def show_update_po_dialog(self, po_id):
        """Show dialog to update purchase order status"""
        pass  # Will be implemented later

    def generate_report(self, report_type):
        """Generate and display a report"""
        pass  # Will be implemented later

class NotificationsDialog(QDialog):
    """Dialog to display notifications for inventory personnel"""
    
    def __init__(self, personnel_id, db_manager, parent=None):
        super().__init__(parent)
        self.personnel_id = personnel_id
        self.db_manager = db_manager
        
        self.setWindowTitle("Notifications")
        self.setMinimumSize(500, 400)
        
        layout = QVBoxLayout(self)
        
        # Notifications list
        self.notifications_list = QListWidget()
        layout.addWidget(self.notifications_list)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        mark_read_btn = QPushButton("Mark All as Read")
        mark_read_btn.clicked.connect(self.mark_all_read)
        
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        
        button_layout.addWidget(mark_read_btn)
        button_layout.addStretch()
        button_layout.addWidget(close_btn)
        
        layout.addLayout(button_layout)
        
        # Load notifications
        self.load_notifications()
    
    def load_notifications(self):
        """Load notifications for this personnel"""
        self.notifications_list.clear()
        
        # Get notifications from database
        notifications = self.db_manager.get_inventory_personnel_notifications(self.personnel_id)
        
        # Add notifications to list widget
        for notification in notifications:
            item = QListWidgetItem()
            
            # Set icon based on notification type
            if notification['priority'] == 'high':
                item.setIcon(QIcon("icons/alert.png"))
            elif notification['priority'] == 'medium':
                item.setIcon(QIcon("icons/warning.png"))
            else:
                item.setIcon(QIcon("icons/info.png"))
            
            # Format date if it's a datetime object
            date_str = notification['date'].strftime('%Y-%m-%d %H:%M') if hasattr(notification['date'], 'strftime') else str(notification['date'])
            
            # Set text
            item.setText(f"{date_str} - {notification['message']}")
            
            # Set background color for unread notifications
            if not notification['read']:
                item.setBackground(QColor("#f0f8ff"))  # Light blue background
            
            # Store notification ID
            item.setData(Qt.UserRole, notification['notification_id'])
            
            self.notifications_list.addItem(item)
    
    def mark_all_read(self):
        """Mark all notifications as read"""
        if self.db_manager.mark_personnel_notifications_read(self.personnel_id):
            self.load_notifications()  # Refresh the list

# Add this to your main.py or wherever you handle application startup
if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # For testing purposes
    from db_ops.db_manager import DatabaseManager
    db_manager = DatabaseManager()
    
    # Show login dialog
    login_dialog = InventoryPersonnelLoginDialog(db_manager)
    if login_dialog.exec() == QDialog.Accepted:
        personnel_id = login_dialog.get_personnel_id()
        portal = InventoryPersonnelPortal(db_manager, personnel_id)
        portal.show()
        sys.exit(app.exec()) 