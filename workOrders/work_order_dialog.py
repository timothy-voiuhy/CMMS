from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QLabel, QLineEdit, 
    QTextEdit, QComboBox, QDateEdit, QSpinBox, QPushButton, QScrollArea,
    QWidget, QMessageBox, QTableWidget, QTableWidgetItem, QHeaderView
)
from PySide6.QtCore import Qt, QDate
import json

class WorkOrderDialog(QDialog):
    """Dialog for creating or editing a work order"""
    def __init__(self, db_manager, work_order=None, parent=None):
        super().__init__(parent)
        self.db_manager = db_manager
        self.work_order = work_order
        self.is_edit_mode = work_order is not None
        self.selected_tools = []  # Store selected tools
        self.selected_spares = []  # Store selected spare parts
        
        self.setWindowTitle("Create Work Order" if not self.is_edit_mode else "Edit Work Order")
        self.setMinimumWidth(800)  # Increased width to accommodate tables
        self.setMinimumHeight(800)  # Increased height
        
        self.setup_ui()
        
        if self.is_edit_mode:
            self.load_work_order_data()
    
    def setup_ui(self):
        """Set up the dialog UI"""
        layout = QVBoxLayout(self)
        
        # Create scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        # Create content widget
        content_widget = QWidget()
        self.form_layout = QFormLayout(content_widget)
        
        # Basic information section
        self.form_layout.addRow(QLabel("<b>Basic Information</b>"))
        
        self.title_edit = QLineEdit()
        self.form_layout.addRow("Title:", self.title_edit)
        
        self.description_edit = QTextEdit()
        self.description_edit.setMinimumHeight(100)
        self.form_layout.addRow("Description:", self.description_edit)
        
        # Equipment selection
        self.equipment_combo = QComboBox()
        self.load_equipment_list()
        self.form_layout.addRow("Equipment:", self.equipment_combo)
        
        # Craftsman selection
        self.craftsman_combo = QComboBox()
        self.load_craftsmen_list()
        self.form_layout.addRow("Assigned To:", self.craftsman_combo)
        
        # Priority selection
        self.priority_combo = QComboBox()
        self.priority_combo.addItems(["Low", "Medium", "High", "Critical"])
        self.priority_combo.setCurrentText("Medium")  # Default
        self.form_layout.addRow("Priority:", self.priority_combo)
        
        # Status selection
        self.status_combo = QComboBox()
        self.status_combo.addItems(["Open", "In Progress", "On Hold", "Completed", "Cancelled"])
        self.form_layout.addRow("Status:", self.status_combo)
        
        # Dates section
        self.form_layout.addRow(QLabel("<b>Dates</b>"))
        
        self.due_date_edit = QDateEdit()
        self.due_date_edit.setCalendarPopup(True)
        self.due_date_edit.setDate(QDate.currentDate().addDays(7))  # Default to 1 week from now
        self.form_layout.addRow("Due Date:", self.due_date_edit)
        
        self.completed_date_edit = QDateEdit()
        self.completed_date_edit.setCalendarPopup(True)
        self.completed_date_edit.setDate(QDate.currentDate())
        self.completed_date_edit.setEnabled(False)  # Disabled by default
        self.form_layout.addRow("Completion Date:", self.completed_date_edit)
        
        # Connect status change to enable/disable completion date
        self.status_combo.currentTextChanged.connect(self.on_status_changed)
        
        # Time and cost section
        self.form_layout.addRow(QLabel("<b>Time and Cost</b>"))
        
        self.estimated_hours_spin = QSpinBox()
        self.estimated_hours_spin.setRange(0, 1000)
        self.estimated_hours_spin.setSuffix(" hours")
        self.form_layout.addRow("Estimated Hours:", self.estimated_hours_spin)
        
        self.actual_hours_spin = QSpinBox()
        self.actual_hours_spin.setRange(0, 1000)
        self.actual_hours_spin.setSuffix(" hours")
        self.form_layout.addRow("Actual Hours:", self.actual_hours_spin)
        
        # Replace the old parts section with new Tools and Spare Parts sections
        self.form_layout.addRow(QLabel("<b>Tools Required</b>"))
        
        # Tools table
        self.tools_table = QTableWidget()
        self.tools_table.setColumnCount(5)
        self.tools_table.setHorizontalHeaderLabels([
            "Tool ID", "Name", "Available Quantity", "Required Quantity", "Location"
        ])
        self.tools_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        self.tools_table.setMinimumHeight(150)
        self.form_layout.addRow(self.tools_table)
        
        # Tool selection controls
        tool_controls = QHBoxLayout()
        self.tool_combo = QComboBox()
        self.tool_combo.setMinimumWidth(300)
        self.tool_quantity_spin = QSpinBox()
        self.tool_quantity_spin.setMinimum(1)
        add_tool_btn = QPushButton("Add Tool")
        add_tool_btn.clicked.connect(self.add_tool)
        remove_tool_btn = QPushButton("Remove Selected")
        remove_tool_btn.clicked.connect(lambda: self.remove_selected(self.tools_table))
        
        tool_controls.addWidget(QLabel("Select Tool:"))
        tool_controls.addWidget(self.tool_combo)
        tool_controls.addWidget(QLabel("Quantity:"))
        tool_controls.addWidget(self.tool_quantity_spin)
        tool_controls.addWidget(add_tool_btn)
        tool_controls.addWidget(remove_tool_btn)
        self.form_layout.addRow(tool_controls)

        # Spare Parts section
        self.form_layout.addRow(QLabel("<b>Spare Parts Required</b>"))
        
        # Spare parts table
        self.spares_table = QTableWidget()
        self.spares_table.setColumnCount(5)
        self.spares_table.setHorizontalHeaderLabels([
            "Part ID", "Name", "Available Quantity", "Required Quantity", "Location"
        ])
        self.spares_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        self.spares_table.setMinimumHeight(150)
        self.form_layout.addRow(self.spares_table)
        
        # Spare part selection controls
        spare_controls = QHBoxLayout()
        self.spare_combo = QComboBox()
        self.spare_combo.setMinimumWidth(300)
        self.spare_quantity_spin = QSpinBox()
        self.spare_quantity_spin.setMinimum(1)
        add_spare_btn = QPushButton("Add Spare Part")
        add_spare_btn.clicked.connect(self.add_spare)
        remove_spare_btn = QPushButton("Remove Selected")
        remove_spare_btn.clicked.connect(lambda: self.remove_selected(self.spares_table))
        
        spare_controls.addWidget(QLabel("Select Spare Part:"))
        spare_controls.addWidget(self.spare_combo)
        spare_controls.addWidget(QLabel("Quantity:"))
        spare_controls.addWidget(self.spare_quantity_spin)
        spare_controls.addWidget(add_spare_btn)
        spare_controls.addWidget(remove_spare_btn)
        self.form_layout.addRow(spare_controls)
        
        # Notes section
        self.form_layout.addRow(QLabel("<b>Additional Notes</b>"))
        
        self.notes_edit = QTextEdit()
        self.notes_edit.setMinimumHeight(80)
        self.form_layout.addRow("Notes:", self.notes_edit)
        
        # Add content widget to scroll area
        scroll.setWidget(content_widget)
        layout.addWidget(scroll)
        
        # Buttons
        buttons_layout = QHBoxLayout()
        
        self.save_btn = QPushButton("Save Work Order")
        self.save_btn.clicked.connect(self.save_work_order)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        
        buttons_layout.addWidget(self.save_btn)
        buttons_layout.addWidget(cancel_btn)
        layout.addLayout(buttons_layout)
        
        # After setting up the UI, load available tools and spares
        self.load_available_tools()
        self.load_available_spares()
    
    def load_equipment_list(self):
        """Load equipment list into combo box"""
        equipment_list = self.db_manager.get_all_equipment()
        
        for equipment in equipment_list:
            self.equipment_combo.addItem(
                f"{equipment['equipment_name']} ({equipment['equipment_id']})",
                equipment['equipment_id']
            )
    
    def load_craftsmen_list(self):
        """Load craftsmen list into combo box"""
        craftsmen_list = self.db_manager.get_all_craftsmen()
        
        for craftsman in craftsmen_list:
            self.craftsman_combo.addItem(
                f"{craftsman['first_name']} {craftsman['last_name']}",
                craftsman['craftsman_id']
            )
    
    def on_status_changed(self, status):
        """Handle status change"""
        # Enable completion date only if status is Completed
        self.completed_date_edit.setEnabled(status == "Completed")
        
        # If changing to Completed, set completion date to today
        if status == "Completed" and not self.is_edit_mode:
            self.completed_date_edit.setDate(QDate.currentDate())
    
    def load_available_tools(self):
        """Load available tools into the combo box"""
        tools = self.db_manager.get_inventory_items_by_category('Tool')
        self.tool_combo.clear()
        for tool in tools:
            if tool['quantity'] > 0:  # Only show available tools
                self.tool_combo.addItem(
                    f"{tool['name']} (Available: {tool['quantity']})",
                    tool
                )
        self.update_tool_quantity_limit()
        self.tool_combo.currentIndexChanged.connect(self.update_tool_quantity_limit)

    def load_available_spares(self):
        """Load available spare parts into the combo box"""
        spares = self.db_manager.get_inventory_items()
        self.spare_combo.clear()
        for spare in spares:
            if spare['category'] != 'Tool' and spare['quantity'] > 0:  # Only show available non-tool items
                self.spare_combo.addItem(
                    f"{spare['name']} (Available: {spare['quantity']})",
                    spare
                )
        self.update_spare_quantity_limit()
        self.spare_combo.currentIndexChanged.connect(self.update_spare_quantity_limit)

    def update_tool_quantity_limit(self):
        """Update the tool quantity spinner maximum based on selected tool"""
        if self.tool_combo.currentData():
            available = self.tool_combo.currentData()['quantity']
            self.tool_quantity_spin.setMaximum(available)
            self.tool_quantity_spin.setValue(min(1, available))

    def update_spare_quantity_limit(self):
        """Update the spare quantity spinner maximum based on selected spare part"""
        if self.spare_combo.currentData():
            available = self.spare_combo.currentData()['quantity']
            self.spare_quantity_spin.setMaximum(available)
            self.spare_quantity_spin.setValue(min(1, available))

    def add_tool(self):
        """Add selected tool to the tools table"""
        tool_data = self.tool_combo.currentData()
        if not tool_data:
            return

        quantity = self.tool_quantity_spin.value()
        
        # Check if tool is already in table
        for row in range(self.tools_table.rowCount()):
            if self.tools_table.item(row, 0).text() == str(tool_data['item_id']):
                QMessageBox.warning(self, "Warning", "This tool is already added!")
                return

        # Add new row
        row = self.tools_table.rowCount()
        self.tools_table.insertRow(row)
        
        self.tools_table.setItem(row, 0, QTableWidgetItem(str(tool_data['item_id'])))
        self.tools_table.setItem(row, 1, QTableWidgetItem(tool_data['name']))
        self.tools_table.setItem(row, 2, QTableWidgetItem(str(tool_data['quantity'])))
        self.tools_table.setItem(row, 3, QTableWidgetItem(str(quantity)))
        self.tools_table.setItem(row, 4, QTableWidgetItem(tool_data.get('location', '')))
        
        # Add to selected tools list
        self.selected_tools.append({
            'item_id': tool_data['item_id'],
            'quantity': quantity
        })

    def add_spare(self):
        """Add selected spare part to the spares table"""
        spare_data = self.spare_combo.currentData()
        if not spare_data:
            return

        quantity = self.spare_quantity_spin.value()
        
        # Check if spare is already in table
        for row in range(self.spares_table.rowCount()):
            if self.spares_table.item(row, 0).text() == str(spare_data['item_id']):
                QMessageBox.warning(self, "Warning", "This spare part is already added!")
                return

        # Add new row
        row = self.spares_table.rowCount()
        self.spares_table.insertRow(row)
        
        self.spares_table.setItem(row, 0, QTableWidgetItem(str(spare_data['item_id'])))
        self.spares_table.setItem(row, 1, QTableWidgetItem(spare_data['name']))
        self.spares_table.setItem(row, 2, QTableWidgetItem(str(spare_data['quantity'])))
        self.spares_table.setItem(row, 3, QTableWidgetItem(str(quantity)))
        self.spares_table.setItem(row, 4, QTableWidgetItem(spare_data.get('location', '')))
        
        # Add to selected spares list
        self.selected_spares.append({
            'item_id': spare_data['item_id'],
            'quantity': quantity
        })

    def remove_selected(self, table):
        """Remove selected row from the specified table"""
        selected_rows = set(item.row() for item in table.selectedItems())
        
        # Remove rows in reverse order to avoid index shifting
        for row in sorted(selected_rows, reverse=True):
            item_id = int(table.item(row, 0).text())
            
            # Remove from selected lists
            if table == self.tools_table:
                self.selected_tools = [t for t in self.selected_tools if t['item_id'] != item_id]
            else:
                self.selected_spares = [s for s in self.selected_spares if s['item_id'] != item_id]
            
            table.removeRow(row)

    def save_work_order(self):
        """Save work order data"""
        # Validate required fields
        if not self.title_edit.text().strip():
            QMessageBox.warning(self, "Validation Error", "Title is required!")
            return
        
        # Prepare data
        work_order_data = {
            'title': self.title_edit.text().strip(),
            'description': self.description_edit.toPlainText().strip(),
            'equipment_id': self.equipment_combo.currentData(),
            'craftsman_id': self.craftsman_combo.currentData(),
            'priority': self.priority_combo.currentText(),
            'status': self.status_combo.currentText(),
            'due_date': self.due_date_edit.date().toPython(),
            'estimated_hours': self.estimated_hours_spin.value(),
            'actual_hours': self.actual_hours_spin.value(),
            'tools_required': self.selected_tools,
            'spares_required': self.selected_spares,
            'notes': self.notes_edit.toPlainText().strip()
        }
        
        # Add completed date if status is Completed
        if self.status_combo.currentText() == "Completed":
            work_order_data['completed_date'] = self.completed_date_edit.date().toPython()
        else:
            work_order_data['completed_date'] = None
        
        # Save to database
        if self.is_edit_mode:
            work_order_data['work_order_id'] = self.work_order['work_order_id']
            success = self.db_manager.update_work_order(work_order_data)
            message = "Work order updated successfully!"
        else:
            success = self.db_manager.create_work_order(work_order_data)
            message = "Work order created successfully!"
        
        if success:
            QMessageBox.information(self, "Success", message)
            self.accept()
        else:
            QMessageBox.critical(self, "Error", "Failed to save work order!")

    def load_work_order_data(self):
        """Load work order data into form fields"""
        if not self.work_order:
            return
        
        # Set basic information
        self.title_edit.setText(self.work_order['title'])
        self.description_edit.setText(self.work_order['description'])
        
        # Set equipment
        equipment_index = self.equipment_combo.findData(self.work_order['equipment_id'])
        if equipment_index >= 0:
            self.equipment_combo.setCurrentIndex(equipment_index)
        
        # Set craftsman
        craftsman_index = self.craftsman_combo.findData(self.work_order['craftsman_id'])
        if craftsman_index >= 0:
            self.craftsman_combo.setCurrentIndex(craftsman_index)
        
        # Set priority and status
        self.priority_combo.setCurrentText(self.work_order['priority'])
        self.status_combo.setCurrentText(self.work_order['status'])
        
        # Set dates
        if self.work_order['due_date']:
            self.due_date_edit.setDate(QDate.fromString(str(self.work_order['due_date']), "yyyy-MM-dd"))
        
        if self.work_order['completed_date']:
            self.completed_date_edit.setDate(QDate.fromString(str(self.work_order['completed_date']), "yyyy-MM-dd"))
            self.completed_date_edit.setEnabled(True)
        
        # Set time and cost
        self.estimated_hours_spin.setValue(self.work_order['estimated_hours'] or 0)
        self.actual_hours_spin.setValue(self.work_order['actual_hours'] or 0)
        
        # Load tools and spares if they exist
        if 'tools_required' in self.work_order and self.work_order['tools_required']:
            try:
                tools = json.loads(self.work_order['tools_required']) if isinstance(self.work_order['tools_required'], str) else self.work_order['tools_required']
                for tool in tools:
                    tool_data = self.db_manager.get_inventory_item(tool['item_id'])
                    if tool_data:
                        self.tool_combo.setCurrentText(f"{tool_data['name']} (Available: {tool_data['quantity']})")
                        self.tool_quantity_spin.setValue(tool['quantity'])
                        self.add_tool()
            except json.JSONDecodeError:
                print("Error decoding tools JSON data")
        
        if 'spares_required' in self.work_order and self.work_order['spares_required']:
            try:
                spares = json.loads(self.work_order['spares_required']) if isinstance(self.work_order['spares_required'], str) else self.work_order['spares_required']
                for spare in spares:
                    spare_data = self.db_manager.get_inventory_item(spare['item_id'])
                    if spare_data:
                        self.spare_combo.setCurrentText(f"{spare_data['name']} (Available: {spare_data['quantity']})")
                        self.spare_quantity_spin.setValue(spare['quantity'])
                        self.add_spare()
            except json.JSONDecodeError:
                print("Error decoding spares JSON data")
        
        # Set notes
        self.notes_edit.setText(self.work_order['notes'] or "")
    

    # def load_work_order_data(self):
    #     """Load work order data into form fields"""
    #     if not self.

