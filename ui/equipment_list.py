from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                              QLineEdit, QPushButton, QTableWidget, QTableWidgetItem,
                              QDialog, QFormLayout, QScrollArea, QFrame, QMenu,
                              QMessageBox)
from PySide6.QtCore import Qt, QSize, QPoint
from PySide6.QtGui import QFont, QCursor
import json
from ui.equipment_details_window import EquipmentDetailsWindow  # Add this import at the top

class EquipmentDetailsDialog(QDialog):
    def __init__(self, equipment_data, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Equipment Details")
        self.setMinimumSize(500, 600)
        self.setup_ui(equipment_data)
        
    def setup_ui(self, equipment_data):
        layout = QVBoxLayout(self)
        
        # Create scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("""
            QScrollArea {
                background-color: #1e1e1e;
                border: none;
            }
        """)
        
        # Create content widget
        content_widget = QWidget()
        form_layout = QFormLayout(content_widget)
        
        # Add standard fields
        standard_fields = [
            ("Equipment ID", str(equipment_data.get('equipment_id', ''))),
            ("Part Number", str(equipment_data.get('part_number', ''))),
            ("Equipment Name", str(equipment_data.get('equipment_name', ''))),
            ("Manufacturer", str(equipment_data.get('manufacturer', ''))),
            ("Model", str(equipment_data.get('model', ''))),
            ("Serial Number", str(equipment_data.get('serial_number', ''))),
            ("Location", str(equipment_data.get('location', ''))),
            ("Installation Date", str(equipment_data.get('installation_date', ''))),
            ("Status", str(equipment_data.get('status', ''))),
            ("Created At", str(equipment_data.get('created_at', ''))),
            ("Last Modified", str(equipment_data.get('last_modified', '')))
        ]
        
        for label, value in standard_fields:
            label_widget = QLabel(label)
            value_widget = QLabel(value if value != 'None' else '')  # Handle None values
            label_widget.setStyleSheet("color: #e0e0e0; font-weight: bold;")
            value_widget.setStyleSheet("color: #e0e0e0;")
            form_layout.addRow(label_widget, value_widget)
        
        # Add custom fields if they exist
        if equipment_data.get('custom_fields'):
            try:
                custom_fields = json.loads(equipment_data['custom_fields'])
                if custom_fields:
                    separator = QFrame()
                    separator.setFrameShape(QFrame.Shape.HLine)
                    separator.setStyleSheet("background-color: #3a3a3a;")
                    form_layout.addRow(separator)
                    
                    custom_label = QLabel("Custom Fields")
                    custom_label.setStyleSheet("color: #e0e0e0; font-weight: bold; font-size: 14px;")
                    form_layout.addRow(custom_label)
                    
                    for key, value in custom_fields.items():
                        label_widget = QLabel(str(key))
                        value_widget = QLabel(str(value))
                        label_widget.setStyleSheet("color: #e0e0e0; font-weight: bold;")
                        value_widget.setStyleSheet("color: #e0e0e0;")
                        form_layout.addRow(label_widget, value_widget)
            except json.JSONDecodeError:
                print("Error decoding custom fields JSON")
        
        scroll.setWidget(content_widget)
        layout.addWidget(scroll)
        
        # Add close button
        close_button = QPushButton("Close")
        close_button.setStyleSheet("""
            QPushButton {
                background-color: #2a2a2a;
                border: 1px solid #3a3a3a;
                border-radius: 4px;
                padding: 8px 16px;
                color: #e0e0e0;
            }
            QPushButton:hover {
                background-color: #3a3a3a;
            }
        """)
        close_button.clicked.connect(self.accept)
        layout.addWidget(close_button)

class EquipmentListWindow(QWidget):
    def __init__(self, db_manager, parent=None):
        super().__init__(parent)
        self.db_manager = db_manager
        self.setWindowTitle("Equipment List")
        self.setup_ui()
        self.load_equipment()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Search section
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search equipment...")
        self.search_input.textChanged.connect(self.filter_equipment)
        self.search_input.setStyleSheet("""
            QLineEdit {
                background-color: #2a2a2a;
                border: 1px solid #3a3a3a;
                border-radius: 4px;
                padding: 8px;
                color: #e0e0e0;
            }
            QLineEdit:focus {
                border: 1px solid #505050;
            }
        """)
        
        search_layout.addWidget(self.search_input)
        layout.addLayout(search_layout)
        
        # Equipment table
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "ID", "Part Number", "Equipment Name", 
            "Location", "Status", "Last Modified"
        ])
        self.table.setStyleSheet("""
            QTableWidget {
                background-color: #1e1e1e;
                color: #e0e0e0;
                gridline-color: #2a2a2a;
                border: none;
            }
            QHeaderView::section {
                background-color: #2a2a2a;
                color: #e0e0e0;
                padding: 8px;
                border: none;
            }
            QTableWidget::item {
                padding: 8px;
            }
            QTableWidget::item:selected {
                background-color: #2b5b84;
            }
        """)
        
        # Enable sorting
        self.table.setSortingEnabled(True)
        
        # Set column widths
        self.table.setColumnWidth(0, 60)   # ID
        self.table.setColumnWidth(1, 120)  # Part Number
        self.table.setColumnWidth(2, 200)  # Equipment Name
        self.table.setColumnWidth(3, 150)  # Location
        self.table.setColumnWidth(4, 120)  # Status
        self.table.setColumnWidth(5, 150)  # Last Modified
        
        # Double click handler
        self.table.doubleClicked.connect(self.show_equipment_details)
        
        # Enable context menu
        self.table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self.show_context_menu)
        
        layout.addWidget(self.table)
        
        # Refresh button
        refresh_button = QPushButton("Refresh List")
        refresh_button.setStyleSheet("""
            QPushButton {
                background-color: #2b5b84;
                border: 1px solid #3a7ab7;
                border-radius: 4px;
                padding: 8px 16px;
                color: #ffffff;
            }
            QPushButton:hover {
                background-color: #3a7ab7;
            }
        """)
        refresh_button.clicked.connect(self.load_equipment)
        layout.addWidget(refresh_button)

    def load_equipment(self):
        equipment_list = self.db_manager.get_all_equipment()
        self.table.setRowCount(len(equipment_list))
        
        for row, equipment in enumerate(equipment_list):
            self.table.setItem(row, 0, QTableWidgetItem(str(equipment['equipment_id'])))
            self.table.setItem(row, 1, QTableWidgetItem(equipment['part_number']))
            self.table.setItem(row, 2, QTableWidgetItem(equipment['equipment_name']))
            self.table.setItem(row, 3, QTableWidgetItem(equipment.get('location', '')))
            self.table.setItem(row, 4, QTableWidgetItem(equipment.get('status', '')))
            self.table.setItem(row, 5, QTableWidgetItem(str(equipment['last_modified'])))

    def filter_equipment(self):
        search_text = self.search_input.text().lower()
        for row in range(self.table.rowCount()):
            row_visible = False
            for col in range(self.table.columnCount()):
                item = self.table.item(row, col)
                if item and search_text in item.text().lower():
                    row_visible = True
                    break
            self.table.setRowHidden(row, not row_visible)

    def show_equipment_details(self, index):
        """Opens the comprehensive equipment details window when double-clicking an item"""
        row = index.row()
        equipment_id = int(self.table.item(row, 0).text())
        
        # Create and show the new details window
        details_window = EquipmentDetailsWindow(equipment_id, self.db_manager)
        details_window.showMaximized()  # Using show() instead of exec() since it's a window, not a dialog

    def show_context_menu(self, position: QPoint):
        row = self.table.rowAt(position.y())
        
        if row >= 0:
            menu = QMenu(self)
            menu.setStyleSheet("""
                QMenu {
                    background-color: #2a2a2a;
                    color: #e0e0e0;
                    border: 1px solid #3a3a3a;
                }
                QMenu::item {
                    padding: 5px 20px;
                }
                QMenu::item:selected {
                    background-color: #3a3a3a;
                }
                QMenu::separator {
                    height: 1px;
                    background-color: #3a3a3a;
                    margin: 5px 0px;
                }
            """)

            # View action - now opens the new window
            view_action = menu.addAction("View Details")
            view_action.triggered.connect(
                lambda: self.show_equipment_details(self.table.indexAt(position))
            )
            
            menu.addSeparator()
            
            # Delete action
            delete_action = menu.addAction("Delete Equipment")
            delete_action.triggered.connect(lambda: self.delete_equipment(row))
            
            menu.exec(QCursor.pos())

    def delete_equipment(self, row: int):
        equipment_id = int(self.table.item(row, 0).text())
        equipment_name = self.table.item(row, 2).text()
        
        # Show confirmation dialog
        reply = QMessageBox.question(
            self,
            "Confirm Deletion",
            f"Are you sure you want to delete equipment:\n{equipment_name}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            if self.db_manager.delete_equipment(equipment_id):
                # Remove row from table
                self.table.removeRow(row)
                QMessageBox.information(
                    self,
                    "Success",
                    "Equipment deleted successfully!"
                )
            else:
                QMessageBox.critical(
                    self,
                    "Error",
                    "Failed to delete equipment. Please try again."
                )