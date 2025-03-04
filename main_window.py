from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                                 QPushButton, QLabel, QStackedWidget, QFrame)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QIcon
from ui.equipment_registration import EquipmentRegistrationWindow
from ui.equipment_list import EquipmentListWindow
from db_manager import DatabaseManager

class CMMSMainWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setWindowTitle("CMMS - Maintenance Management System")
        self.setMinimumSize(1200, 800)
        
        # Initialize database manager
        self.db_manager = DatabaseManager()
        
        # Create central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        
        # Create sidebar for navigation
        sidebar = self.create_sidebar()
        main_layout.addWidget(sidebar)
        
        # Create stacked widget for different pages
        self.stacked_widget = QStackedWidget()
        
        # Create windows
        self.welcome_page = self.create_welcome_page()
        self.equipment_registration = EquipmentRegistrationWindow(self.db_manager)
        self.equipment_list = EquipmentListWindow(self.db_manager)
        
        # Add pages to stacked widget
        self.stacked_widget.addWidget(self.welcome_page)
        self.stacked_widget.addWidget(self.equipment_registration)
        self.stacked_widget.addWidget(self.equipment_list)
        
        # Connect the registration signal to list refresh
        self.equipment_registration.equipment_registered.connect(self.equipment_list.load_equipment)
        
        main_layout.addWidget(self.stacked_widget)
        
        # Set layout proportions
        main_layout.setStretch(0, 1)  # Sidebar takes 1 part
        main_layout.setStretch(1, 4)  # Main content takes 4 parts

    def create_sidebar(self):
        sidebar = QFrame()
        sidebar.setFrameStyle(QFrame.Shape.StyledPanel | QFrame.Shadow.Raised)
        sidebar.setStyleSheet("""
            QFrame {
                background-color: #2c3e50;
                border-radius: 10px;
                margin: 5px;
            }
            QPushButton {
                background-color: transparent;
                border: none;
                color: white;
                text-align: left;
                padding: 10px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #34495e;
                border-radius: 5px;
            }
            QPushButton:checked {
                background-color: #3498db;
                border-radius: 5px;
            }
        """)
        
        layout = QVBoxLayout(sidebar)
        
        # Add logo/title
        title = QLabel("CMMS")
        title.setStyleSheet("color: white; font-size: 24px; font-weight: bold; padding: 20px;")
        layout.addWidget(title)
        
        # Add navigation buttons
        self.nav_buttons = []
        
        home_btn = self.create_nav_button("Home", 0)
        equipment_btn = self.create_nav_button("Equipment Registration", 1)
        equipment_list_btn = self.create_nav_button("Equipments", 2)
        
        layout.addWidget(home_btn)
        layout.addWidget(equipment_btn)
        layout.addWidget(equipment_list_btn)
        
        # Add stretch to push buttons to top
        layout.addStretch()
        
        return sidebar

    def create_nav_button(self, text, page_index):
        button = QPushButton(text)
        button.setCheckable(True)
        button.clicked.connect(lambda: self.change_page(page_index, button))
        self.nav_buttons.append(button)
        if page_index == 0:
            button.setChecked(True)
        return button

    def change_page(self, index, button):
        self.stacked_widget.setCurrentIndex(index)
        # Update button states
        for btn in self.nav_buttons:
            btn.setChecked(btn == button)

    def create_welcome_page(self):
        welcome_widget = QWidget()
        welcome_widget.setStyleSheet("""
            QWidget {
                background-color: #f5f6fa;
            }
            QLabel {
                color: #2c3e50;
            }
            .feature-box {
                background-color: white;
                border-radius: 10px;
                padding: 20px;
                margin: 10px;
            }
        """)
        
        layout = QVBoxLayout(welcome_widget)
        
        # Welcome header
        header = QLabel("Welcome to CMMS")
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header.setFont(QFont("Arial", 24, QFont.Weight.Bold))
        layout.addWidget(header)
        
        # Subtitle
        subtitle = QLabel("Computerized Maintenance Management System")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setFont(QFont("Arial", 14))
        layout.addWidget(subtitle)
        
        # Features section
        features_layout = QHBoxLayout()
        
        # Feature boxes
        features = [
            ("Equipment Management", "Register and track all your equipment with detailed information"),
            ("Maintenance Tracking", "Schedule and monitor maintenance tasks efficiently"),
            ("Custom Fields", "Add custom fields to track specific equipment attributes")
        ]
        
        for title, description in features:
            feature_box = QFrame()
            feature_box.setProperty("class", "feature-box")
            feature_box.setStyleSheet("""
                QFrame {
                    background-color: white;
                    border-radius: 10px;
                    padding: 20px;
                    margin: 10px;
                }
            """)
            
            box_layout = QVBoxLayout(feature_box)
            
            title_label = QLabel(title)
            title_label.setFont(QFont("Arial", 16, QFont.Weight.Bold))
            title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            
            desc_label = QLabel(description)
            desc_label.setWordWrap(True)
            desc_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            
            box_layout.addWidget(title_label)
            box_layout.addWidget(desc_label)
            
            features_layout.addWidget(feature_box)
        
        layout.addLayout(features_layout)
        layout.addStretch()
        
        return welcome_widget

    def closeEvent(self, event):
        # self.db_manager.close()
        super().closeEvent(event)
        