from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                              QPushButton, QLabel, QTabWidget, QLineEdit,
                              QComboBox, QSpinBox, QDoubleSpinBox, QTableWidget,
                              QTableWidgetItem, QDialog, QFormLayout, QMessageBox,
                              QScrollArea, QSplitter, QTextEdit, QMenuBar, QMenu,
                              QStatusBar, QDateEdit, QCheckBox, QFrame)
from PySide6.QtCore import Qt, Signal, QDate, QDateTime
from PySide6.QtGui import QAction, QIcon
from datetime import datetime, timedelta
import json

class InventoryWindow(QMainWindow):
    def __init__(self, db_manager, parent=None):
        super().__init__(parent)
        self.db_manager = db_manager
        self.setWindowTitle("Inventory Management")
        
        # Create central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        self.main_layout = QVBoxLayout(central_widget)
        
        # Create tab widget
        self.tab_widget = QTabWidget()
        self.main_layout.addWidget(self.tab_widget)
        
        # Setup tabs
        self.setup_dashboard_tab()
        self.setup_inventory_tab()
        self.setup_tools_tab()
        self.setup_transactions_tab()
        self.setup_suppliers_tab()
        
        # Setup menu bar
        self.setup_menu_bar()
        
        # Setup status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        
        # Load initial data
        self.refresh_data()

    def setup_dashboard_tab(self):
        """Setup the dashboard with overview and alerts"""
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        
        content = QWidget()
        layout = QVBoxLayout(content)
        
        # Statistics section
        stats_widget = QWidget()
        stats_layout = QHBoxLayout(stats_widget)
        
        # Total items box
        self.total_items_label = self.create_stat_box("Total Items", "0")
        
        # Low stock items box
        self.low_stock_label = self.create_stat_box("Low Stock Items", "0", "#F44336")
        
        # Items to reorder box
        self.reorder_label = self.create_stat_box("Items to Reorder", "0", "#FF9800")
        
        # Total value box
        self.total_value_label = self.create_stat_box("Total Value", "$0.00", "#4CAF50")
        
        stats_layout.addWidget(self.total_items_label)
        stats_layout.addWidget(self.low_stock_label)
        stats_layout.addWidget(self.reorder_label)
        stats_layout.addWidget(self.total_value_label)
        
        layout.addWidget(stats_widget)
        
        # Alerts section
        alerts_label = QLabel("Alerts and Notifications")
        alerts_label.setStyleSheet("font-size: 14px; font-weight: bold;")
        layout.addWidget(alerts_label)
        
        self.alerts_table = QTableWidget()
        self.alerts_table.setColumnCount(4)
        self.alerts_table.setHorizontalHeaderLabels([
            "Priority", "Type", "Message", "Date"
        ])
        layout.addWidget(self.alerts_table)
        
        # Recent transactions section
        transactions_label = QLabel("Recent Transactions")
        transactions_label.setStyleSheet("font-size: 14px; font-weight: bold;")
        layout.addWidget(transactions_label)
        
        self.recent_transactions_table = QTableWidget()
        self.recent_transactions_table.setColumnCount(6)
        self.recent_transactions_table.setHorizontalHeaderLabels([
            "Date", "Item", "Type", "Quantity", "Reference", "Performed By"
        ])
        layout.addWidget(self.recent_transactions_table)
        
        scroll.setWidget(content)
        self.tab_widget.addTab(scroll, "Dashboard")

    def setup_inventory_tab(self):
        """Setup the main inventory management tab"""
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        
        content = QWidget()
        layout = QVBoxLayout(content)
        
        # Search and filter section
        filter_widget = QWidget()
        filter_layout = QHBoxLayout(filter_widget)
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search inventory...")
        
        self.category_filter = QComboBox()
        self.category_filter.addItem("All Categories")
        
        self.status_filter = QComboBox()
        self.status_filter.addItems(["All Status", "Active", "Inactive", "Low Stock"])
        
        filter_layout.addWidget(QLabel("Search:"))
        filter_layout.addWidget(self.search_input)
        filter_layout.addWidget(QLabel("Category:"))
        filter_layout.addWidget(self.category_filter)
        filter_layout.addWidget(QLabel("Status:"))
        filter_layout.addWidget(self.status_filter)
        
        layout.addWidget(filter_widget)
        
        # Inventory table
        self.inventory_table = QTableWidget()
        self.inventory_table.setColumnCount(10)
        self.inventory_table.setHorizontalHeaderLabels([
            "Item Code", "Name", "Category", "Quantity", "Unit",
            "Location", "Min Qty", "Reorder Point", "Unit Cost", "Total Value"
        ])
        layout.addWidget(self.inventory_table)
        
        # Buttons
        button_widget = QWidget()
        button_layout = QHBoxLayout(button_widget)
        
        add_item_btn = QPushButton("Add New Item")
        add_item_btn.clicked.connect(self.show_add_item_dialog)
        
        import_btn = QPushButton("Import Items")
        import_btn.clicked.connect(self.import_items)
        
        export_btn = QPushButton("Export Items")
        export_btn.clicked.connect(self.export_items)
        
        refresh_btn = QPushButton("Refresh")
        refresh_btn.clicked.connect(self.refresh_inventory)
        
        button_layout.addWidget(add_item_btn)
        button_layout.addWidget(import_btn)
        button_layout.addWidget(export_btn)
        button_layout.addWidget(refresh_btn)
        
        layout.addWidget(button_widget)
        
        scroll.setWidget(content)
        self.tab_widget.addTab(scroll, "Inventory")

    def setup_tools_tab(self):
        """Setup the tools management tab"""
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        
        content = QWidget()
        layout = QVBoxLayout(content)
        
        # Tools table
        self.tools_table = QTableWidget()
        self.tools_table.setColumnCount(8)
        self.tools_table.setHorizontalHeaderLabels([
            "Tool ID", "Name", "Status", "Location", "Checked Out To",
            "Checkout Date", "Expected Return", "Notes"
        ])
        layout.addWidget(self.tools_table)
        
        # Buttons
        button_widget = QWidget()
        button_layout = QHBoxLayout(button_widget)
        
        checkout_btn = QPushButton("Check Out Tool")
        checkout_btn.clicked.connect(self.show_checkout_dialog)
        
        checkin_btn = QPushButton("Check In Tool")
        checkin_btn.clicked.connect(self.show_checkin_dialog)
        
        add_tool_btn = QPushButton("Add New Tool")
        add_tool_btn.clicked.connect(self.show_add_tool_dialog)
        
        button_layout.addWidget(checkout_btn)
        button_layout.addWidget(checkin_btn)
        button_layout.addWidget(add_tool_btn)
        
        layout.addWidget(button_widget)
        
        scroll.setWidget(content)
        self.tab_widget.addTab(scroll, "Tools")

    def setup_transactions_tab(self):
        """Setup the transactions history tab"""
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        
        content = QWidget()
        layout = QVBoxLayout(content)
        
        # Date range filter
        date_widget = QWidget()
        date_layout = QHBoxLayout(date_widget)
        
        self.date_from = QDateEdit()
        self.date_from.setCalendarPopup(True)
        self.date_from.setDate(QDate.currentDate().addMonths(-1))
        
        self.date_to = QDateEdit()
        self.date_to.setCalendarPopup(True)
        self.date_to.setDate(QDate.currentDate())
        
        self.transaction_type_filter = QComboBox()
        self.transaction_type_filter.addItems([
            "All Types", "IN", "OUT", "ADJUST"
        ])
        
        date_layout.addWidget(QLabel("From:"))
        date_layout.addWidget(self.date_from)
        date_layout.addWidget(QLabel("To:"))
        date_layout.addWidget(self.date_to)
        date_layout.addWidget(QLabel("Type:"))
        date_layout.addWidget(self.transaction_type_filter)
        
        layout.addWidget(date_widget)
        
        # Transactions table
        self.transactions_table = QTableWidget()
        self.transactions_table.setColumnCount(9)
        self.transactions_table.setHorizontalHeaderLabels([
            "Date", "Item", "Type", "Quantity", "Unit Cost",
            "Total Cost", "Reference", "Work Order", "Performed By"
        ])
        layout.addWidget(self.transactions_table)
        
        # Buttons
        button_widget = QWidget()
        button_layout = QHBoxLayout(button_widget)
        
        add_transaction_btn = QPushButton("Add Transaction")
        add_transaction_btn.clicked.connect(self.show_add_transaction_dialog)
        
        export_transactions_btn = QPushButton("Export Transactions")
        export_transactions_btn.clicked.connect(self.export_transactions)
        
        button_layout.addWidget(add_transaction_btn)
        button_layout.addWidget(export_transactions_btn)
        
        layout.addWidget(button_widget)
        
        scroll.setWidget(content)
        self.tab_widget.addTab(scroll, "Transactions")

    def setup_suppliers_tab(self):
        """Setup the suppliers management tab"""
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        
        content = QWidget()
        layout = QVBoxLayout(content)
        
        # Suppliers table
        self.suppliers_table = QTableWidget()
        self.suppliers_table.setColumnCount(7)
        self.suppliers_table.setHorizontalHeaderLabels([
            "Name", "Contact Person", "Phone", "Email",
            "Address", "Status", "Notes"
        ])
        layout.addWidget(self.suppliers_table)
        
        # Buttons
        button_widget = QWidget()
        button_layout = QHBoxLayout(button_widget)
        
        add_supplier_btn = QPushButton("Add Supplier")
        add_supplier_btn.clicked.connect(self.show_add_supplier_dialog)
        
        edit_supplier_btn = QPushButton("Edit Supplier")
        edit_supplier_btn.clicked.connect(self.show_edit_supplier_dialog)
        
        export_suppliers_btn = QPushButton("Export Suppliers")
        export_suppliers_btn.clicked.connect(self.export_suppliers)
        
        button_layout.addWidget(add_supplier_btn)
        button_layout.addWidget(edit_supplier_btn)
        button_layout.addWidget(export_suppliers_btn)
        
        layout.addWidget(button_widget)
        
        scroll.setWidget(content)
        self.tab_widget.addTab(scroll, "Suppliers")

    def setup_menu_bar(self):
        """Setup the menu bar"""
        menu_bar = self.menuBar()
        
        # File menu
        file_menu = menu_bar.addMenu("File")
        
        import_action = file_menu.addAction("Import Data")
        import_action.triggered.connect(self.import_data)
        
        export_action = file_menu.addAction("Export Data")
        export_action.triggered.connect(self.export_data)
        
        file_menu.addSeparator()
        
        exit_action = file_menu.addAction("Exit")
        exit_action.triggered.connect(self.close)
        
        # Reports menu
        reports_menu = menu_bar.addMenu("Reports")
        
        inventory_report = reports_menu.addAction("Inventory Report")
        inventory_report.triggered.connect(self.generate_inventory_report)
        
        valuation_report = reports_menu.addAction("Valuation Report")
        valuation_report.triggered.connect(self.generate_valuation_report)
        
        movement_report = reports_menu.addAction("Movement Report")
        movement_report.triggered.connect(self.generate_movement_report)
        
        reports_menu.addSeparator()
        
        custom_report = reports_menu.addAction("Custom Report")
        custom_report.triggered.connect(self.generate_custom_report)

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

