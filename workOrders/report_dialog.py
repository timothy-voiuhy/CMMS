
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QCheckBox
)

class CustomReportDialog(QDialog):
    """Dialog for selecting fields for custom report"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Custom Report")
        self.setMinimumWidth(400)
        
        layout = QVBoxLayout(self)
        
        # Instructions
        label = QLabel("Select fields to include in the report:")
        layout.addWidget(label)
        
        # Field checkboxes
        self.field_checkboxes = {}
        fields = [
            "work_order_id", "title", "description", "equipment_id", "equipment_name",
            "assigned_to", "priority", "status", "created_date", "due_date",
            "completed_date", "estimated_hours", "actual_hours", "parts_used",
            "total_cost", "notes"
        ]
        
        for field in fields:
            checkbox = QCheckBox(field.replace('_', ' ').title())
            checkbox.setChecked(True)  # Default to checked
            self.field_checkboxes[field] = checkbox
            layout.addWidget(checkbox)
        
        # Buttons
        buttons = QHBoxLayout()
        select_all_btn = QPushButton("Select All")
        select_all_btn.clicked.connect(self.select_all)
        
        deselect_all_btn = QPushButton("Deselect All")
        deselect_all_btn.clicked.connect(self.deselect_all)
        
        buttons.addWidget(select_all_btn)
        buttons.addWidget(deselect_all_btn)
        layout.addLayout(buttons)
        
        # OK/Cancel buttons
        dialog_buttons = QHBoxLayout()
        ok_btn = QPushButton("OK")
        ok_btn.clicked.connect(self.accept)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        
        dialog_buttons.addWidget(ok_btn)
        dialog_buttons.addWidget(cancel_btn)
        layout.addLayout(dialog_buttons)
    
    def select_all(self):
        """Select all fields"""
        for checkbox in self.field_checkboxes.values():
            checkbox.setChecked(True)
    
    def deselect_all(self):
        """Deselect all fields"""
        for checkbox in self.field_checkboxes.values():
            checkbox.setChecked(False)
    
    def get_selected_fields(self):
        """Get list of selected fields"""
        return [field for field, checkbox in self.field_checkboxes.items() if checkbox.isChecked()]

