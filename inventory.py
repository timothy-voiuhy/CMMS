from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                              QPushButton, QLabel, QTabWidget, QLineEdit,
                              QComboBox, QSpinBox, QDoubleSpinBox, QTableWidget,
                              QTableWidgetItem, QDialog, QFormLayout, QMessageBox,
                              QScrollArea, QSplitter, QTextEdit, QMenuBar, QMenu,
                              QStatusBar, QDateEdit, QCheckBox, QFrame, QInputDialog, QFileDialog,
                              QSizePolicy, QHeaderView)
from PySide6.QtCore import Qt, Signal, QDate, QDateTime
from PySide6.QtGui import QAction, QIcon
from datetime import datetime, timedelta
import json
import random
from reporting import (InventoryReport, InventoryValuationReport, 
                      InventoryMovementReport, InventoryCustomReport)
import os
import subprocess

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
        self.setup_suppliers_tab()
        
        # Setup menu bar
        self.setup_menu_bar()
        
        # Setup status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        
        # Load initial data
        self.refresh_data()

    def refresh_data(self):
        """Refresh all data in the window"""
        self.refresh_inventory()
        self.refresh_tools()
        self.refresh_suppliers()
        self.refresh_dashboard()

    def refresh_dashboard(self):
        """Refresh dashboard statistics"""
        try:
            # Get inventory data
            items = self.db_manager.get_inventory_items()
            
            # Calculate statistics
            total_items = len(items)
            total_value = sum(float(item.get('quantity', 0)) * float(item.get('unit_cost', 0)) for item in items)
            low_stock_items = len([item for item in items if item.get('quantity', 0) <= item.get('minimum_quantity', 0)])
            reorder_items = len([item for item in items if item.get('quantity', 0) <= item.get('reorder_point', 0)])
            
            # Update dashboard boxes
            self.total_items_value_label.setText(str(total_items))
            self.low_stock_value_label.setText(str(low_stock_items))
            self.reorder_value_label.setText(str(reorder_items))
            self.total_value_value_label.setText(f"${total_value:.2f}")
            
            # Update alerts table
            self.refresh_alerts()
            
            # Update recent transactions table
            self.refresh_recent_transactions()
            
        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                f"An error occurred while refreshing the dashboard:\n{str(e)}"
            )

    def refresh_alerts(self):
        """Refresh alerts table in dashboard"""
        try:
            # Clear the table
            self.alerts_table.setRowCount(0)
            
            # Get inventory data
            items = self.db_manager.get_inventory_items()
            
            # Add low stock alerts
            for item in items:
                quantity = int(item.get('quantity', 0))
                min_quantity = int(item.get('minimum_quantity', 0))
                reorder_point = int(item.get('reorder_point', 0))
                
                if quantity <= min_quantity:
                    self.add_alert(
                        "High",
                        "Low Stock",
                        f"{item['name']} is below minimum quantity ({quantity} < {min_quantity})",
                        datetime.now()
                    )
                elif quantity <= reorder_point:
                    self.add_alert(
                        "Medium",
                        "Reorder",
                        f"{item['name']} needs to be reordered ({quantity} <= {reorder_point})",
                        datetime.now()
                    )
            
            # Get overdue tools
            tools = self.db_manager.get_inventory_items_by_category('Tool')
            for tool in tools:
                checkout = self.db_manager.get_tool_checkout_status(tool['item_id'])
                if checkout and checkout['expected_return_date'] < datetime.now().date():
                    self.add_alert(
                        "High",
                        "Overdue Tool",
                        f"{tool['name']} is overdue (Expected: {checkout['expected_return_date']})",
                        datetime.now()
                    )
            
            # Resize columns to content
            self.alerts_table.resizeColumnsToContents()
            
        except Exception as e:
            print(f"Error refreshing alerts: {e}")

    def add_alert(self, priority, alert_type, message, date):
        """Add an alert to the alerts table"""
        row_position = self.alerts_table.rowCount()
        self.alerts_table.insertRow(row_position)
        
        self.alerts_table.setItem(row_position, 0, QTableWidgetItem(priority))
        self.alerts_table.setItem(row_position, 1, QTableWidgetItem(alert_type))
        self.alerts_table.setItem(row_position, 2, QTableWidgetItem(message))
        self.alerts_table.setItem(row_position, 3, QTableWidgetItem(date.strftime('%Y-%m-%d %H:%M')))

    def refresh_recent_transactions(self):
        """Refresh recent transactions table in dashboard"""
        try:
            # Clear the table
            self.recent_transactions_table.setRowCount(0)
            
            # Get recent transactions
            transactions = self.db_manager.get_recent_transactions(limit=10)
            
            # Populate the table
            for transaction in transactions:
                row_position = self.recent_transactions_table.rowCount()
                self.recent_transactions_table.insertRow(row_position)
                
                # Get item name
                item = self.db_manager.get_inventory_item(transaction['item_id'])
                item_name = f"{item['item_code']} - {item['name']}" if item else "Unknown Item"
                
                # Get work order info if available
                work_order = None
                if transaction.get('work_order_id'):
                    work_order = self.db_manager.get_work_order_by_id(transaction['work_order_id'])
                work_order_ref = f"WO#{work_order['work_order_id']}" if work_order else ""
                
                # Set transaction data
                self.recent_transactions_table.setItem(row_position, 0, QTableWidgetItem(transaction['transaction_date'].strftime('%Y-%m-%d')))
                self.recent_transactions_table.setItem(row_position, 1, QTableWidgetItem(item_name))
                self.recent_transactions_table.setItem(row_position, 2, QTableWidgetItem(transaction['transaction_type']))
                self.recent_transactions_table.setItem(row_position, 3, QTableWidgetItem(str(transaction['quantity'])))
                self.recent_transactions_table.setItem(row_position, 4, QTableWidgetItem(work_order_ref))
                self.recent_transactions_table.setItem(row_position, 5, QTableWidgetItem(transaction.get('performed_by', '')))
            
            # Resize columns to content
            self.recent_transactions_table.resizeColumnsToContents()
            
        except Exception as e:
            print(f"Error refreshing recent transactions: {e}")

    def setup_dashboard_tab(self):
        """Setup the dashboard with overview and alerts"""
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        
        content = QWidget()
        layout = QVBoxLayout(content)
        
        # Statistics section
        stats_widget = QWidget()
        stats_layout = QHBoxLayout(stats_widget)
        
        # Create stat boxes and store references to their value labels
        box, self.total_items_value_label = self.create_stat_box("Total Items", "0")
        stats_layout.addWidget(box)
        
        box, self.low_stock_value_label = self.create_stat_box("Low Stock Items", "0", "#F44336")
        stats_layout.addWidget(box)
        
        box, self.reorder_value_label = self.create_stat_box("Items to Reorder", "0", "#FF9800")
        stats_layout.addWidget(box)
        
        box, self.total_value_value_label = self.create_stat_box("Total Value", "$0.00", "#4CAF50")
        stats_layout.addWidget(box)
        
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
        
        return box, value_label

    def setup_inventory_tab(self):
        """Setup the main inventory management tab"""
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        
        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setSpacing(10)  # Add some spacing between elements
        
        # Search and filter section
        filter_widget = QWidget()
        filter_layout = QHBoxLayout(filter_widget)
        filter_layout.setContentsMargins(0, 0, 0, 0)  # Remove margins to maximize space
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search by item code, name, category, or location...")
        self.search_input.textChanged.connect(self.filter_inventory)
        
        self.category_filter = QComboBox()
        self.category_filter.addItem("All Categories")
        self.category_filter.currentTextChanged.connect(self.filter_inventory)
        
        self.status_filter = QComboBox()
        self.status_filter.addItems(["All Status", "In Stock", "Low Stock", "Out of Stock"])
        self.status_filter.currentTextChanged.connect(self.filter_inventory)
        
        filter_layout.addWidget(QLabel("Search:"))
        filter_layout.addWidget(self.search_input, 1)  # Give search more space
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
        self.inventory_table.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.inventory_table.horizontalHeader().setStretchLastSection(True)
        self.inventory_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        layout.addWidget(self.inventory_table, 1)  # Give table more vertical space with stretch factor
        
        # Buttons
        button_widget = QWidget()
        button_layout = QHBoxLayout(button_widget)
        button_layout.setContentsMargins(0, 0, 0, 0)  # Remove margins
        
        add_item_btn = QPushButton("Add New Item")
        add_item_btn.clicked.connect(self.show_add_item_dialog)
        
        import_btn = QPushButton("Import Items")
        import_btn.clicked.connect(self.import_items)
        
        export_btn = QPushButton("Export Items")
        export_btn.clicked.connect(self.export_items)
        
        refresh_btn = QPushButton("Refresh")
        refresh_btn.clicked.connect(self.refresh_inventory)
        
        # Add Demo Data button (only for development)
        demo_data_btn = QPushButton("Generate Demo Data")
        demo_data_btn.clicked.connect(self.generate_demo_data)
        demo_data_btn.setStyleSheet("background-color: #FF9800; color: white;")
        
        button_layout.addWidget(add_item_btn)
        button_layout.addWidget(import_btn)
        button_layout.addWidget(export_btn)
        button_layout.addWidget(refresh_btn)
        button_layout.addWidget(demo_data_btn)
        button_layout.addStretch()  # Add stretch to keep buttons left-aligned
        
        layout.addWidget(button_widget)
        
        scroll.setWidget(content)
        self.tab_widget.addTab(scroll, "Inventory")

    def filter_inventory(self):
        """Filter inventory table based on search and filter criteria"""
        search_text = self.search_input.text().lower()
        category = self.category_filter.currentText()
        status = self.status_filter.currentText()
        
        for row in range(self.inventory_table.rowCount()):
            # Get all searchable fields
            item_code = self.inventory_table.item(row, 0).text().lower()
            name = self.inventory_table.item(row, 1).text().lower()
            item_category = self.inventory_table.item(row, 2).text()
            location = self.inventory_table.item(row, 5).text().lower()
            quantity = int(self.inventory_table.item(row, 3).text())
            min_quantity = int(self.inventory_table.item(row, 6).text())
            
            # Check if search text matches any of the fields
            matches_search = any([
                search_text in item_code,
                search_text in name,
                search_text in item_category.lower(),
                search_text in location
            ])
            
            # Check category
            matches_category = category == "All Categories" or category == item_category
            
            # Check status
            item_status = "In Stock"
            if quantity <= 0:
                item_status = "Out of Stock"
            elif quantity <= min_quantity:
                item_status = "Low Stock"
            
            matches_status = status == "All Status" or status == item_status
            
            # Show/hide row based on all criteria
            self.inventory_table.setRowHidden(row, not (matches_search and matches_category and matches_status))

    def setup_tools_tab(self):
        """Setup the tools management tab"""
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        
        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setSpacing(10)
        
        # Tools table
        self.tools_table = QTableWidget()
        self.tools_table.setColumnCount(8)
        self.tools_table.setHorizontalHeaderLabels([
            "Tool ID", "Name", "Status", "Location", "Checked Out To",
            "Checkout Date", "Expected Return", "Notes"
        ])
        self.tools_table.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.tools_table.horizontalHeader().setStretchLastSection(True)
        self.tools_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        layout.addWidget(self.tools_table, 1)  # Give table more vertical space
        
        # Buttons
        button_widget = QWidget()
        button_layout = QHBoxLayout(button_widget)
        button_layout.setContentsMargins(0, 0, 0, 0)
        
        checkout_btn = QPushButton("Check Out Tool")
        checkout_btn.clicked.connect(self.show_checkout_dialog)
        
        checkin_btn = QPushButton("Check In Tool")
        checkin_btn.clicked.connect(self.show_checkin_dialog)
        
        add_tool_btn = QPushButton("Add New Tool")
        add_tool_btn.clicked.connect(self.show_add_tool_dialog)
        
        button_layout.addWidget(checkout_btn)
        button_layout.addWidget(checkin_btn)
        button_layout.addWidget(add_tool_btn)
        button_layout.addStretch()
        
        layout.addWidget(button_widget)
        
        scroll.setWidget(content)
        self.tab_widget.addTab(scroll, "Tools")

    def setup_suppliers_tab(self):
        """Setup the suppliers management tab"""
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        
        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setSpacing(10)
        
        # Suppliers table
        self.suppliers_table = QTableWidget()
        self.suppliers_table.setColumnCount(7)
        self.suppliers_table.setHorizontalHeaderLabels([
            "Name", "Contact Person", "Phone", "Email",
            "Address", "Status", "Notes"
        ])
        self.suppliers_table.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.suppliers_table.horizontalHeader().setStretchLastSection(True)
        self.suppliers_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        layout.addWidget(self.suppliers_table, 1)  # Give table more vertical space
        
        # Buttons
        button_widget = QWidget()
        button_layout = QHBoxLayout(button_widget)
        button_layout.setContentsMargins(0, 0, 0, 0)
        
        add_supplier_btn = QPushButton("Add Supplier")
        add_supplier_btn.clicked.connect(self.show_add_supplier_dialog)
        
        edit_supplier_btn = QPushButton("Edit Supplier")
        edit_supplier_btn.clicked.connect(self.show_edit_supplier_dialog)
        
        export_suppliers_btn = QPushButton("Export Suppliers")
        export_suppliers_btn.clicked.connect(self.export_suppliers)
        
        button_layout.addWidget(add_supplier_btn)
        button_layout.addWidget(edit_supplier_btn)
        button_layout.addWidget(export_suppliers_btn)
        button_layout.addStretch()
        
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

    def show_add_item_dialog(self):
        """Show dialog for adding a new inventory item"""
        dialog = AddItemDialog(self.db_manager, self)
        if dialog.exec() == QDialog.Accepted:
            self.refresh_inventory()

    def refresh_inventory(self):
        """Refresh the inventory table with latest data"""
        # Clear the table
        self.inventory_table.setRowCount(0)
        
        # Get fresh data from database
        items = self.db_manager.get_inventory_items()
        
        # Populate the table
        for item in items:
            row_position = self.inventory_table.rowCount()
            self.inventory_table.insertRow(row_position)
            
            # Calculate total value
            total_value = float(item.get('quantity', 0)) * float(item.get('unit_cost', 0))
            
            # Set item data
            self.inventory_table.setItem(row_position, 0, QTableWidgetItem(str(item.get('item_code', ''))))
            self.inventory_table.setItem(row_position, 1, QTableWidgetItem(str(item.get('name', ''))))
            self.inventory_table.setItem(row_position, 2, QTableWidgetItem(str(item.get('category', ''))))
            self.inventory_table.setItem(row_position, 3, QTableWidgetItem(str(item.get('quantity', 0))))
            self.inventory_table.setItem(row_position, 4, QTableWidgetItem(str(item.get('unit', ''))))
            self.inventory_table.setItem(row_position, 5, QTableWidgetItem(str(item.get('location', ''))))
            self.inventory_table.setItem(row_position, 6, QTableWidgetItem(str(item.get('minimum_quantity', 0))))
            self.inventory_table.setItem(row_position, 7, QTableWidgetItem(str(item.get('reorder_point', 0))))
            self.inventory_table.setItem(row_position, 8, QTableWidgetItem(f"${item.get('unit_cost', 0):.2f}"))
            self.inventory_table.setItem(row_position, 9, QTableWidgetItem(f"${total_value:.2f}"))
        
        # Resize columns to content
        self.inventory_table.resizeColumnsToContents()

    def import_items(self):
        """Import inventory items from a CSV file"""
        from PySide6.QtWidgets import QFileDialog
        import csv
        
        # Show file dialog to select CSV file
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Import Inventory Items",
            "",
            "CSV Files (*.csv);;All Files (*)"
        )
        
        if not file_path:
            return
            
        try:
            with open(file_path, 'r', newline='') as csvfile:
                reader = csv.DictReader(csvfile)
                
                # Validate headers
                required_fields = ['item_code', 'name', 'category', 'quantity', 'unit', 
                                 'minimum_quantity', 'reorder_point', 'unit_cost']
                headers = reader.fieldnames
                
                missing_fields = [field for field in required_fields if field not in headers]
                if missing_fields:
                    QMessageBox.warning(
                        self,
                        "Invalid CSV Format",
                        f"The following required fields are missing: {', '.join(missing_fields)}"
                    )
                    return
                
                # Import items
                success_count = 0
                error_count = 0
                
                for row in reader:
                    try:
                        # Convert numeric fields
                        row['quantity'] = int(row['quantity'])
                        row['minimum_quantity'] = int(row['minimum_quantity'])
                        row['reorder_point'] = int(row['reorder_point'])
                        row['unit_cost'] = float(row['unit_cost'])
                        
                        # Add item to database
                        if self.db_manager.add_inventory_item(row):
                            success_count += 1
                        else:
                            error_count += 1
                    except ValueError as e:
                        error_count += 1
                        print(f"Error importing row: {e}")
                
                # Show results
                QMessageBox.information(
                    self,
                    "Import Results",
                    f"Successfully imported {success_count} items.\n"
                    f"Failed to import {error_count} items."
                )
                
                # Refresh the inventory table
                self.refresh_inventory()
                
        except Exception as e:
            QMessageBox.critical(
                self,
                "Import Error",
                f"An error occurred while importing items:\n{str(e)}"
            )

    def export_items(self):
        """Export inventory items to a CSV file"""
        from PySide6.QtWidgets import QFileDialog
        import csv
        
        # Show file dialog to select save location
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export Inventory Items",
            "",
            "CSV Files (*.csv);;All Files (*)"
        )
        
        if not file_path:
            return
            
        try:
            # Get all inventory items
            items = self.db_manager.get_inventory_items()
            
            # Define fields to export
            fields = ['item_code', 'name', 'category', 'quantity', 'unit',
                     'location', 'minimum_quantity', 'reorder_point', 'unit_cost']
            
            with open(file_path, 'w', newline='') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fields)
                writer.writeheader()
                
                # Write items
                for item in items:
                    # Filter only the fields we want to export
                    row = {field: item.get(field, '') for field in fields}
                    writer.writerow(row)
            
            QMessageBox.information(
                self,
                "Export Successful",
                f"Successfully exported {len(items)} items to {file_path}"
            )
            
        except Exception as e:
            QMessageBox.critical(
                self,
                "Export Error",
                f"An error occurred while exporting items:\n{str(e)}"
            )

    def show_checkout_dialog(self):
        """Show dialog for checking out a tool"""
        # Get selected tool
        current_row = self.tools_table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "No Tool Selected", "Please select a tool to check out.")
            return
            
        tool_id = int(self.tools_table.item(current_row, 0).text())
        tool_name = self.tools_table.item(current_row, 1).text()
        
        # Create dialog
        dialog = QDialog(self)
        dialog.setWindowTitle("Check Out Tool")
        dialog.setModal(True)
        
        layout = QFormLayout(dialog)
        
        # Add form fields
        craftsman_combo = QComboBox()
        craftsmen = self.db_manager.get_all_craftsmen()
        for craftsman in craftsmen:
            craftsman_combo.addItem(
                f"{craftsman['first_name']} {craftsman['last_name']}", 
                craftsman['craftsman_id']
            )
            
        work_order_combo = QComboBox()
        work_order_combo.addItem("None", None)
        work_orders = self.db_manager.get_open_work_orders()
        for wo in work_orders:
            work_order_combo.addItem(f"WO#{wo['work_order_id']} - {wo['title']}", wo['work_order_id'])
            
        expected_return = QDateEdit()
        expected_return.setDate(QDate.currentDate().addDays(1))
        expected_return.setCalendarPopup(True)
        
        notes = QTextEdit()
        
        layout.addRow("Tool:", QLabel(tool_name))
        layout.addRow("Craftsman:", craftsman_combo)
        layout.addRow("Work Order:", work_order_combo)
        layout.addRow("Expected Return:", expected_return)
        layout.addRow("Notes:", notes)
        
        # Add buttons
        button_box = QHBoxLayout()
        checkout_btn = QPushButton("Check Out")
        cancel_btn = QPushButton("Cancel")
        
        button_box.addWidget(checkout_btn)
        button_box.addWidget(cancel_btn)
        layout.addRow(button_box)
        
        # Connect buttons
        cancel_btn.clicked.connect(dialog.reject)
        checkout_btn.clicked.connect(lambda: self.process_checkout(
            dialog,
            tool_id,
            craftsman_combo.currentData(),
            work_order_combo.currentData(),
            expected_return.date().toPython(),
            notes.toPlainText()
        ))
        
        dialog.exec()

    def process_checkout(self, dialog, tool_id, craftsman_id, work_order_id, expected_return, notes):
        """Process the tool checkout"""
        try:
            checkout_data = {
                'item_id': tool_id,
                'craftsman_id': craftsman_id,
                'work_order_id': work_order_id,
                'expected_return_date': expected_return,
                'notes': notes
            }
            
            if self.db_manager.checkout_tool(checkout_data):
                QMessageBox.information(self, "Success", "Tool checked out successfully!")
                dialog.accept()
                self.refresh_tools()
            else:
                QMessageBox.critical(self, "Error", "Failed to check out tool!")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error checking out tool: {str(e)}")

    def show_checkin_dialog(self):
        """Show dialog for checking in a tool"""
        # Get selected tool
        current_row = self.tools_table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "No Tool Selected", "Please select a tool to check in.")
            return
            
        tool_id = int(self.tools_table.item(current_row, 0).text())
        tool_name = self.tools_table.item(current_row, 1).text()
        
        # Verify tool is checked out
        if self.tools_table.item(current_row, 2).text() != "Checked Out":
            QMessageBox.warning(self, "Invalid Action", "This tool is not checked out.")
            return
        
        # Create dialog
        dialog = QDialog(self)
        dialog.setWindowTitle("Check In Tool")
        dialog.setModal(True)
        
        layout = QFormLayout(dialog)
        
        # Add form fields
        condition = QComboBox()
        condition.addItems(["Good", "Needs Maintenance", "Damaged"])
        
        notes = QTextEdit()
        
        layout.addRow("Tool:", QLabel(tool_name))
        layout.addRow("Condition:", condition)
        layout.addRow("Notes:", notes)
        
        # Add buttons
        button_box = QHBoxLayout()
        checkin_btn = QPushButton("Check In")
        cancel_btn = QPushButton("Cancel")
        
        button_box.addWidget(checkin_btn)
        button_box.addWidget(cancel_btn)
        layout.addRow(button_box)
        
        # Connect buttons
        cancel_btn.clicked.connect(dialog.reject)
        checkin_btn.clicked.connect(lambda: self.process_checkin(
            dialog,
            tool_id,
            condition.currentText(),
            notes.toPlainText()
        ))
        
        dialog.exec()

    def process_checkin(self, dialog, tool_id, condition, notes):
        """Process the tool check-in"""
        try:
            checkin_data = {
                'item_id': tool_id,
                'condition': condition,
                'notes': notes
            }
            
            if self.db_manager.checkin_tool(checkin_data):
                QMessageBox.information(self, "Success", "Tool checked in successfully!")
                dialog.accept()
                self.refresh_tools()
            else:
                QMessageBox.critical(self, "Error", "Failed to check in tool!")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error checking in tool: {str(e)}")

    def show_add_tool_dialog(self):
        """Show dialog for adding a new tool"""
        dialog = QDialog(self)
        dialog.setWindowTitle("Add New Tool")
        dialog.setModal(True)
        
        layout = QFormLayout(dialog)
        
        # Add form fields
        tool_id = QLineEdit()
        name = QLineEdit()
        description = QTextEdit()
        location = QLineEdit()
        quantity = QSpinBox()
        quantity.setMinimum(1)
        
        layout.addRow("Tool ID:", tool_id)
        layout.addRow("Name:", name)
        layout.addRow("Description:", description)
        layout.addRow("Location:", location)
        layout.addRow("Quantity:", quantity)
        
        # Add buttons
        button_box = QHBoxLayout()
        save_btn = QPushButton("Save")
        cancel_btn = QPushButton("Cancel")
        
        button_box.addWidget(save_btn)
        button_box.addWidget(cancel_btn)
        layout.addRow(button_box)
        
        # Connect buttons
        cancel_btn.clicked.connect(dialog.reject)
        save_btn.clicked.connect(lambda: self.save_tool(
            dialog,
            tool_id.text(),
            name.text(),
            description.toPlainText(),
            location.text(),
            quantity.value()
        ))
        
        dialog.exec()

    def save_tool(self, dialog, tool_id, name, description, location, quantity):
        """Save a new tool to the database"""
        if not tool_id or not name:
            QMessageBox.warning(self, "Validation Error", "Tool ID and Name are required!")
            return
            
        try:
            tool_data = {
                'item_code': tool_id,
                'name': name,
                'description': description,
                'location': location,
                'quantity': quantity,
                'category': 'Tool',  # Fixed category for tools
                'minimum_quantity': 1,
                'reorder_point': 1,
                'unit_cost': 0.00  # Default value, can be updated later
            }
            
            if self.db_manager.add_inventory_item(tool_data):
                QMessageBox.information(self, "Success", "Tool added successfully!")
                dialog.accept()
                self.refresh_tools()
            else:
                QMessageBox.critical(self, "Error", "Failed to add tool!")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error adding tool: {str(e)}")

    def refresh_tools(self):
        """Refresh the tools table"""
        # Clear the table
        self.tools_table.setRowCount(0)
        
        # Get tools (items with category 'Tool')
        tools = self.db_manager.get_inventory_items_by_category('Tool')
        
        # Populate the table
        for tool in tools:
            row_position = self.tools_table.rowCount()
            self.tools_table.insertRow(row_position)
            
            # Get checkout status
            checkout = self.db_manager.get_tool_checkout_status(tool['item_id'])
            status = "Checked Out" if checkout else "Available"
            checked_out_to = f"{checkout['craftsman_name']} until {checkout['expected_return_date']}" if checkout else ""
            
            # Set tool data
            self.tools_table.setItem(row_position, 0, QTableWidgetItem(str(tool['item_id'])))
            self.tools_table.setItem(row_position, 1, QTableWidgetItem(tool['name']))
            self.tools_table.setItem(row_position, 2, QTableWidgetItem(status))
            self.tools_table.setItem(row_position, 3, QTableWidgetItem(tool['location']))
            self.tools_table.setItem(row_position, 4, QTableWidgetItem(checked_out_to))
            self.tools_table.setItem(row_position, 5, QTableWidgetItem(tool.get('notes', '')))
        
        # Resize columns to content
        self.tools_table.resizeColumnsToContents()

    def show_add_supplier_dialog(self):
        """Show dialog for adding a new supplier"""
        dialog = AddSupplierDialog(self.db_manager, self)
        if dialog.exec() == QDialog.Accepted:
            self.refresh_suppliers()

    def show_edit_supplier_dialog(self):
        """Show dialog for editing a supplier"""
        # Get selected supplier
        current_row = self.suppliers_table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "No Supplier Selected", "Please select a supplier to edit.")
            return
            
        # Get supplier data
        supplier_name = self.suppliers_table.item(current_row, 0).text()
        supplier = self.db_manager.get_supplier_by_name(supplier_name)
        
        if not supplier:
            QMessageBox.critical(self, "Error", "Could not find supplier data!")
            return
            
        # Create and show edit dialog
        dialog = AddSupplierDialog(self.db_manager, self)
        
        # Pre-fill the form with existing data
        dialog.name.setText(supplier['name'])
        dialog.contact_person.setText(supplier['contact_person'])
        dialog.phone.setText(supplier['phone'])
        dialog.email.setText(supplier['email'])
        dialog.address.setText(supplier['address'])
        dialog.notes.setText(supplier['notes'])
        
        # Change dialog title to indicate editing
        dialog.setWindowTitle("Edit Supplier")
        
        if dialog.exec() == QDialog.Accepted:
            self.refresh_suppliers()

    def export_suppliers(self):
        """Export suppliers to a CSV file"""
        from PySide6.QtWidgets import QFileDialog
        import csv
        
        # Show file dialog to select save location
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export Suppliers",
            "",
            "CSV Files (*.csv);;All Files (*)"
        )
        
        if not file_path:
            return
            
        try:
            # Get all suppliers
            suppliers = self.db_manager.get_suppliers()
            
            # Define fields to export
            fields = ['name', 'contact_person', 'phone', 'email', 'address', 'status', 'notes']
            
            with open(file_path, 'w', newline='') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fields)
                writer.writeheader()
                
                # Write suppliers
                for supplier in suppliers:
                    # Filter only the fields we want to export
                    row = {field: supplier.get(field, '') for field in fields}
                    writer.writerow(row)
            
            QMessageBox.information(
                self,
                "Export Successful",
                f"Successfully exported {len(suppliers)} suppliers to {file_path}"
            )
            
        except Exception as e:
            QMessageBox.critical(
                self,
                "Export Error",
                f"An error occurred while exporting suppliers:\n{str(e)}"
            )

    def refresh_suppliers(self):
        """Refresh the suppliers table"""
        # Clear the table
        self.suppliers_table.setRowCount(0)
        
        # Get suppliers
        suppliers = self.db_manager.get_suppliers()
        
        # Populate the table
        for supplier in suppliers:
            row_position = self.suppliers_table.rowCount()
            self.suppliers_table.insertRow(row_position)
            
            # Set supplier data
            self.suppliers_table.setItem(row_position, 0, QTableWidgetItem(supplier['name']))
            self.suppliers_table.setItem(row_position, 1, QTableWidgetItem(supplier.get('contact_person', '')))
            self.suppliers_table.setItem(row_position, 2, QTableWidgetItem(supplier.get('phone', '')))
            self.suppliers_table.setItem(row_position, 3, QTableWidgetItem(supplier.get('email', '')))
            self.suppliers_table.setItem(row_position, 4, QTableWidgetItem(supplier.get('address', '')))
            self.suppliers_table.setItem(row_position, 5, QTableWidgetItem(supplier.get('status', 'Active')))
            self.suppliers_table.setItem(row_position, 6, QTableWidgetItem(supplier.get('notes', '')))
        
        # Resize columns to content
        self.suppliers_table.resizeColumnsToContents()

    def import_data(self):
        """Import data from a file"""
        from PySide6.QtWidgets import QFileDialog, QInputDialog
        
        # Ask user what type of data to import
        data_type, ok = QInputDialog.getItem(
            self,
            "Import Data",
            "Select data type to import:",
            ["Inventory Items", "Tools", "Suppliers"],
            0,
            False
        )
        
        if not ok:
            return
            
        # Show file dialog to select file
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            f"Import {data_type}",
            "",
            "CSV Files (*.csv);;All Files (*)"
        )
        
        if not file_path:
            return
            
        # Import based on data type
        if data_type == "Inventory Items":
            self.import_items()
        elif data_type == "Tools":
            self.import_tools()
        elif data_type == "Suppliers":
            self.import_suppliers()

    def export_data(self):
        """Export data to a file"""
        from PySide6.QtWidgets import QFileDialog, QInputDialog
        
        # Ask user what type of data to export
        data_type, ok = QInputDialog.getItem(
            self,
            "Export Data",
            "Select data type to export:",
            ["Inventory Items", "Tools", "Suppliers"],
            0,
            False
        )
        
        if not ok:
            return
            
        # Export based on data type
        if data_type == "Inventory Items":
            self.export_items()
        elif data_type == "Tools":
            self.export_tools()
        elif data_type == "Suppliers":
            self.export_suppliers()

    def import_tools(self):
        """Import tools from a CSV file"""
        from PySide6.QtWidgets import QFileDialog
        import csv
        
        # Show file dialog to select CSV file
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Import Tools",
            "",
            "CSV Files (*.csv);;All Files (*)"
        )
        
        if not file_path:
            return
            
        try:
            with open(file_path, 'r', newline='') as csvfile:
                reader = csv.DictReader(csvfile)
                
                # Validate headers
                required_fields = ['tool_id', 'name', 'description', 'location', 'quantity']
                headers = reader.fieldnames
                
                missing_fields = [field for field in required_fields if field not in headers]
                if missing_fields:
                    QMessageBox.warning(
                        self,
                        "Invalid CSV Format",
                        f"The following required fields are missing: {', '.join(missing_fields)}"
                    )
                    return
                
                # Import tools
                success_count = 0
                error_count = 0
                
                for row in reader:
                    try:
                        # Convert numeric fields
                        row['quantity'] = int(row['quantity'])
                        
                        # Create tool data
                        tool_data = {
                            'item_code': row['tool_id'],
                            'name': row['name'],
                            'description': row['description'],
                            'location': row['location'],
                            'quantity': row['quantity'],
                            'category': 'Tool',
                            'minimum_quantity': 1,
                            'reorder_point': 1,
                            'unit_cost': 0.00
                        }
                        
                        # Add tool to database
                        if self.db_manager.add_inventory_item(tool_data):
                            success_count += 1
                        else:
                            error_count += 1
                    except ValueError as e:
                        error_count += 1
                        print(f"Error importing row: {e}")
                
                # Show results
                QMessageBox.information(
                    self,
                    "Import Results",
                    f"Successfully imported {success_count} tools.\n"
                    f"Failed to import {error_count} tools."
                )
                
                # Refresh the tools table
                self.refresh_tools()
                
        except Exception as e:
            QMessageBox.critical(
                self,
                "Import Error",
                f"An error occurred while importing tools:\n{str(e)}"
            )

    def export_tools(self):
        """Export tools to a CSV file"""
        from PySide6.QtWidgets import QFileDialog
        import csv
        
        # Show file dialog to select save location
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export Tools",
            "",
            "CSV Files (*.csv);;All Files (*)"
        )
        
        if not file_path:
            return
            
        try:
            # Get all tools
            tools = self.db_manager.get_inventory_items_by_category('Tool')
            
            # Define fields to export
            fields = ['tool_id', 'name', 'description', 'location', 'quantity', 'status', 'notes']
            
            with open(file_path, 'w', newline='') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fields)
                writer.writeheader()
                
                # Write tools
                for tool in tools:
                    # Get checkout status
                    checkout = self.db_manager.get_tool_checkout_status(tool['item_id'])
                    status = "Checked Out" if checkout else "Available"
                    
                    # Create row data
                    row = {
                        'tool_id': tool['item_code'],
                        'name': tool['name'],
                        'description': tool.get('description', ''),
                        'location': tool.get('location', ''),
                        'quantity': tool.get('quantity', 1),
                        'status': status,
                        'notes': tool.get('notes', '')
                    }
                    writer.writerow(row)
            
            QMessageBox.information(
                self,
                "Export Successful",
                f"Successfully exported {len(tools)} tools to {file_path}"
            )
            
        except Exception as e:
            QMessageBox.critical(
                self,
                "Export Error",
                f"An error occurred while exporting tools:\n{str(e)}"
            )

    def import_suppliers(self):
        """Import suppliers from a CSV file"""
        from PySide6.QtWidgets import QFileDialog
        import csv
        
        # Show file dialog to select CSV file
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Import Suppliers",
            "",
            "CSV Files (*.csv);;All Files (*)"
        )
        
        if not file_path:
            return
            
        try:
            with open(file_path, 'r', newline='') as csvfile:
                reader = csv.DictReader(csvfile)
                
                # Validate headers
                required_fields = ['name', 'contact_person', 'phone', 'email', 'address']
                headers = reader.fieldnames
                
                missing_fields = [field for field in required_fields if field not in headers]
                if missing_fields:
                    QMessageBox.warning(
                        self,
                        "Invalid CSV Format",
                        f"The following required fields are missing: {', '.join(missing_fields)}"
                    )
                    return
                
                # Import suppliers
                success_count = 0
                error_count = 0
                
                for row in reader:
                    try:
                        if self.db_manager.add_supplier(row):
                            success_count += 1
                        else:
                            error_count += 1
                    except Exception as e:
                        error_count += 1
                        print(f"Error importing row: {e}")
                
                # Show results
                QMessageBox.information(
                    self,
                    "Import Results",
                    f"Successfully imported {success_count} suppliers.\n"
                    f"Failed to import {error_count} suppliers."
                )
                
                # Refresh the suppliers table
                self.refresh_suppliers()
                
        except Exception as e:
            QMessageBox.critical(
                self,
                "Import Error",
                f"An error occurred while importing suppliers:\n{str(e)}"
            )

    def show_report_success_message(self, report_path):
        """Show success message with options to open report or containing folder"""
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("Report Generated")
        msg_box.setText(f"Report has been generated successfully!")
        msg_box.setInformativeText(f"Location: {report_path}")
        
        # Add custom buttons
        open_btn = msg_box.addButton("Open Report", QMessageBox.ActionRole)
        folder_btn = msg_box.addButton("Open Folder", QMessageBox.ActionRole)
        ok_btn = msg_box.addButton(QMessageBox.Ok)
        
        msg_box.exec_()
        
        clicked_button = msg_box.clickedButton()
        if clicked_button == open_btn:
            # Open the report file with default application
            if os.path.exists(report_path):
                if os.name == 'nt':  # Windows
                    os.startfile(report_path)
                elif os.name == 'posix':  # macOS and Linux
                    if os.system('which xdg-open') == 0:  # Linux
                        subprocess.run(['xdg-open', report_path])
                    else:  # macOS
                        subprocess.run(['open', report_path])
        elif clicked_button == folder_btn:
            # Open the containing folder
            folder_path = os.path.dirname(report_path)
            if os.path.exists(folder_path):
                if os.name == 'nt':  # Windows
                    subprocess.run(['explorer', folder_path])
                elif os.name == 'posix':  # macOS and Linux
                    if os.system('which xdg-open') == 0:  # Linux
                        subprocess.run(['xdg-open', folder_path])
                    else:  # macOS
                        subprocess.run(['open', folder_path])

    def generate_inventory_report(self):
        """Generate inventory report"""
        try:
            # Get inventory data
            items = self.db_manager.get_inventory_items()
            
            # Calculate statistics
            total_items = len(items)
            total_value = sum(float(item.get('quantity', 0)) * float(item.get('unit_cost', 0)) for item in items)
            low_stock_items = len([item for item in items if item.get('quantity', 0) <= item.get('minimum_quantity', 0)])
            
            # Create report data
            report_data = {
                'items': items,
                'summary': {
                    'total_items': total_items,
                    'total_value': total_value,
                    'low_stock_items': low_stock_items,
                    'report_date': datetime.now()
                }
            }
            
            # Create report
            report = InventoryReport(report_data)
            report_path = report.generate()
            
            if report_path:
                self.show_report_success_message(report_path)
            else:
                QMessageBox.critical(
                    self,
                    "Report Error",
                    "Failed to generate inventory report."
                )
                
        except Exception as e:
            QMessageBox.critical(
                self,
                "Report Error",
                f"An error occurred while generating the report:\n{str(e)}"
            )

    def generate_valuation_report(self):
        """Generate inventory valuation report"""
        try:
            # Get inventory data
            items = self.db_manager.get_inventory_items()
            
            # Calculate valuations by category
            valuations = {}
            for item in items:
                category = item.get('category', 'Uncategorized')
                value = float(item.get('quantity', 0)) * float(item.get('unit_cost', 0))
                
                if category not in valuations:
                    valuations[category] = {
                        'count': 0,
                        'value': 0.0
                    }
                
                valuations[category]['count'] += 1
                valuations[category]['value'] += value
            
            # Calculate total value
            total_value = sum(v['value'] for v in valuations.values())
            
            # Create report data
            report_data = {
                'items': items,
                'valuations': valuations,
                'summary': {
                    'total_value': total_value,
                    'report_date': datetime.now()
                }
            }
            
            # Create report
            report = InventoryValuationReport(report_data)
            report_path = report.generate()
            
            if report_path:
                self.show_report_success_message(report_path)
            else:
                QMessageBox.critical(
                    self,
                    "Report Error",
                    "Failed to generate valuation report."
                )
                
        except Exception as e:
            QMessageBox.critical(
                self,
                "Report Error",
                f"An error occurred while generating the report:\n{str(e)}"
            )

    def generate_movement_report(self):
        """Generate inventory movement report"""
        try:
            # Get inventory data
            items = self.db_manager.get_inventory_items()
            
            # Prepare movement data
            movement_data = []
            for item in items:
                quantity = int(item.get('quantity', 0))
                min_quantity = int(item.get('minimum_quantity', 0))
                reorder_point = int(item.get('reorder_point', 0))
                
                status = "OK"
                if quantity <= min_quantity:
                    status = "LOW STOCK"
                elif quantity <= reorder_point:
                    status = "REORDER"
                
                movement_data.append({
                    'item_code': item.get('item_code', ''),
                    'name': item.get('name', ''),
                    'quantity': quantity,
                    'min_quantity': min_quantity,
                    'reorder_point': reorder_point,
                    'status': status,
                    'unit': item.get('unit', '')
                })
            
            # Create report data
            report_data = {
                'items': items,
                'movement_data': movement_data,
                'summary': {
                    'total_items': len(items),
                    'low_stock_items': len([item for item in items if item.get('quantity', 0) <= item.get('minimum_quantity', 0)]),
                    'reorder_items': len([item for item in items if item.get('quantity', 0) <= item.get('reorder_point', 0)]),
                    'report_date': datetime.now()
                }
            }
            
            # Create report
            report = InventoryMovementReport(report_data)
            report_path = report.generate()
            
            if report_path:
                self.show_report_success_message(report_path)
            else:
                QMessageBox.critical(
                    self,
                    "Report Error",
                    "Failed to generate movement report."
                )
                
        except Exception as e:
            QMessageBox.critical(
                self,
                "Report Error",
                f"An error occurred while generating the report:\n{str(e)}"
            )

    def generate_custom_report(self):
        """Generate custom inventory report"""
        try:
            # Ask user what to include in the report
            options = {
                'inventory_summary': 'Include Inventory Summary',
                'low_stock': 'Include Low Stock Items',
                'valuation': 'Include Valuation Analysis',
                'movement': 'Include Movement Analysis'
            }
            
            # Create dialog for options
            dialog = QDialog(self)
            dialog.setWindowTitle("Custom Report Options")
            dialog.setModal(True)
            
            layout = QVBoxLayout(dialog)
            
            # Add checkboxes for options
            checkboxes = {}
            for key, label in options.items():
                checkbox = QCheckBox(label)
                checkbox.setChecked(True)  # Default all to checked
                checkboxes[key] = checkbox
                layout.addWidget(checkbox)
            
            # Add buttons
            button_box = QHBoxLayout()
            generate_btn = QPushButton("Generate")
            cancel_btn = QPushButton("Cancel")
            
            button_box.addWidget(generate_btn)
            button_box.addWidget(cancel_btn)
            layout.addLayout(button_box)
            
            # Connect buttons
            cancel_btn.clicked.connect(dialog.reject)
            generate_btn.clicked.connect(dialog.accept)
            
            if dialog.exec() != QDialog.Accepted:
                return
            
            # Get selected options
            selected_options = {key: checkbox.isChecked() for key, checkbox in checkboxes.items()}
            
            # Get inventory data
            items = self.db_manager.get_inventory_items()
            
            # Create report data
            report_data = {
                'items': items,
                'options': selected_options,
                'summary': {
                    'total_items': len(items),
                    'total_value': sum(float(item.get('quantity', 0)) * float(item.get('unit_cost', 0)) for item in items),
                    'low_stock_items': len([item for item in items if item.get('quantity', 0) <= item.get('minimum_quantity', 0)]),
                    'reorder_items': len([item for item in items if item.get('quantity', 0) <= item.get('reorder_point', 0)]),
                    'report_date': datetime.now()
                }
            }
            
            # Create report
            report = InventoryCustomReport(report_data)
            report_path = report.generate()
            
            if report_path:
                self.show_report_success_message(report_path)
            else:
                QMessageBox.critical(
                    self,
                    "Report Error",
                    "Failed to generate custom report."
                )
                
        except Exception as e:
            QMessageBox.critical(
                self,
                "Report Error",
                f"An error occurred while generating the report:\n{str(e)}"
            )

    def generate_demo_data(self):
        """Generate demo data for development purposes with random variations"""
        connection = None
        cursor = None
        try:
            # Establish database connection
            connection = self.db_manager.connect()
            if not connection:
                raise Exception("Could not establish database connection")
            
            cursor = connection.cursor()
            
            # Sample categories with more options
            categories = [
                {'name': 'Electronics', 'description': 'Electronic components and devices'},
                {'name': 'Mechanical', 'description': 'Mechanical parts and components'},
                {'name': 'Safety', 'description': 'Safety equipment and gear'},
                {'name': 'Tool', 'description': 'Maintenance tools and equipment'},
                {'name': 'Electrical', 'description': 'Electrical supplies and components'},
                {'name': 'Plumbing', 'description': 'Plumbing supplies and fixtures'},
                {'name': 'HVAC', 'description': 'Heating, ventilation, and air conditioning'},
                {'name': 'Office', 'description': 'Office supplies and equipment'}
            ]
            
            # Add categories
            for category in categories:
                cursor.execute("SELECT category_id FROM inventory_categories WHERE name = %s", (category['name'],))
                if not cursor.fetchone():
                    cursor.execute(
                        "INSERT INTO inventory_categories (name, description) VALUES (%s, %s)",
                        (category['name'], category['description'])
                    )
            connection.commit()
            
            # Sample suppliers with more variety
            suppliers = [
                {
                    'name': 'TechSupply Co.',
                    'contact_person': 'John Smith',
                    'phone': f"555-{random.randint(1000,9999)}",
                    'email': 'john@techsupply.com',
                    'address': '123 Tech Street',
                    'notes': 'Primary electronics supplier'
                },
                {
                    'name': 'MechParts Inc.',
                    'contact_person': 'Jane Doe',
                    'phone': f"555-{random.randint(1000,9999)}",
                    'email': 'jane@mechparts.com',
                    'address': '456 Mech Avenue',
                    'notes': 'Mechanical parts supplier'
                },
                {
                    'name': 'SafetyGear Ltd.',
                    'contact_person': 'Bob Wilson',
                    'phone': f"555-{random.randint(1000,9999)}",
                    'email': 'bob@safetygear.com',
                    'address': '789 Safety Road',
                    'notes': 'Safety equipment supplier'
                },
                {
                    'name': 'ElectroMax Systems',
                    'contact_person': 'Sarah Johnson',
                    'phone': f"555-{random.randint(1000,9999)}",
                    'email': 'sarah@electromax.com',
                    'address': '321 Electric Ave',
                    'notes': 'Electrical components supplier'
                },
                {
                    'name': 'PlumbPro Supply',
                    'contact_person': 'Mike Brown',
                    'phone': f"555-{random.randint(1000,9999)}",
                    'email': 'mike@plumbpro.com',
                    'address': '654 Water Way',
                    'notes': 'Plumbing supplies provider'
                }
            ]
            
            # Add suppliers
            for supplier in suppliers:
                if not self.db_manager.get_supplier_by_name(supplier['name']):
                    self.db_manager.add_supplier(supplier)
            
            # Base items with variations
            base_items = [
                {
                    'name': 'Digital Multimeter',
                    'category': 'Electronics',
                    'supplier': 'TechSupply Co.',
                    'unit': 'pcs',
                    'base_cost': 89.99
                },
                {
                    'name': 'Bearing Set',
                    'category': 'Mechanical',
                    'supplier': 'MechParts Inc.',
                    'unit': 'sets',
                    'base_cost': 45.50
                },
                {
                    'name': 'Safety Helmet',
                    'category': 'Safety',
                    'supplier': 'SafetyGear Ltd.',
                    'unit': 'pcs',
                    'base_cost': 29.99
                },
                {
                    'name': 'Wrench Set',
                    'category': 'Tool',
                    'supplier': 'MechParts Inc.',
                    'unit': 'sets',
                    'base_cost': 149.99
                }
            ]
            
            # Generate variations of items
            items = []
            for base_item in base_items:
                # Generate 2-4 variations of each base item
                for i in range(random.randint(2, 4)):
                    # Add size/type variations
                    variations = {
                        'Digital Multimeter': ['Basic', 'Professional', 'Industrial', 'Wireless'],
                        'Bearing Set': ['Small', 'Medium', 'Large', 'Precision'],
                        'Safety Helmet': ['Standard', 'Premium', 'Heavy-Duty', 'Lightweight'],
                        'Wrench Set': ['Metric', 'SAE', 'Combined', 'Professional']
                    }
                    
                    variation = random.choice(variations[base_item['name']])
                    item_name = f"{variation} {base_item['name']}"
                    
                    # Generate random item code
                    category_prefix = base_item['category'][:2].upper()
                    item_code = f"{category_prefix}{random.randint(1000, 9999)}"
                    
                    # Randomize quantities and costs
                    quantity = random.randint(5, 100)
                    min_quantity = max(1, int(quantity * random.uniform(0.1, 0.2)))  # 10-20% of quantity
                    reorder_point = max(2, int(quantity * random.uniform(0.2, 0.3)))  # 20-30% of quantity
                    unit_cost = base_item['base_cost'] * random.uniform(0.8, 1.2)  # ±20% of base cost
                    
                    # Generate random location
                    shelf = random.choice(['A', 'B', 'C', 'D'])
                    position = random.randint(1, 5)
                    level = random.randint(1, 3)
                    location = f"Shelf {shelf}{position}-L{level}"
                    
                    items.append({
                        'item_code': item_code,
                        'name': item_name,
                        'category': base_item['category'],
                        'quantity': quantity,
                        'unit': base_item['unit'],
                        'unit_cost': round(unit_cost, 2),
                        'minimum_quantity': min_quantity,
                        'reorder_point': reorder_point,
                        'location': location,
                        'supplier': base_item['supplier']
                    })
            
            # Add some random tools
            tool_types = ['Hammer', 'Screwdriver', 'Pliers', 'Drill', 'Saw', 'Level', 'Measuring Tape']
            tool_variations = ['Standard', 'Professional', 'Heavy-Duty', 'Precision', 'Industrial']
            
            for _ in range(random.randint(5, 8)):  # Add 5-8 random tools
                tool_type = random.choice(tool_types)
                variation = random.choice(tool_variations)
                tool_name = f"{variation} {tool_type}"
                
                items.append({
                    'item_code': f"TL{random.randint(1000, 9999)}",
                    'name': tool_name,
                    'category': 'Tool',
                    'quantity': random.randint(2, 10),
                    'unit': 'pcs',
                    'unit_cost': round(random.uniform(20, 200), 2),
                    'minimum_quantity': 1,
                    'reorder_point': 2,
                    'location': f"Tool Cabinet {random.randint(1, 5)}",
                    'supplier': random.choice(['MechParts Inc.', 'TechSupply Co.'])
                })
            
            # Add inventory items
            success_count = 0
            for item in items:
                try:
                    # Get category ID
                    cursor.execute("SELECT category_id FROM inventory_categories WHERE name = %s", (item['category'],))
                    category_result = cursor.fetchone()
                    category_id = category_result[0] if category_result else None
                    
                    # Get supplier ID
                    supplier = self.db_manager.get_supplier_by_name(item['supplier'])
                    supplier_id = supplier['supplier_id'] if supplier else None
                    
                    # Prepare item data
                    item_data = {
                        'item_code': item['item_code'],
                        'name': item['name'],
                        'category_id': category_id,
                        'supplier_id': supplier_id,
                        'quantity': item['quantity'],
                        'unit': item['unit'],
                        'unit_cost': item['unit_cost'],
                        'minimum_quantity': item['minimum_quantity'],
                        'reorder_point': item['reorder_point'],
                        'location': item['location']
                    }
                    
                    # Add item
                    if self.db_manager.add_inventory_item(item_data):
                        success_count += 1
                        
                except Exception as e:
                    print(f"Error adding demo item {item['item_code']}: {e}")
                    continue
            
            # Commit all changes
            connection.commit()
            
            # Refresh the inventory
            self.refresh_inventory()
            
            # Show success message
            QMessageBox.information(
                self,
                "Demo Data Generated",
                f"Successfully added:\n"
                f"- {len(categories)} categories\n"
                f"- {len(suppliers)} suppliers\n"
                f"- {success_count} inventory items"
            )
            
        except Exception as e:
            if connection:
                connection.rollback()
            QMessageBox.critical(
                self,
                "Error",
                f"An error occurred while generating demo data:\n{str(e)}"
            )
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()

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