class AddItemDialog(QDialog):
    def __init__(self, db_manager, parent=None):
        super().__init__(parent)
        self.db_manager = db_manager
        self.setWindowTitle("Add New Item")
        self.setModal(True)
        
        layout = QVBoxLayout(self)
        
        # Create form layout
        form = QFormLayout()
        
        # Item fields
        self.item_code = QLineEdit()
        self.name = QLineEdit()
        self.category = QComboBox()
        self.supplier = QComboBox()
        self.description = QTextEdit()
        self.unit = QLineEdit()
        self.unit_cost = QDoubleSpinBox()
        self.unit_cost.setMaximum(999999.99)
        self.quantity = QSpinBox()
        self.quantity.setMaximum(999999)
        self.min_quantity = QSpinBox()
        self.min_quantity.setMaximum(999999)
        self.reorder_point = QSpinBox()
        self.reorder_point.setMaximum(999999)
        self.location = QLineEdit()
        
        # Load categories and suppliers
        self.load_categories()
        self.load_suppliers()
        
        # Add fields to form
        form.addRow("Item Code*:", self.item_code)
        form.addRow("Name*:", self.name)
        form.addRow("Category:", self.category)
        form.addRow("Supplier:", self.supplier)
        form.addRow("Description:", self.description)
        form.addRow("Unit:", self.unit)
        form.addRow("Unit Cost:", self.unit_cost)
        form.addRow("Quantity:", self.quantity)
        form.addRow("Minimum Quantity:", self.min_quantity)
        form.addRow("Reorder Point:", self.reorder_point)
        form.addRow("Location:", self.location)
        
        layout.addLayout(form)
        
        # Add buttons
        button_box = QHBoxLayout()
        save_btn = QPushButton("Save")
        save_btn.clicked.connect(self.save_item)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        
        button_box.addWidget(save_btn)
        button_box.addWidget(cancel_btn)
        layout.addLayout(button_box)

    def load_categories(self):
        categories = self.db_manager.get_inventory_categories()
        self.category.clear()
        self.category.addItem("Select Category", None)
        for category in categories:
            self.category.addItem(category['name'], category['category_id'])

    def load_suppliers(self):
        suppliers = self.db_manager.get_suppliers()
        self.supplier.clear()
        self.supplier.addItem("Select Supplier", None)
        for supplier in suppliers:
            self.supplier.addItem(supplier['name'], supplier['supplier_id'])

    def save_item(self):
        # Validate required fields
        if not self.item_code.text() or not self.name.text():
            QMessageBox.warning(self, "Validation Error", "Item Code and Name are required!")
            return
        
        # Create item data
        data = {
            'item_code': self.item_code.text(),
            'name': self.name.text(),
            'category_id': self.category.currentData(),
            'supplier_id': self.supplier.currentData(),
            'description': self.description.toPlainText(),
            'unit': self.unit.text(),
            'unit_cost': self.unit_cost.value(),
            'quantity': self.quantity.value(),
            'minimum_quantity': self.min_quantity.value(),
            'reorder_point': self.reorder_point.value(),
            'location': self.location.text()
        }
        
        try:
            if self.db_manager.add_inventory_item(data):
                QMessageBox.information(self, "Success", "Item added successfully!")
                self.accept()
            else:
                QMessageBox.critical(self, "Error", "Failed to add item!")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error adding item: {str(e)}")

