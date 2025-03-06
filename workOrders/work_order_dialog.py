from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QLabel, QLineEdit, 
    QTextEdit, QComboBox, QDateEdit, QSpinBox, QPushButton, QScrollArea,
    QWidget, QMessageBox
)
from PySide6.QtCore import Qt, QDate

class WorkOrderDialog(QDialog):
    """Dialog for creating or editing a work order"""
    def __init__(self, db_manager, work_order=None, parent=None):
        super().__init__(parent)
        self.db_manager = db_manager
        self.work_order = work_order
        self.is_edit_mode = work_order is not None
        
        self.setWindowTitle("Create Work Order" if not self.is_edit_mode else "Edit Work Order")
        self.setMinimumWidth(600)
        self.setMinimumHeight(700)
        
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
        
        # Parts and materials section
        self.form_layout.addRow(QLabel("<b>Parts and Materials</b>"))
        
        self.parts_edit = QTextEdit()
        self.parts_edit.setPlaceholderText("List parts and materials used")
        self.parts_edit.setMinimumHeight(80)
        self.form_layout.addRow("Parts Used:", self.parts_edit)
        
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
            'parts_used': self.parts_edit.toPlainText().strip(),
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
        
        # Set parts and notes
        self.parts_edit.setText(self.work_order['parts_used'] or "")
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