# class WorkOrderDialog(QDialog):
#     """Dialog for creating or editing a work order"""
#     def __init__(self, db_manager, work_order=None, parent=None):
#         super().__init__(parent)
#         self.db_manager = db_manager
#         self.work_order = work_order
#         self.is_edit_mode = work_order is not None
        
#         self.setWindowTitle("Create Work Order" if not self.is_edit_mode else "Edit Work Order")
#         self.setMinimumWidth(600)
#         self.setMinimumHeight(700)
        
#         self.setup_ui()
        
#         if self.is_edit_mode:
#             self.load_work_order_data()
    
#     def setup_ui(self):
#         """Set up the dialog UI"""
#         layout = QVBoxLayout(self)
        
#         # Create scroll area
#         scroll = QScrollArea()
#         scroll.setWidgetResizable(True)
#         scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
#         # Create content widget
#         content_widget = QWidget()
#         self.form_layout = QFormLayout(content_widget)
        
#         # Basic information section
#         self.form_layout.addRow(QLabel("<b>Basic Information</b>"))
        
#         self.title_edit = QLineEdit()
#         self.form_layout.addRow("Title:", self.title_edit)
        
#         self.description_edit = QTextEdit()
#         self.description_edit.setMinimumHeight(100)
#         self.form_layout.addRow("Description:", self.description_edit)
        