class AddTransactionDialog(QDialog):
    def __init__(self, db_manager, parent=None):
        super().__init__(parent)
        self.db_manager = db_manager
        self.setWindowTitle("Add Transaction")
        self.setModal(True)
        
        layout = QVBoxLayout(self)
        
        # Create form layout
        form = QFormLayout()
        
        # Transaction fields
        self.item = QComboBox()
        self.transaction_type = QComboBox()
        self.transaction_type.addItems(["IN", "OUT", "ADJUST"])
        self.quantity = QSpinBox()
        self.quantity.setMaximum(999999)
        self.unit_cost = QDoubleSpinBox()
        self.unit_cost.setMaximum(999999.99)
        self.reference = QLineEdit()
        self.work_order = QComboBox()
        self.notes = QTextEdit()
        
        # Load items and work orders
        self.load_items()
        self.load_work_orders()
        
        # Add fields to form
        form.addRow("Item*:", self.item)
        form.addRow("Type*:", self.transaction_type)
        form.addRow("Quantity*:", self.quantity)
        form.addRow("Unit Cost:", self.unit_cost)
        form.addRow("Reference:", self.reference)
        form.addRow("Work Order:", self.work_order)
        form.addRow("Notes:", self.notes)
        
        layout.addLayout(form)
        
        # Add buttons
        button_box = QHBoxLayout()
        save_btn = QPushButton("Save")
        save_btn.clicked.connect(self.save_transaction)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        
        button_box.addWidget(save_btn)
        button_box.addWidget(cancel_btn)
        layout.addLayout(button_box)

    def load_items(self):
        items = self.db_manager.get_inventory_items()
        self.item.clear()
        self.item.addItem("Select Item", None)
        for item in items:
            self.item.addItem(f"{item['item_code']} - {item['name']}", item['item_id'])

    def load_work_orders(self):
        work_orders = self.db_manager.get_open_work_orders()
        self.work_order.clear()
        self.work_order.addItem("Select Work Order", None)
        for wo in work_orders:
            self.work_order.addItem(f"WO#{wo['work_order_id']} - {wo['title']}", wo['work_order_id'])

    def save_transaction(self):
        # Validate required fields
        if not self.item.currentData():
            QMessageBox.warning(self, "Validation Error", "Please select an item!")
            return
        
        if self.quantity.value() <= 0:
            QMessageBox.warning(self, "Validation Error", "Quantity must be greater than 0!")
            return
        
        # Create transaction data
        data = {
            'item_id': self.item.currentData(),
            'transaction_type': self.transaction_type.currentText(),
            'quantity': self.quantity.value(),
            'unit_cost': self.unit_cost.value(),
            'reference_number': self.reference.text(),
            'work_order_id': self.work_order.currentData(),
            'notes': self.notes.toPlainText()
        }
        
        try:
            if self.db_manager.add_inventory_transaction(data):
                QMessageBox.information(self, "Success", "Transaction added successfully!")
                self.accept()
            else:
                QMessageBox.critical(self, "Error", "Failed to add transaction!")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error adding transaction: {str(e)}")

