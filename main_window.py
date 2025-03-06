from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                                 QPushButton, QLabel, QStackedWidget, QFrame, QGridLayout, QMessageBox, QScrollArea, QSizePolicy)
from PySide6.QtCore import Qt, Slot, QSize, QTimer, QEvent, QPoint, QPropertyAnimation, QEasingCurve
from PySide6.QtGui import QFont, QIcon, QPixmap, QEnterEvent
from ui.equipment_registration import EquipmentRegistrationWindow
from ui.equipment_list import EquipmentListWindow
from craftsmen import CraftsMenWindow
from workOrders.work_orders import WorkOrdersWindow
from inventory import InventoryWindow
from db_manager import DatabaseManager
from styles.theme_settings_widget import ThemeSettingsWidget
from styles.dark_theme import DarkTheme
from styles.theme_config import ThemeConfig
from ui.equipments_window import EquipmentsWindow
from notifications import EmailNotificationService
from craftsman_portal import CraftsmanPortal
from craftsman_login import CraftsmanLoginDialog

class CMMSMainWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setWindowTitle("CMMS - Maintenance Management System")
        # Remove or comment out the setMinimumSize line as it might interfere
        # self.setMinimumSize(1200, 800)
        
        # Add this line to ensure window starts maximized
        self.setWindowState(Qt.WindowState.WindowMaximized)
        
        # Create menu bar
        self.create_menu_bar()
        
        # Initialize database manager
        self.db_manager = DatabaseManager()
        
        # Create central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        self.main_layout = QVBoxLayout(central_widget)  # Changed to VBoxLayout
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        
        # Create stacked widget for different pages
        self.stacked_widget = QStackedWidget()
        
        # Create windows
        self.welcome_page = self.create_welcome_page()
        self.equipments_window = EquipmentsWindow(self.db_manager)
        self.craftsmen_window = CraftsMenWindow(db_manager=self.db_manager, parent=self)
        self.work_orders_window = WorkOrdersWindow(db_manager=self.db_manager, parent=self)
        self.inventory_window = InventoryWindow(db_manager=self.db_manager, parent=self)

        # Add pages to stacked widget
        self.stacked_widget.addWidget(self.welcome_page)
        self.stacked_widget.addWidget(self.equipments_window)
        self.stacked_widget.addWidget(self.craftsmen_window)
        self.stacked_widget.addWidget(self.work_orders_window)
        self.stacked_widget.addWidget(self.inventory_window)
        
        self.main_layout.addWidget(self.stacked_widget)
        
        self.setStyleSheet(DarkTheme.get_stylesheet())
        self.load_saved_theme()

        # In the MainWindow.__init__ method, after initializing the db_manager:
        self.notification_service = EmailNotificationService(self.db_manager)
        if self.notification_service.is_enabled():
            self.notification_service.start_scheduler()

    def create_welcome_page(self):
        welcome_widget = QWidget()
        welcome_widget.setStyleSheet("""
            QWidget {
                background-color: #1e1e1e;
                color: #e0e0e0;
            }
            QLabel {
                color: #e0e0e0;
            }
            .feature-box {
                background-color: #2a2a2a;
                border-radius: 10px;
                padding: 30px;  /* Increased padding */
                margin: 15px;   /* Increased margin */
                border: 1px solid #3a3a3a;
                min-height: 200px;  /* Set minimum height */
                min-width: 250px;   /* Set minimum width */
            }
            .feature-box:hover {
                background-color: #3a3a3a;
                border: 1px solid #4a4a4a;
            }
            QScrollArea {
                background-color: #1e1e1e;
                border: none;
            }
            QScrollBar:vertical {
                background: #2a2a2a;
                width: 12px;
            }
            QScrollBar::handle:vertical {
                background: #404040;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical:hover {
                background: #4a4a4a;
            }
        """)
        
        main_layout = QVBoxLayout(welcome_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)
        
        # Welcome header with improved styling
        header_container = QWidget()
        header_layout = QVBoxLayout(header_container)
        header_layout.setContentsMargins(0, 0, 0, 0)
        
        header = QLabel("Welcome to CMMS")
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header.setFont(QFont("Arial", 28, QFont.Weight.Bold))
        header.setStyleSheet("color: #e0e0e0; margin-bottom: 10px;")
        
        subtitle = QLabel("Computerized Maintenance Management System")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setFont(QFont("Arial", 16))
        subtitle.setStyleSheet("color: #a0a0a0;")
        
        header_layout.addWidget(header)
        header_layout.addWidget(subtitle)
        
        # Add a separator line
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        separator.setStyleSheet("background-color: #3a3a3a; margin: 20px 0;")
        
        main_layout.addWidget(header_container)
        main_layout.addWidget(separator)
        
        # Create scroll area for features
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        
        # Create content widget for scroll area
        features_container = QWidget()
        features_layout = QVBoxLayout(features_container)
        features_layout.setContentsMargins(5, 5, 5, 5)
        
        # Features grid layout
        grid_layout = QGridLayout()
        grid_layout.setSpacing(15)
        
        # Feature boxes - updated to include Work Orders
        features = [
            ("Equipment Management", "Register and track all your equipment with detailed information", 
             "icons/equipment.png", 1),  # Navigate to Equipment tab
            ("Craftsmen", "Manage technicians and their skills, certifications, and assignments", 
             "icons/craftsman.png", 2),  # Navigate to Craftsmen tab
            ("Work Orders", "Create and track maintenance work orders from request to completion", 
             "icons/workorder.png", 3),  # Navigate to Work Orders tab
            ("Preventive Maintenance", "Schedule and manage routine maintenance tasks", 
             "icons/maintenance.png", 4),  # Navigate to PM tab (future)
            ("Inventory", "Track spare parts and supplies for maintenance operations", 
             "icons/inventory.png", 5),  # Navigate to Inventory tab (future)
            ("Reports & Analytics", "Generate reports and analyze maintenance performance", 
             "icons/reports.png", 6),  # Navigate to Reports tab (future)
        ]
        
        # Create clickable feature boxes
        self.feature_boxes = []
        row, col = 0, 0
        
        for title, description, icon_path, page_index in features:
            feature_box = self.create_feature_box(title, description, icon_path, page_index)
            grid_layout.addWidget(feature_box, row, col)
            self.feature_boxes.append(feature_box)
            
            # Update grid position
            col += 1
            if col > 1:  # 2 columns
                col = 0
                row += 1
        
        # Add Craftsman Portal button
        craftsman_portal_box = self.create_feature_box(
            "Craftsman Portal", 
            "Access the craftsman portal to view and update work orders", 
            "icons/craftsman_portal.png",
            7  # New page index for direct access
        )
        grid_layout.addWidget(craftsman_portal_box, row+1, 0, 1, 2)  # Span two columns
        self.feature_boxes.append(craftsman_portal_box)
        
        # Add inventory feature box
        inventory_box = self.create_feature_box(
            "Inventory Management",
            "Track spare parts, tools, and supplies for maintenance operations",
            "icons/inventory.png",
            5  # Page index for inventory
        )
        grid_layout.addWidget(inventory_box, row+1, 1, 1, 2)  # Add to grid at appropriate position
        
        features_layout.addLayout(grid_layout)
        
        # Set the features container as the scroll area's widget
        scroll_area.setWidget(features_container)
        
        # Add scroll area to main layout with stretch factor
        main_layout.addWidget(scroll_area, 1)  # This will make the scroll area take available space
        
        # Add a status section at the bottom
        status_container = QWidget()
        status_container.setStyleSheet("""
            background-color: #2a2a2a;
            border-radius: 10px;
            padding: 15px;
            margin-top: 20px;
        """)
        status_layout = QHBoxLayout(status_container)
        
        status_label = QLabel("System Status: Ready")
        status_label.setStyleSheet("color: #4CAF50; font-weight: bold;")
        
        version_label = QLabel("Version 1.0.0")
        version_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        version_label.setStyleSheet("color: #a0a0a0;")
        
        status_layout.addWidget(status_label)
        status_layout.addWidget(version_label)
        
        main_layout.addWidget(status_container)
        
        return welcome_widget

    def create_feature_box(self, title, description, icon_path, page_index):
        """Create a clickable feature box that navigates to the specified page on double-click"""
        feature_box = QFrame()
        feature_box.setProperty("class", "feature-box")
        feature_box.setCursor(Qt.CursorShape.PointingHandCursor)  # Change cursor to hand when hovering
        feature_box.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)  # Allow box to expand
        
        # Store the page index for navigation
        feature_box.setProperty("page_index", page_index)
        
        box_layout = QVBoxLayout(feature_box)
        box_layout.setSpacing(15)  # Increased spacing
        box_layout.setContentsMargins(15, 15, 15, 15)  # Add internal margins
        
        # Add icon if available - with improved error handling and path resolution
        icon_label = QLabel()
        
        # Try multiple approaches to load the icon
        icon_loaded = False
        
        # First, try the direct path
        try:
            icon = QIcon(icon_path)
            if not icon.isNull():
                pixmap = icon.pixmap(QSize(64, 64))  # Increased icon size
                icon_label.setPixmap(pixmap)
                icon_loaded = True
        except:
            pass
        
        # If that fails, try with resource path
        if not icon_loaded:
            try:
                # Try with project root
                import os
                project_root = os.path.dirname(os.path.abspath(__file__))
                full_path = os.path.join(project_root, icon_path)
                
                icon = QIcon(full_path)
                if not icon.isNull():
                    pixmap = icon.pixmap(QSize(64, 64))  # Increased icon size
                    icon_label.setPixmap(pixmap)
                    icon_loaded = True
            except:
                pass
        
        # If icon loaded successfully, add it to layout
        if icon_loaded:
            icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            box_layout.addWidget(icon_label)
        else:
            # If icon loading fails, add a placeholder or text indicator
            placeholder = QLabel("📊")  # Unicode icon as fallback
            placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
            placeholder.setStyleSheet("font-size: 48px; color: #4a7ab3;")  # Increased font size
            box_layout.addWidget(placeholder)
        
        title_label = QLabel(title)
        title_label.setFont(QFont("Arial", 18, QFont.Weight.Bold))  # Increased font size
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("color: #e0e0e0;")
        
        desc_label = QLabel(description)
        desc_label.setFont(QFont("Arial", 12))  # Increased font size
        desc_label.setWordWrap(True)
        desc_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        desc_label.setStyleSheet("color: #a0a0a0;")
        
        box_layout.addWidget(title_label)
        box_layout.addSpacing(10)  # Add space between title and description
        box_layout.addWidget(desc_label)
        box_layout.addStretch()  # Push content to the top
        
        # Connect mouse double-click event to navigation instead of single click
        feature_box.mouseDoubleClickEvent = lambda event, box=feature_box: self.navigate_from_feature_box(box)
        
        return feature_box

    def navigate_from_feature_box(self, box):
        """Navigate to the page associated with the clicked feature box"""
        page_index = box.property("page_index")
        
        # Check if the page exists
        if 0 <= page_index < self.stacked_widget.count():
            self.stacked_widget.setCurrentIndex(page_index)
        elif page_index == 7:  # Craftsman Portal
            self.open_craftsman_portal()
        else:
            # For future features, show a "coming soon" message
            title = box.findChild(QLabel).text()
            if title == "Work Orders":
                self.stacked_widget.setCurrentIndex(3)  # Work Orders index
            else:
                QMessageBox.information(
                    self,
                    "Coming Soon",
                    f"The {title} feature is coming soon!"
                )

    def closeEvent(self, event):
        # Stop the notification scheduler if it's running
        if hasattr(self, 'notification_service'):
            self.notification_service.stop_scheduler()
        
        # Continue with existing close event handling
        event.accept()
        
    @Slot()
    def show_theme_settings(self):
        """Show theme settings dialog"""
        if not hasattr(self, 'theme_settings'):
            self.theme_settings = ThemeSettingsWidget(DarkTheme)
            self.theme_settings.setStyleSheet(self.styleSheet())
            self.theme_settings.theme_updated.connect(self.apply_theme_settings)
        
        self.theme_settings.show()

    @Slot(dict)
    def apply_theme_settings(self, settings: dict):
        """Apply updated theme settings"""
        colors = settings['colors']
        border_radius = settings['border_radius']
        
        # Update DarkTheme colors
        DarkTheme.COLORS.update(colors)
        
        # Apply updated stylesheet
        self.setStyleSheet(DarkTheme.get_stylesheet())
        
        # Apply to all child windows
        for window in self.findChildren(QWidget):
            window.setStyleSheet(DarkTheme.get_stylesheet())

    def load_saved_theme(self):
        """Load saved theme configuration"""
        
        theme_config = ThemeConfig()
        current_theme = theme_config.get_current_theme()
        
        if current_theme:
            # Update DarkTheme colors
            DarkTheme.COLORS.update(current_theme['colors'])
            
            # Apply theme
            self.setStyleSheet(DarkTheme.get_stylesheet())

    def create_menu_bar(self):
        """Create the main menu bar with navigation options"""
        menu_bar = self.menuBar()
        
        # File menu
        file_menu = menu_bar.addMenu("File")
        
        exit_action = file_menu.addAction("Exit")
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        
        # Navigation menu
        nav_menu = menu_bar.addMenu("Navigation")
        
        # Add navigation actions
        home_action = nav_menu.addAction("Home")
        home_action.setShortcut("Ctrl+1")
        home_action.triggered.connect(lambda: self.stacked_widget.setCurrentIndex(0))
        
        equipment_action = nav_menu.addAction("Equipment")
        equipment_action.setShortcut("Ctrl+2")
        equipment_action.triggered.connect(lambda: self.stacked_widget.setCurrentIndex(1))
        
        craftsmen_action = nav_menu.addAction("Craftsmen")
        craftsmen_action.setShortcut("Ctrl+3")
        craftsmen_action.triggered.connect(lambda: self.stacked_widget.setCurrentIndex(2))
        
        work_orders_action = nav_menu.addAction("Work Orders")
        work_orders_action.setShortcut("Ctrl+4")
        work_orders_action.triggered.connect(lambda: self.stacked_widget.setCurrentIndex(3))
        
        # Add Craftsman Portal action
        craftsman_portal_action = nav_menu.addAction("Craftsman Portal")
        craftsman_portal_action.setShortcut("Ctrl+5")
        craftsman_portal_action.triggered.connect(self.open_craftsman_portal)
        
        # Add Web Portal action to the Navigation menu
        web_portal_action = nav_menu.addAction("Launch Web Portal")
        web_portal_action.triggered.connect(self.launch_web_portal)
        
        # Add inventory to Navigation menu
        inventory_action = nav_menu.addAction("Inventory")
        inventory_action.setShortcut("Ctrl+5")
        inventory_action.triggered.connect(lambda: self.stacked_widget.setCurrentIndex(4))
        
        # View menu
        view_menu = menu_bar.addMenu("View")
        
        # Theme settings action
        theme_action = view_menu.addAction("Theme Settings")
        theme_action.triggered.connect(self.show_theme_settings)
        
        # Help menu
        help_menu = menu_bar.addMenu("Help")
        
        about_action = help_menu.addAction("About")
        about_action.triggered.connect(self.show_about_dialog)

    def show_about_dialog(self):
        """Show the About dialog"""
        QMessageBox.about(
            self,
            "About CMMS",
            """<h1>CMMS - Computerized Maintenance Management System</h1>
            <p>Version 1.0.0</p>
            <p>A comprehensive system for managing equipment maintenance, craftsmen, and work orders.</p>
            <p>Features:</p>
            <ul>
                <li>Equipment Management - Track all your equipment and maintenance history</li>
                <li>Craftsmen Management - Manage technicians, skills, and team assignments</li>
                <li>Work Orders - Create, assign, and track maintenance work orders</li>
                <li>Reporting - Generate detailed reports and analytics</li>
            </ul>
            <p>&copy; 2023 Your Organization</p>"""
        )

    def open_craftsman_portal(self):
        """Open the craftsman portal with login dialog"""
        # DEVELOPMENT MODE: Uncomment the next lines to bypass login dialog
        # portal = CraftsmanPortal(self.db_manager, craftsman_id=1)  # Use a valid craftsman ID
        # portal.show()
        # return
        
        # Create a login dialog
        login_dialog = CraftsmanLoginDialog(self.db_manager, self)
        if login_dialog.exec():
            # If login successful, open the portal with the craftsman ID
            craftsman_id = login_dialog.get_craftsman_id()
            if craftsman_id:
                portal = CraftsmanPortal(self.db_manager, craftsman_id, parent=self)
                portal.show()

    def launch_web_portal(self):
        """Launch the web-based craftsman portal"""
        try:
            import threading
            from webportal import start_web_portal
            
            # Show information dialog
            QMessageBox.information(
                self,
                "Web Portal",
                "Starting the web-based craftsman portal...\n\n"
                "Craftsmen can access the portal at:\n"
                "http://localhost:5000\n\n"
                "The portal will run until the application is closed."
            )
            
            # Start the web portal in a separate thread
            portal_thread = threading.Thread(
                target=start_web_portal,
                kwargs={'debug': False},
                daemon=True  # This ensures the thread will exit when the main program exits
            )
            portal_thread.start()
            
            # Store the thread reference
            self.portal_thread = portal_thread
            
        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                f"Failed to start web portal: {str(e)}\n\n"
                "Make sure Flask is installed by running:\n"
                "pip install flask flask-login"
            )