#         # Equipment selection
#         self.equipment_combo = QComboBox()
#         self.load_equipment_list()
#         self.form_layout.addRow("Equipment:", self.equipment_combo)
        
#         # Craftsman selection
#         self.craftsman_combo = QComboBox()
#         self.load_craftsmen_list()
#         self.form_layout.addRow("Assigned To:", self.craftsman_combo)
        
#         # Priority selection
#         self.priority_combo = QComboBox()
#         self.priority_combo.addItems(["Low", "Medium", "High", "Critical"])
#         self.priority_combo.setCurrentText("Medium")  # Default
#         self.form_layout.addRow("Priority:", self.priority_combo)
        
#         # Status selection
#         self.status_combo = QComboBox()
#         self.status_combo.addItems(["Open", "In Progress", "On Hold", "Completed", "Cancelled"])
#         self.form_layout.addRow("Status:", self.status_combo)
        
#         # Dates section
#         self.form_layout.addRow(QLabel("<b>Dates</b>"))
        
#         self.due_date_edit = QDateEdit()
#         self.due_date_edit.setCalendarPopup(True)
#         self.due_date_edit.setDate(QDate.currentDate().addDays(7))  # Default to 1 week from now
#         self.form_layout.addRow("Due Date:", self.due_date_edit)
        
