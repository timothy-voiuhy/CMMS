"""
Inventory Personnel Login Dialog - For inventory personnel to access the portal
"""

from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
                              QLineEdit, QMessageBox, QCheckBox, QFormLayout)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QIcon

class InventoryPersonnelLoginDialog(QDialog):
    """Dialog for inventory personnel login"""
    
    def __init__(self, db_manager, parent=None):
        super().__init__(parent)
        self.db_manager = db_manager
        self.personnel_id = None
        
        self.setWindowTitle("Inventory Personnel Portal Login")
        self.setMinimumWidth(400)
        
        layout = QVBoxLayout(self)
        
        # Header
        header_label = QLabel("Inventory Personnel Portal Login")
        header_label.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        header_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(header_label)
        
        # Form layout
        form_layout = QFormLayout()
        
        # Employee ID field
        self.employee_id = QLineEdit()
        self.employee_id.setPlaceholderText("Enter your Employee ID")
        form_layout.addRow("Employee ID:", self.employee_id)
        
        # Password field
        self.password = QLineEdit()
        self.password.setPlaceholderText("Enter your password")
        self.password.setEchoMode(QLineEdit.EchoMode.Password)
        form_layout.addRow("Password:", self.password)
        
        # Remember me checkbox
        self.remember_me = QCheckBox("Remember me")
        form_layout.addRow("", self.remember_me)
        
        layout.addLayout(form_layout)
        
        # Buttons
        buttons_layout = QHBoxLayout()
        
        login_btn = QPushButton("Login")
        login_btn.clicked.connect(self.login)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        
        buttons_layout.addWidget(login_btn)
        buttons_layout.addWidget(cancel_btn)
        
        layout.addLayout(buttons_layout)
    
    def login(self):
        """Handle login attempt"""
        employee_id = self.employee_id.text().strip()
        password = self.password.text()
        
        # DEVELOPMENT MODE: Allow bypass with special employee ID
        if employee_id.lower() == "dev":
            # Use a default personnel ID for development
            self.personnel_id = 1
            QMessageBox.information(self, "Development Mode", "Logging in with development bypass")
            self.accept()
            return
        
        if not employee_id:
            QMessageBox.warning(self, "Login Error", "Please enter your Employee ID")
            return
        
        # Get personnel by employee ID
        personnel = self.db_manager.get_personnel_by_employee_id(employee_id)
        
        if personnel:
            # For demo purposes, we'll accept any password
            # In a real application, you would verify the password
            self.personnel_id = personnel['personnel_id']
            self.accept()
        else:
            QMessageBox.warning(self, "Login Error", "Invalid Employee ID or password")
    
    def get_personnel_id(self):
        """Return the authenticated personnel ID"""
        return self.personnel_id