class AddSupplierDialog(QDialog):
    def __init__(self, db_manager, parent=None):
        super().__init__(parent)
        self.db_manager = db_manager
        self.setWindowTitle("Add Supplier")
        self.setModal(True)
        
        layout = QVBoxLayout(self)
        
        # Create form layout
        form = QFormLayout()
        
        # Supplier fields
        self.name = QLineEdit()
        self.contact_person = QLineEdit()
        self.phone = QLineEdit()
        self.email = QLineEdit()
        self.address = QTextEdit()
        self.notes = QTextEdit()
        
        # Add fields to form
        form.addRow("Name*:", self.name)
        form.addRow("Contact Person:", self.contact_person)
        form.addRow("Phone:", self.phone)
        form.addRow("Email:", self.email)
        form.addRow("Address:", self.address)
        form.addRow("Notes:", self.notes)
        
        layout.addLayout(form)
        
        # Add buttons
        button_box = QHBoxLayout()
        save_btn = QPushButton("Save")
        save_btn.clicked.connect(self.save_supplier)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        
        button_box.addWidget(save_btn)
        button_box.addWidget(cancel_btn)
        layout.addLayout(button_box)

    def save_supplier(self):
        # Validate required fields
        if not self.name.text():
            QMessageBox.warning(self, "Validation Error", "Supplier name is required!")
            return
        
        # Create supplier data
        data = {
            'name': self.name.text(),
            'contact_person': self.contact_person.text(),
            'phone': self.phone.text(),
            'email': self.email.text(),
            'address': self.address.toPlainText(),
            'notes': self.notes.toPlainText()
        }
        
        try:
            if self.db_manager.add_supplier(data):
                QMessageBox.information(self, "Success", "Supplier added successfully!")
                self.accept()
            else:
                QMessageBox.critical(self, "Error", "Failed to add supplier!")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error adding supplier: {str(e)}")