#         self.completed_date_edit = QDateEdit()
#         self.completed_date_edit.setCalendarPopup(True)
#         self.completed_date_edit.setDate(QDate.currentDate())
#         self.completed_date_edit.setEnabled(False)  # Disabled by default
#         self.form_layout.addRow("Completion Date:", self.completed_date_edit)
        
#         # Connect status change to enable/disable completion date
#         self.status_combo.currentTextChanged.connect(self.on_status_changed)
        
#         # Time and cost section
#         self.form_layout.addRow(QLabel("<b>Time and Cost</b>"))
        
#         self.estimated_hours_spin = QSpinBox()
#         self.estimated_hours_spin.setRange(0, 1000)
#         self.estimated_hours_spin.setSuffix(" hours")
#         self.form_layout.addRow("Estimated Hours:", self.estimated_hours_spin)
        
#         self.actual_hours_spin = QSpinBox()
#         self.actual_hours_spin.setRange(0, 1000)
#         self.actual_hours_spin.setSuffix(" hours")
#         self.form_layout.addRow("Actual Hours:", self.actual_hours_spin)
        
#         # Parts and materials section
#         self.form_layout.addRow(QLabel("<b>Parts and Materials</b>"))
        
#         self.parts_edit = QTextEdit()
#         self.parts_edit.setPlaceholderText("List parts and materials used")
#         self.parts_edit.setMinimumHeight(80)
#         self.form_layout.addRow("Parts Used:", self.parts_edit)
        
