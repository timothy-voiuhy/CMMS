from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                                 QPushButton, QLabel, QStackedWidget, QFrame, QGridLayout, QMessageBox, QScrollArea, QSizePolicy, QInputDialog, QLineEdit, QApplication)
from PySide6.QtCore import Qt, Slot, QSize, QTimer, QEvent, QPoint, QPropertyAnimation, QEasingCurve
from PySide6.QtGui import QFont, QIcon, QPixmap, QEnterEvent
from ui.equipment_registration import EquipmentRegistrationWindow
from ui.equipment_list import EquipmentListWindow
from craftsmen import CraftsMenWindow
from workOrders.work_orders import WorkOrdersWindow
from inventory import InventoryWindow
from db_ops.db_manager import DatabaseManager
from styles.theme_settings_widget import ThemeSettingsWidget
from styles.dark_theme import DarkTheme
from styles.theme_config import ThemeConfig
from ui.equipments_window import EquipmentsWindow
from notifications import EmailNotificationService
from craftsman_portal import CraftsmanPortal
from craftsman_login import CraftsmanLoginDialog
from scheduler import MaintenanceScheduler
from schedules_window import SchedulesWindow
from inventory_personnel_portal import InventoryPersonnelPortal
from inventory_personnel_login import InventoryPersonnelLoginDialog
from notification_center import NotificationCenter
import logging
from font_size_dialog import GlobalFontSizeDialog

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

        self.notification_service = EmailNotificationService(self.db_manager)
        if self.notification_service.is_enabled():
            self.notification_service.start_scheduler()
            
        # Initialize notification center but don't show it yet
        self.notification_center = None

        # Start the maintenance scheduler
        self.scheduler_logger = logging.getLogger('maintenance_scheduler')
        self.scheduler_logger.info("Starting maintenance scheduler...")
        self.scheduler = MaintenanceScheduler(notification_service=self.notification_service)
        self.scheduler.db_manager = self.db_manager
        self.scheduler.start()
        
        # Create central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        self.main_layout = QVBoxLayout(central_widget)  # Changed to VBoxLayout
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        
        # Create stacked widget for different pages
        self.stacked_widget = QStackedWidget()

        # Create welcome page only at startup
        self.welcome_page = self.create_welcome_page()
        self.stacked_widget.addWidget(self.welcome_page)
        
        # Initialize window references to None for lazy loading
        self.equipments_window = None
        self.craftsmen_window = None
        self.work_orders_window = None
        self.inventory_window = None
        self.schedules_window = None
        
        self.main_layout.addWidget(self.stacked_widget)
        
        self.setStyleSheet(DarkTheme.get_stylesheet())
        self.load_saved_theme()

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
        
        # Feature boxes - updated to include Schedules
        features = [
            ("Equipment Management", "Register and track all your equipment with detailed information", 
             "icons/equipment.png", 1),  # Navigate to Equipment tab
            ("Craftsmen", "Manage technicians and their skills, certifications, and assignments", 
             "icons/craftsman.png", 2),  # Navigate to Craftsmen tab
            ("Work Orders", "Create and track maintenance work orders from request to completion", 
             "icons/workorder.png", 3),  # Navigate to Work Orders tab
            ("Schedules", "Schedule and manage recurring maintenance tasks", 
             "icons/maintenance.png", 5),  # Navigate to Schedules tab
            ("Inventory Management", "Track spare parts, tools, and supplies for maintenance operations", 
             "icons/inventory.png", 4),  # Navigate to Inventory tab
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
        if page_index == 1:  # Equipment
            window = self.get_equipments_window()
            self.stacked_widget.setCurrentWidget(window)
        elif page_index == 2:  # Craftsmen
            window = self.get_craftsmen_window()
            self.stacked_widget.setCurrentWidget(window)
        elif page_index == 3:  # Work Orders
            window = self.get_work_orders_window()
            self.stacked_widget.setCurrentWidget(window)
        elif page_index == 4:  # Inventory
            window = self.get_inventory_window()
            self.stacked_widget.setCurrentWidget(window)
        elif page_index == 5:  # Schedules
            window = self.get_schedules_window()
            self.stacked_widget.setCurrentWidget(window)
        elif page_index == 7:  # Craftsman Portal
            self.open_craftsman_portal()
        elif page_index == 0:  # Welcome page
            self.stacked_widget.setCurrentIndex(0)
        else:
            # For future features, show a "coming soon" message
            title = box.findChild(QLabel).text()
            QMessageBox.information(
                self,
                "Coming Soon",
                f"The {title} feature is coming soon!"
            )

    def closeEvent(self, event):
        # Stop the Django server if it's running
        if hasattr(self, 'django_process') and self.django_process:
            try:
                self.django_process.terminate()
                self.django_process.wait(timeout=2)  # Wait up to 2 seconds for termination
            except:
                pass  # Ignore errors during termination
        
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
        font_size = settings.get('font_size', 10)  # Default to 10 if not set
        
        # Update DarkTheme colors
        DarkTheme.COLORS.update(colors)
        
        # Apply updated stylesheet
        self.setStyleSheet(DarkTheme.get_stylesheet())
        
        # Apply to all child windows
        for window in self.findChildren(QWidget):
            window.setStyleSheet(DarkTheme.get_stylesheet())
        
        # Apply font size
        app = QApplication.instance()
        font = app.font()
        font.setPointSize(font_size)
        app.setFont(font)

    def load_saved_theme(self):
        """Load saved theme configuration"""
        theme_config = ThemeConfig()
        current_theme = theme_config.get_current_theme()
        
        if current_theme:
            # Update DarkTheme colors
            DarkTheme.COLORS.update(current_theme['colors'])
            
            # Apply theme
            self.setStyleSheet(DarkTheme.get_stylesheet())
            
            # Apply font size if available
            if 'font_size' in current_theme:
                app = QApplication.instance()
                font = app.font()
                font.setPointSize(current_theme['font_size'])
                app.setFont(font)

    def show_edit_font_dialog(self):
        dialog = GlobalFontSizeDialog(parent=self)
        if dialog.exec():
            font_size = dialog.font_slider.value()
            GlobalFontSizeDialog.change_application_font_size(font_size)

    def create_menu_bar(self):
        """Create the main menu bar with navigation options"""
        menu_bar = self.menuBar()
        
        # File menu
        file_menu = menu_bar.addMenu("File")
        
        exit_action = file_menu.addAction("Exit")
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        
        # Add direct menu items for each feature
        home_action = menu_bar.addAction("Home")
        home_action.setShortcut("Ctrl+1")
        home_action.triggered.connect(lambda: self.stacked_widget.setCurrentIndex(0))
        
        equipment_action = menu_bar.addAction("Equipment")
        equipment_action.setShortcut("Ctrl+2")
        equipment_action.triggered.connect(lambda: self.stacked_widget.setCurrentWidget(self.get_equipments_window()))
        
        craftsmen_action = menu_bar.addAction("Craftsmen")
        craftsmen_action.setShortcut("Ctrl+3")
        craftsmen_action.triggered.connect(lambda: self.stacked_widget.setCurrentWidget(self.get_craftsmen_window()))
        
        work_orders_action = menu_bar.addAction("Work Orders")
        work_orders_action.setShortcut("Ctrl+4")
        work_orders_action.triggered.connect(lambda: self.stacked_widget.setCurrentWidget(self.get_work_orders_window()))
        
        inventory_action = menu_bar.addAction("Inventory")
        inventory_action.setShortcut("Ctrl+5")
        inventory_action.triggered.connect(lambda: self.stacked_widget.setCurrentWidget(self.get_inventory_window()))
        
        schedules_action = menu_bar.addAction("Schedules")
        schedules_action.setShortcut("Ctrl+6")
        schedules_action.triggered.connect(lambda: self.stacked_widget.setCurrentWidget(self.get_schedules_window()))
        
        # Create Portals menu
        portals_menu = menu_bar.addMenu("Portals")
        
        # Add portal options
        craftsman_portal_action = portals_menu.addAction("Craftsman Portal")
        craftsman_portal_action.setShortcut("Ctrl+7")
        craftsman_portal_action.triggered.connect(self.open_craftsman_portal)
        
        inventory_portal_action = portals_menu.addAction("Inventory Personnel Portal")
        inventory_portal_action.setShortcut("Ctrl+8")
        inventory_portal_action.triggered.connect(self.open_inventory_portal)
        
        web_portal_action = portals_menu.addAction("Web Portal")
        web_portal_action.triggered.connect(self.launch_web_portal)
        
        # Add Administration menu option
        admin_action = menu_bar.addAction("Administration")
        admin_action.setShortcut("Ctrl+A")
        admin_action.triggered.connect(self.open_admin_window)
        
        # View menu
        view_menu = menu_bar.addMenu("View")
        
        # Theme settings action
        theme_action = view_menu.addAction("Theme Settings")
        theme_action.triggered.connect(self.show_theme_settings)
        
        font_action = view_menu.addAction("Edit Font")
        font_action.triggered.connect(self.show_edit_font_dialog)

        # Add Notifications Center action to View menu
        notifications_action = view_menu.addAction("Notifications Center")
        notifications_action.setShortcut("Ctrl+N")
        notifications_action.triggered.connect(self.show_notification_center)
        
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
        """Launch the web-based portal using Django's runserver"""
        try:
            # Get the path to the Django project
            import os
            import sys
            import subprocess
            import threading
            
            project_root = os.path.dirname(os.path.abspath(__file__))
            django_project_path = os.path.join(project_root, 'CMMSPortals')
            
            # Check if manage.py exists
            manage_py_path = os.path.join(django_project_path, 'manage.py')
            if not os.path.exists(manage_py_path):
                QMessageBox.critical(
                    self,
                    "Error",
                    f"Django project not found at {django_project_path}"
                )
                return
            
            # Show information dialog
            QMessageBox.information(
                self,
                "Web Portal",
                "Starting the web-based portal...\n\n"
                "Users can access the portal at:\n"
                "http://localhost:8000\n\n"
                "The portal will run until the application is closed."
            )
            
            # Get Python executable path
            python_exe = sys.executable
            
            # Function to run the Django server
            def run_django_server():
                try:
                    # Start the Django server
                    process = subprocess.Popen(
                        [python_exe, manage_py_path, 'runserver', '8000'],
                        cwd=django_project_path,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        text=True
                    )
                    
                    # Store the process reference so we can terminate it later
                    self.django_process = process
                    
                    # Wait for the process to complete (which it won't unless terminated)
                    process.wait()
                except Exception as e:
                    print(f"Error in Django server thread: {str(e)}")
            
            # Start the Django server in a separate thread
            portal_thread = threading.Thread(
                target=run_django_server,
                daemon=True  # This ensures the thread will exit when the main program exits
            )
            portal_thread.start()
            
            # Store the thread reference
            self.portal_thread = portal_thread
            
            # Open the browser to the portal
            import webbrowser
            webbrowser.open('http://127.0.0.1:8000/')
            
        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                f"Failed to start web portal: {str(e)}\n\n"
                "Make sure Django is installed by running:\n"
                "pip install django"
            )

    def open_admin_window(self):
        """Open the administration window"""
        # Import here to avoid circular imports
        from admin_window import AdminWindow
        
        # Create authentication dialog to verify admin access
        password, ok = QInputDialog.getText(
            self, 
            "Admin Authentication", 
            "Enter Admin Password:",
            QLineEdit.Password
        )
        
        if ok and password:
            # Verify admin password - in a real app this would check against stored credentials
            if self.db_manager.verify_admin_password(password):
                # Open the admin window
                admin_window = AdminWindow(self.db_manager, self)
                admin_window.showMaximized()
            else:
                QMessageBox.warning(
                    self,
                    "Authentication Failed",
                    "Incorrect admin password. Access denied."
                )

    def open_inventory_portal(self):
        """Open the inventory personnel portal with login dialog"""
        # Create a login dialog
        login_dialog = InventoryPersonnelLoginDialog(self.db_manager, self)
        if login_dialog.exec():
            # If login successful, open the portal with the personnel ID
            personnel_id = login_dialog.get_personnel_id()
            if personnel_id:
                portal = InventoryPersonnelPortal(self.db_manager, personnel_id, parent=self)
                portal.show()

    def show_notification_center(self):
        """Show the notification center window"""
        if not self.notification_center:
            self.notification_center = NotificationCenter(self.notification_service, self)
            # Connect the notification count signal to update UI if needed
            self.notification_center.notification_count_changed.connect(self.update_notification_indicator)
        
        self.notification_center.refresh_notifications()
        self.notification_center.show()
        self.notification_center.raise_()
        self.notification_center.activateWindow()
    
    def update_notification_indicator(self, count):
        """Update UI to indicate notification count if needed"""
        # This could be used to show a badge or indicator in the main UI
        # For now, we'll just print to console
        # print(f"Failed notifications: {count}")
        
        # In a future enhancement, this could update a status bar or icon
        # to show the number of pending/failed notifications
        pass

    # Lazy loading methods for each window
    def get_equipments_window(self):
        if self.equipments_window is None:
            self.equipments_window = EquipmentsWindow(self.db_manager)
            self.stacked_widget.addWidget(self.equipments_window)
        return self.equipments_window
    
    def get_craftsmen_window(self):
        if self.craftsmen_window is None:
            self.craftsmen_window = CraftsMenWindow(db_manager=self.db_manager, parent=self)
            self.stacked_widget.addWidget(self.craftsmen_window)
        return self.craftsmen_window
    
    def get_work_orders_window(self):
        if self.work_orders_window is None:
            self.work_orders_window = WorkOrdersWindow(db_manager=self.db_manager, parent=self)
            self.work_orders_window.sig_work_order_created.connect(self.notification_service.check_and_send_notifications)
            self.stacked_widget.addWidget(self.work_orders_window)
        return self.work_orders_window
    
    def get_inventory_window(self):
        if self.inventory_window is None:
            self.inventory_window = InventoryWindow(db_manager=self.db_manager, parent=self, notification_service=self.notification_service)
            self.inventory_window.sig_inventory_updated.connect(self.notification_service.check_and_send_notifications)
            self.stacked_widget.addWidget(self.inventory_window)
        return self.inventory_window
    
    def get_schedules_window(self):
        if self.schedules_window is None:
            self.schedules_window = SchedulesWindow(db_manager=self.db_manager, parent=self)
            self.stacked_widget.addWidget(self.schedules_window)
        return self.schedules_window