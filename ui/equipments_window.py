from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QTabWidget,
                              QMenuBar, QStatusBar, QMessageBox, QTabBar)
from PySide6.QtCore import Qt
from ui.equipment_list import EquipmentListWindow
from ui.equipment_registration import EquipmentRegistrationWindow

class EquipmentsWindow(QWidget):
    def __init__(self, db_manager, parent=None):
        super().__init__(parent)
        self.db_manager = db_manager
        self.setup_ui()

    def setup_ui(self):
        # Create main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Create menu bar
        menu_bar = QMenuBar()
        equipment_menu = menu_bar.addMenu("Equipment")
        
        # Add "New Equipment" action
        new_equipment_action = equipment_menu.addAction("New Equipment")
        new_equipment_action.triggered.connect(self.add_equipment_tab)
        
        layout.addWidget(menu_bar)
        
        # Create tab widget
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabsClosable(True)
        self.tab_widget.tabCloseRequested.connect(self.close_tab)
        
        # Add equipment list as the main tab (not closable)
        self.equipment_list = EquipmentListWindow(self.db_manager)
        self.tab_widget.addTab(self.equipment_list, "Equipment List")
        self.tab_widget.tabBar().setTabButton(0, QTabBar.ButtonPosition.RightSide, None)
        
        # Make sure the tab widget takes all available space
        layout.addWidget(self.tab_widget, 1)  # Add stretch factor

    def add_equipment_tab(self):
        """Add a new equipment registration tab"""
        registration_tab = EquipmentRegistrationWindow(self.db_manager)
        registration_tab.equipment_registered.connect(self.equipment_list.load_equipment)
        
        # Add new tab and switch to it
        index = self.tab_widget.addTab(registration_tab, "New Equipment")
        self.tab_widget.setCurrentIndex(index)

    def close_tab(self, index):
        """Close the specified tab"""
        if index != 0:  # Don't close the main equipment list tab
            widget = self.tab_widget.widget(index)
            widget.deleteLater()
            self.tab_widget.removeTab(index) 