#         # Notes section
#         self.form_layout.addRow(QLabel("<b>Additional Notes</b>"))
        
#         self.notes_edit = QTextEdit()
#         self.notes_edit.setMinimumHeight(80)
#         self.form_layout.addRow("Notes:", self.notes_edit)
        
#         # Add content widget to scroll area
#         scroll.setWidget(content_widget)
#         layout.addWidget(scroll)
        
#         # Buttons
#         buttons_layout = QHBoxLayout()
        
#         self.save_btn = QPushButton("Save Work Order")
#         self.save_btn.clicked.connect(self.save_work_order)
        
#         cancel_btn = QPushButton("Cancel")
#         cancel_btn.clicked.connect(self.reject)
        
#         buttons_layout.addWidget(self.save_btn)
#         buttons_layout.addWidget(cancel_btn)
#         layout.addLayout(buttons_layout)
    
#     def load_equipment_list(self):
#         """Load equipment list into combo box"""
#         equipment_list = self.db_manager.get_all_equipment()
        
#         for equipment in equipment_list:
#             self.equipment_combo.addItem(
#                 f"{equipment['equipment_name']} ({equipment['equipment_id']})",
#                 equipment['equipment_id']
#             )
    
#     def load_craftsmen_list(self):
#         """Load craftsmen list into combo box"""
#         craftsmen_list = self.db_manager.get_all_craftsmen()
        
