from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                              QLineEdit, QPushButton, QComboBox, QMessageBox,
                              QFrame, QCheckBox)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QIcon, QPixmap, QFont

class LoginWindow(QDialog):
    """Login window for CMMS system authentication"""
    
    def __init__(self, db_manager, parent=None):
        super().__init__(parent)
        self.db_manager = db_manager
        self.user_info = None
        
        self.setWindowTitle("CMMS Login")
        self.setMinimumWidth(400)
        self.setWindowFlags(Qt.WindowType.WindowCloseButtonHint | Qt.WindowType.MSWindowsFixedSizeDialogHint)
        
        self.setup_ui()
        
    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(30, 30, 30, 30)
        
        # Logo and header
        header_layout = QVBoxLayout()
        
        # Logo (you can replace with your actual logo)
        try:
            logo_label = QLabel()
            logo_pixmap = QPixmap("icons/cmms_logo.png")
            if not logo_pixmap.isNull():
                logo_label.setPixmap(logo_pixmap.scaled(100, 100, Qt.AspectRatioMode.KeepAspectRatio))
                logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                header_layout.addWidget(logo_label)
        except:
            pass  # If logo loading fails, just skip it
        
        # Title
        title_label = QLabel("CMMS System Login")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        header_layout.addWidget(title_label)
        
        # Subtitle
        subtitle_label = QLabel("Please enter your credentials to access the system")
        subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle_label.setFont(QFont("Arial", 10))
        header_layout.addWidget(subtitle_label)
        
        main_layout.addLayout(header_layout)
        
        # Separator
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        main_layout.addWidget(separator)
        
        # User type selection
        user_type_layout = QHBoxLayout()
        user_type_label = QLabel("User Type:")
        self.user_type_combo = QComboBox()
        self.user_type_combo.addItems(["Administrator", "Maintenance Manager", "Technician", "Inventory Personnel"])
        self.user_type_combo.setCurrentIndex(0)  # Default to Administrator
        
        user_type_layout.addWidget(user_type_label)
        user_type_layout.addWidget(self.user_type_combo)
        main_layout.addLayout(user_type_layout)
        
        # Username
        username_layout = QHBoxLayout()
        username_label = QLabel("Username:")
        self.username_edit = QLineEdit()
        self.username_edit.setPlaceholderText("Enter your username")
        
        username_layout.addWidget(username_label)
        username_layout.addWidget(self.username_edit)
        main_layout.addLayout(username_layout)
        
        # Password
        password_layout = QHBoxLayout()
        password_label = QLabel("Password:")
        self.password_edit = QLineEdit()
        self.password_edit.setPlaceholderText("Enter your password")
        self.password_edit.setEchoMode(QLineEdit.EchoMode.Password)
        
        password_layout.addWidget(password_label)
        password_layout.addWidget(self.password_edit)
        main_layout.addLayout(password_layout)
        
        # Remember me checkbox
        self.remember_checkbox = QCheckBox("Remember me")
        main_layout.addWidget(self.remember_checkbox)
        
        # Buttons
        buttons_layout = QHBoxLayout()
        
        self.login_button = QPushButton("Login")
        self.login_button.setDefault(True)
        self.login_button.clicked.connect(self.validate_login)
        
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        
        buttons_layout.addWidget(self.login_button)
        buttons_layout.addWidget(self.cancel_button)
        
        main_layout.addLayout(buttons_layout)
        
        # Set focus to username field
        self.username_edit.setFocus()
        
    def validate_login(self):
        """Validate user credentials"""
        username = self.username_edit.text().strip()
        password = self.password_edit.text()
        user_type = self.user_type_combo.currentText()
        
        if not username or not password:
            QMessageBox.warning(
                self,
                "Login Failed",
                "Please enter both username and password."
            )
            return
        
        # For development/testing purposes, allow a backdoor login
        # In production, you would remove this and use only database validation
        if username == "admin" and password == "admin":
            self.user_info = {
                "id": 1,
                "username": username,
                "user_type": "Administrator",
                "full_name": "System Administrator"
            }
            self.accept()
            return
            
        # Validate against database
        # This assumes you have a method in your DatabaseManager to validate users
        # You'll need to implement this method based on your database structure
        user = self.db_manager.validate_user(username, password, user_type)
        
        if user:
            self.user_info = user
            self.accept()
        else:
            QMessageBox.warning(
                self,
                "Login Failed",
                "Invalid username or password. Please try again."
            )
    
    def get_user_info(self):
        """Return the authenticated user information"""
        return self.user_info 