#         for craftsman in craftsmen_list:
#             self.craftsman_combo.addItem(
#                 f"{craftsman['first_name']} {craftsman['last_name']}",
#                 craftsman['craftsman_id']
#             )
    
#     def on_status_changed(self, status):
#         """Handle status change"""
#         # Enable completion date only if status is Completed
#         self.completed_date_edit.setEnabled(status == "Completed")
        
#         # If changing to Completed, set completion date to today
#         if status == "Completed" and not self.is_edit_mode:
#             self.completed_date_edit.setDate(QDate.currentDate())
    
#     def save_work_order(self):
#         """Save work order data"""
#         # Validate required fields
#         if not self.title_edit.text().strip():
#             QMessageBox.warning(self, "Validation Error", "Title is required!")
#             return
        
#         # Prepare data
#         work_order_data = {
#             'title': self.title_edit.text().strip(),
#             'description': self.description_edit.toPlainText().strip(),
#             'equipment_id': self.equipment_combo.currentData(),
#             'craftsman_id': self.craftsman_combo.currentData(),
#             'priority': self.priority_combo.currentText(),
#             'status': self.status_combo.currentText(),
#             'due_date': self.due_date_edit.date().toPython(),
#             'estimated_hours': self.estimated_hours_spin.value(),
#             'actual_hours': self.actual_hours_spin.value(),
#             'parts_used': self.parts_edit.toPlainText().strip(),
#             'notes': self.notes_edit.toPlainText().strip()
#         }
        
#         # Add completed date if status is Completed
#         if self.status_combo.currentText() == "Completed":
#             work_order_data['completed_date'] = self.completed_date_edit.date().toPython()
#         else:
#             work_order_data['completed_date'] = None
        
#         # Save to database
#         if self.is_edit_mode:
#             work_order_data['work_order_id'] = self.work_order['work_order_id']
#             success = self.db_manager.update_work_order(work_order_data)
#             message = "Work order updated successfully!"
#         else:
#             success = self.db_manager.create_work_order(work_order_data)
#             message = "Work order created successfully!"
        
#         if success:
#             QMessageBox.information(self, "Success", message)
#             self.accept()
#         else:
#             QMessageBox.critical(self, "Error", "Failed to save work order!") 
