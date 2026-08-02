from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                                 QLineEdit, QDateEdit, QComboBox, QPushButton, 
                                 QScrollArea, QFrame, QMessageBox, QFormLayout,
                                 QDialog, QTableWidget, QTableWidgetItem, QSizePolicy)
from PySide6.QtCore import Qt, QDate, Signal
import json
from typing import Dict, Any
import random
from datetime import datetime, timedelta

class EquipmentRegistrationWindow(QWidget):
    equipment_registered = Signal()
    
    def __init__(self, db_manager, parent=None):
        super().__init__(parent)
        self.db_manager = db_manager
        self.setWindowTitle("Equipment Registration")
        self.setup_ui()

    def setup_ui(self):
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        
        # Add description at the top with dark theme styling
        description = QLabel(
            "Welcome to Equipment Registration! Use this form to register new equipment "
            "in the system. Required fields are marked with *. You can add custom fields "
            "for any additional information specific to your equipment."
        )
        description.setWordWrap(True)
        description.setStyleSheet("""
            padding: 10px;
            background-color: #2a2a2a;
            border-radius: 5px;
            color: #e0e0e0;
            border: 1px solid #3a3a3a;
        """)
        main_layout.addWidget(description)
        
        # Create a scroll area for the form
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)  # Ensure vertical scrollbar appears when needed
        scroll.setStyleSheet("""
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
        
        # Create a widget to hold the form AND buttons
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setSpacing(15)  # Add more spacing between elements
        content_widget.setStyleSheet("""
            QWidget {
                background-color: #1e1e1e;
                color: #e0e0e0;
            }
            QLineEdit, QDateEdit, QComboBox {
                background-color: #2a2a2a;
                border: 1px solid #3a3a3a;
                border-radius: 4px;
                padding: 5px;
                color: #e0e0e0;
            }
            QLineEdit:focus, QDateEdit:focus, QComboBox:focus {
                border: 1px solid #505050;
            }
            QPushButton {
                background-color: #2a2a2a;
                border: 1px solid #3a3a3a;
                border-radius: 4px;
                padding: 6px 12px;
                color: #e0e0e0;
            }
            QPushButton:hover {
                background-color: #3a3a3a;
            }
            QPushButton:pressed {
                background-color: #404040;
            }
        """)
        
        # Create form layout and add it to content layout
        form_widget = QWidget()
        self.form_layout = QFormLayout(form_widget)
        self.form_layout.setSpacing(10)  # Add more spacing in the form
        content_layout.addWidget(form_widget)
        
        # Add standard fields
        self.fields = {}
        
        # All standard fields are now required with tooltips
        self.add_field(
            "part_number", 
            "Part Number", 
            required=True,
            tooltip="Enter the unique identifier for this equipment"
        )
        self.fields["part_number"].textChanged.connect(self.validate_part_number)
        
        self.add_field(
            "equipment_name", 
            "Equipment Name", 
            required=True,
            tooltip="Enter a descriptive name for the equipment"
        )
        self.fields["equipment_name"].textChanged.connect(self.validate_equipment_name)
        
        self.add_field(
            "manufacturer",
            "Manufacturer",
            required=True,
            tooltip="Name of the equipment manufacturer"
        )
        
        self.add_field(
            "model",
            "Model",
            required=True,
            tooltip="Model number or name of the equipment"
        )
        
        self.add_field(
            "serial_number",
            "Serial Number",
            required=True,
            tooltip="Unique serial number provided by the manufacturer"
        )
        
        self.add_field(
            "location",
            "Location",
            required=True,
            tooltip="Physical location where the equipment is installed"
        )
        
        # Add date field with tooltip
        self.installation_date = QDateEdit()
        self.installation_date.setCalendarPopup(True)
        self.installation_date.setDate(QDate.currentDate())
        self.installation_date.setToolTip("Date when the equipment was or will be installed")
        self.form_layout.addRow("Installation Date:", self.installation_date)
        
        # Add status dropdown with tooltip
        self.status_combo = QComboBox()
        self.status_combo.addItems(["Active", "Inactive", "Under Maintenance", "Retired"])
        self.status_combo.setToolTip("Current operational status of the equipment")
        self.form_layout.addRow("Status:", self.status_combo)
        
        # Add custom fields section
        custom_fields_frame = QFrame()
        custom_fields_frame.setFrameStyle(QFrame.Shape.StyledPanel | QFrame.Shadow.Raised)
        custom_fields_frame.setStyleSheet("""
            QFrame {
                background-color: #2a2a2a;
                border: 1px solid #3a3a3a;
                border-radius: 4px;
            }
        """)
        
        # Update custom fields label
        custom_fields_label = QLabel("Custom Fields")
        custom_fields_label.setStyleSheet("""
            font-weight: bold;
            color: #e0e0e0;
            padding: 5px;
        """)
        
        custom_fields_layout = QVBoxLayout(custom_fields_frame)
        custom_fields_layout.addWidget(custom_fields_label)
        
        self.custom_fields_layout = QVBoxLayout()
        custom_fields_layout.addLayout(self.custom_fields_layout)
        
        # Add custom field button
        add_field_button = QPushButton("Add Custom Field")
        add_field_button.clicked.connect(self.add_custom_field)
        custom_fields_layout.addWidget(add_field_button)
        
        self.form_layout.addRow(custom_fields_frame)
        
        # Add a separator line above buttons
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        separator.setStyleSheet("background-color: #3a3a3a;")
        content_layout.addWidget(separator)
        
        # Add buttons with improved styling and layout
        button_layout = QHBoxLayout()
        button_layout.setContentsMargins(10, 10, 10, 10)  # Add some padding
        button_layout.setSpacing(10)  # Space between buttons
        
        # Add a "Fill Demo Data" button next to Clear Form
        demo_button = QPushButton("Fill Demo Data")
        demo_button.setStyleSheet("""
            QPushButton {
                background-color: #2a2a2a;
                border: 1px solid #3a3a3a;
                border-radius: 4px;
                padding: 10px 20px;
                color: #e0e0e0;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: #3a3a3a;
                border: 1px solid #505050;
            }
            QPushButton:pressed {
                background-color: #404040;
            }
        """)
        demo_button.clicked.connect(self.fill_demo_data)
        
        clear_button = QPushButton("Clear Form")
        clear_button.setStyleSheet("""
            QPushButton {
                background-color: #2a2a2a;
                border: 1px solid #3a3a3a;
                border-radius: 4px;
                padding: 10px 20px;
                color: #e0e0e0;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: #3a3a3a;
                border: 1px solid #505050;
            }
            QPushButton:pressed {
                background-color: #404040;
            }
        """)
        clear_button.clicked.connect(self.clear_form)
        
        save_button = QPushButton("Register Equipment")
        save_button.setStyleSheet("""
            QPushButton {
                background-color: #2b5b84;
                border: 1px solid #3a7ab7;
                border-radius: 4px;
                padding: 10px 20px;
                color: #ffffff;
                min-width: 100px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #3a7ab7;
            }
            QPushButton:pressed {
                background-color: #2b5b84;
            }
        """)
        save_button.clicked.connect(self.save_equipment)
        
        # Update button layout
        button_layout.addStretch()
        button_layout.addWidget(demo_button)
        button_layout.addWidget(clear_button)
        button_layout.addWidget(save_button)
        
        # Add button layout to content layout
        content_layout.addLayout(button_layout)
        
        # At the end, make sure we set a reasonable size hint
        content_widget.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        
        # Set the content widget as the scroll area's widget
        scroll.setWidget(content_widget)
        main_layout.addWidget(scroll, 1)  # Give the scroll area a stretch factor of 1

    def add_field(self, name: str, label: str, required: bool = False, tooltip: str = ""):
        field = QLineEdit()
        if required:
            label += " *"
            # Add visual indication for required fields
            field.setStyleSheet("""
                QLineEdit {
                    border: 1px solid #3a3a3a;
                    background-color: #2a2a2a;
                    border-radius: 4px;
                    padding: 5px;
                    color: #e0e0e0;
                }
                QLineEdit:focus {
                    border: 1px solid #505050;
                }
            """)
        if tooltip:
            field.setToolTip(tooltip)
        self.form_layout.addRow(label, field)
        self.fields[name] = field

    def add_custom_field(self):
        custom_field_widget = QWidget()
        custom_field_layout = QHBoxLayout(custom_field_widget)
        
        field_name = QLineEdit()
        field_name.setPlaceholderText("Field Name")
        field_value = QLineEdit()
        field_value.setPlaceholderText("Field Value")
        remove_button = QPushButton("Remove")
        
        custom_field_layout.addWidget(field_name)
        custom_field_layout.addWidget(field_value)
        custom_field_layout.addWidget(remove_button)
        
        self.custom_fields_layout.addWidget(custom_field_widget)
        
        remove_button.clicked.connect(lambda: self.remove_custom_field(custom_field_widget))

    def remove_custom_field(self, widget):
        widget.deleteLater()

    def get_custom_fields(self) -> Dict[str, str]:
        custom_fields = {}
        for i in range(self.custom_fields_layout.count()):
            widget = self.custom_fields_layout.itemAt(i).widget()
            if widget:
                layout = widget.layout()
                name = layout.itemAt(0).widget().text()
                value = layout.itemAt(1).widget().text()
                if name and value:
                    custom_fields[name] = value
        return custom_fields

    def check_duplicate_equipment(self) -> tuple[bool, str]:
        """
        Check if equipment with similar details already exists.
        Returns (is_duplicate, message)
        """
        part_number = self.fields["part_number"].text().strip()
        serial_number = self.fields["serial_number"].text().strip()
        equipment_name = self.fields["equipment_name"].text().strip()
        
        # Skip empty fields in duplicate check
        check_fields = {}
        if part_number:
            check_fields['part_number'] = part_number
        if serial_number:
            check_fields['serial_number'] = serial_number
        if equipment_name:
            check_fields['equipment_name'] = equipment_name
        
        # If no fields to check, return early
        if not check_fields:
            return False, ""
        
        # Get existing equipment
        existing_equipment = self.db_manager.get_equipment_by_fields(check_fields)
        
        if existing_equipment:
            duplicate_fields = []
            if part_number and any(eq.get('part_number') == part_number for eq in existing_equipment):
                duplicate_fields.append("Part Number")
            if serial_number and any(eq.get('serial_number') == serial_number for eq in existing_equipment):
                duplicate_fields.append("Serial Number")
            if equipment_name and any(eq.get('equipment_name') == equipment_name for eq in existing_equipment):
                duplicate_fields.append("Equipment Name")
            
            if duplicate_fields:
                return True, f"Equipment with the same {' and '.join(duplicate_fields)} already exists!"
        
        return False, ""

    def save_equipment(self):
        """Save equipment data after validation"""
        # Reset validation errors
        validation_errors = []
        
        # Validate all standard fields are not empty
        for field_name, field in self.fields.items():
            field_value = field.text().strip()
            if not field_value:
                # Convert field_name from snake_case to Title Case for display
                display_name = " ".join(word.capitalize() for word in field_name.split("_"))
                validation_errors.append(f"{display_name} is required")
                field.setStyleSheet("""
                    QLineEdit {
                        border: 1px solid #ff5555;
                        background-color: #2a2a2a;
                        border-radius: 4px;
                        padding: 5px;
                        color: #e0e0e0;
                    }
                """)
        
        # Validate part number format (alphanumeric with hyphens allowed)
        part_number = self.fields["part_number"].text().strip()
        if part_number and not all(c.isalnum() or c == '-' for c in part_number):
            validation_errors.append("Part Number should contain only letters, numbers, and hyphens")
            self.fields["part_number"].setStyleSheet("""
                QLineEdit {
                    border: 1px solid #ffaa55;
                    background-color: #2a2a2a;
                    border-radius: 4px;
                    padding: 5px;
                    color: #e0e0e0;
                }
            """)
        
        # Validate serial number format
        serial_number = self.fields["serial_number"].text().strip()
        if serial_number and not all(c.isalnum() or c in '-_' for c in serial_number):
            validation_errors.append("Serial Number should contain only letters, numbers, hyphens, and underscores")
            self.fields["serial_number"].setStyleSheet("""
                QLineEdit {
                    border: 1px solid #ffaa55;
                    background-color: #2a2a2a;
                    border-radius: 4px;
                    padding: 5px;
                    color: #e0e0e0;
                }
            """)
        
        # Validate installation date is not in the future
        current_date = QDate.currentDate()
        selected_date = self.installation_date.date()
        if selected_date > current_date:
            validation_errors.append("Installation Date cannot be in the future")
            self.installation_date.setStyleSheet("""
                QDateEdit {
                    border: 1px solid #ffaa55;
                    background-color: #2a2a2a;
                    border-radius: 4px;
                    padding: 5px;
                    color: #e0e0e0;
                }
            """)
        
        # Validate custom fields
        custom_fields = {}
        for i in range(self.custom_fields_layout.count()):
            widget = self.custom_fields_layout.itemAt(i).widget()
            if widget:
                layout = widget.layout()
                name = layout.itemAt(0).widget().text().strip()
                value = layout.itemAt(1).widget().text().strip()
                
                # Validate custom field names
                if name:
                    if not value:
                        validation_errors.append(f"Custom field '{name}' has no value")
                        layout.itemAt(1).widget().setStyleSheet("""
                            QLineEdit {
                                border: 1px solid #ff5555;
                                background-color: #2a2a2a;
                                border-radius: 4px;
                                padding: 5px;
                                color: #e0e0e0;
                            }
                        """)
                    elif name in ["Part Number", "Equipment Name", "Manufacturer", "Model", 
                                 "Serial Number", "Location", "Installation Date", "Status"]:
                        validation_errors.append(f"Custom field '{name}' conflicts with a standard field name")
                        layout.itemAt(0).widget().setStyleSheet("""
                            QLineEdit {
                                border: 1px solid #ff5555;
                                background-color: #2a2a2a;
                                border-radius: 4px;
                                padding: 5px;
                                color: #e0e0e0;
                            }
                        """)
                    else:
                        custom_fields[name] = value
        
        # Show validation errors if any
        if validation_errors:
            error_message = "Please correct the following errors:\n• " + "\n• ".join(validation_errors)
            QMessageBox.warning(self, "Validation Error", error_message)
            return
        
        # Check for duplicates
        is_duplicate, message = self.check_duplicate_equipment()
        if is_duplicate:
            QMessageBox.warning(self, "Duplicate Equipment", message)
            return
        
        # Gather equipment data
        equipment_data = {
            "Part Number": part_number,
            "Equipment Name": self.fields["equipment_name"].text().strip(),
            "Manufacturer": self.fields["manufacturer"].text().strip(),
            "Model": self.fields["model"].text().strip(),
            "Serial Number": serial_number,
            "Location": self.fields["location"].text().strip(),
            "Installation Date": selected_date.toString("yyyy-MM-dd"),
            "Status": self.status_combo.currentText()
        }
        
        # Add custom fields to equipment data
        equipment_data.update(custom_fields)
        
        # Show confirmation dialog
        dialog = ConfirmationDialog(equipment_data, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            # Convert back to snake_case for database
            db_data = {
                "part_number": equipment_data["Part Number"],
                "equipment_name": equipment_data["Equipment Name"],
                "manufacturer": equipment_data["Manufacturer"],
                "model": equipment_data["Model"],
                "serial_number": equipment_data["Serial Number"],
                "location": equipment_data["Location"],
                "installation_date": equipment_data["Installation Date"],
                "status": equipment_data["Status"]
            }
            
            # Add custom fields to db_data
            for key, value in custom_fields.items():
                db_data[key] = value
            
            # Save to database
            user_id = getattr(self, 'current_user_id', 1)  # Default to 1 if not set
            if self.db_manager.register_equipment(user_id, db_data):
                QMessageBox.information(self, "Success", "Equipment registered successfully!")
                self.clear_form()
                self.equipment_registered.emit()
            else:
                QMessageBox.critical(self, "Error", "Failed to register equipment!")

    def clear_form(self):
        """Clear all form fields and reset validation styling"""
        # Clear standard fields
        for field in self.fields.values():
            field.clear()
            field.setStyleSheet("""
                QLineEdit {
                    border: 1px solid #3a3a3a;
                    background-color: #2a2a2a;
                    border-radius: 4px;
                    padding: 5px;
                    color: #e0e0e0;
                }
            """)
        
        # Reset date to current
        self.installation_date.setDate(QDate.currentDate())
        self.installation_date.setStyleSheet("""
            QDateEdit {
                border: 1px solid #3a3a3a;
                background-color: #2a2a2a;
                border-radius: 4px;
                padding: 5px;
                color: #e0e0e0;
            }
        """)
        
        # Reset status
        self.status_combo.setCurrentIndex(0)
        
        # Clear custom fields
        while self.custom_fields_layout.count():
            widget = self.custom_fields_layout.takeAt(0).widget()
            if widget:
                widget.deleteLater()

    def fill_demo_data(self):
        # Clear everything first
        self.clear_form()
        
        # Lists for random data generation
        manufacturers = ["TechCorp Industries", "MegaMachine Corp", "IndustrialTech", "PowerTools Inc", "HighTech Solutions"]
        locations = ["Building A - Room {}", "Workshop {}", "Factory Floor {}", "Lab {}", "Warehouse {}"]
        model_prefixes = ["LC", "PT", "HT", "MX", "RT"]
        power_ratings = ["3000W", "4000W", "5000W", "6000W", "7500W"]
        maintenance_intervals = ["3 months", "6 months", "12 months", "24 months"]
        safety_categories = ["Class 1", "Class 2", "Class 3", "Class 4"]
        equipment_types = ["Laser Cutter", "CNC Machine", "3D Printer", "Industrial Robot", "Testing Equipment"]
        
        # Generate random year and serial parts
        current_year = datetime.now().year
        random_number = random.randint(1, 999)
        random_serial = random.randint(10000, 99999)
        
        # Generate demo data with randomness
        demo_data = {
            "part_number": f"PT-{current_year}-{random_number:03d}",
            "equipment_name": f"{random.choice(equipment_types)} #{random_number:03d}",
            "manufacturer": random.choice(manufacturers),
            "model": f"{random.choice(model_prefixes)}-{random.randint(1000, 9999)}X",
            "serial_number": f"SN-{current_year}-{random_serial}",
            "location": random.choice(locations).format(random.randint(100, 999))
        }
        
        # Fill the fields
        for field_name, value in demo_data.items():
            if field_name in self.fields:
                self.fields[field_name].setText(value)
        
        # Set a random date within the last 6 months
        days_ago = random.randint(0, 180)
        demo_date = QDate.currentDate().addDays(-days_ago)
        self.installation_date.setDate(demo_date)
        
        # Set random status
        self.status_combo.setCurrentText(random.choice(["Active", "Inactive", "Under Maintenance"]))
        
        # Add random custom fields
        demo_custom_fields = [
            ("Power Rating", random.choice(power_ratings)),
            ("Maintenance Interval", random.choice(maintenance_intervals)),
            ("Safety Category", random.choice(safety_categories)),
        ]
        
        for name, value in demo_custom_fields:
            custom_field_widget = QWidget()
            custom_field_layout = QHBoxLayout(custom_field_widget)
            
            field_name = QLineEdit()
            field_name.setText(name)
            field_value = QLineEdit()
            field_value.setText(value)
            remove_button = QPushButton("Remove")
            
            custom_field_layout.addWidget(field_name)
            custom_field_layout.addWidget(field_value)
            custom_field_layout.addWidget(remove_button)
            
            self.custom_fields_layout.addWidget(custom_field_widget)
            remove_button.clicked.connect(lambda checked, w=custom_field_widget: self.remove_custom_field(w))

    def validate_part_number(self):
        """Validate part number as user types"""
        part_number = self.fields["part_number"].text().strip()
        if not part_number:
            self.fields["part_number"].setStyleSheet("""
                QLineEdit {
                    border: 1px solid #ff5555;
                    background-color: #2a2a2a;
                    border-radius: 4px;
                    padding: 5px;
                    color: #e0e0e0;
                }
            """)
            self.fields["part_number"].setToolTip("Part Number is required")
        elif not all(c.isalnum() or c == '-' for c in part_number):
            self.fields["part_number"].setStyleSheet("""
                QLineEdit {
                    border: 1px solid #ffaa55;
                    background-color: #2a2a2a;
                    border-radius: 4px;
                    padding: 5px;
                    color: #e0e0e0;
                }
            """)
            self.fields["part_number"].setToolTip("Part Number should contain only letters, numbers, and hyphens")
        else:
            self.fields["part_number"].setStyleSheet("""
                QLineEdit {
                    border: 1px solid #55aa55;
                    background-color: #2a2a2a;
                    border-radius: 4px;
                    padding: 5px;
                    color: #e0e0e0;
                }
            """)
            self.fields["part_number"].setToolTip("Valid Part Number")

    def validate_equipment_name(self):
        """Validate equipment name as user types"""
        equipment_name = self.fields["equipment_name"].text().strip()
        if not equipment_name:
            self.fields["equipment_name"].setStyleSheet("""
                QLineEdit {
                    border: 1px solid #ff5555;
                    background-color: #2a2a2a;
                    border-radius: 4px;
                    padding: 5px;
                    color: #e0e0e0;
                }
            """)
            self.fields["equipment_name"].setToolTip("Equipment Name is required")
        else:
            self.fields["equipment_name"].setStyleSheet("""
                QLineEdit {
                    border: 1px solid #55aa55;
                    background-color: #2a2a2a;
                    border-radius: 4px;
                    padding: 5px;
                    color: #e0e0e0;
                }
            """)
            self.fields["equipment_name"].setToolTip("Valid Equipment Name")

class ConfirmationDialog(QDialog):
    def __init__(self, equipment_data, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Confirm Equipment Details")
        self.setup_ui(equipment_data)
        
    def setup_ui(self, equipment_data):
        layout = QVBoxLayout(self)
        
        # Create table
        table = QTableWidget()
        table.setColumnCount(2)
        table.setHorizontalHeaderLabels(["Field", "Value"])
        table.setRowCount(len(equipment_data))
        table.setStyleSheet("""
            QTableWidget {
                background-color: #1e1e1e;
                color: #e0e0e0;
                border: 1px solid #3a3a3a;
                gridline-color: #2a2a2a;
            }
            QTableWidget::item {
                padding: 5px;
            }
            QHeaderView::section {
                background-color: #2a2a2a;
                color: #e0e0e0;
                padding: 5px;
                border: 1px solid #3a3a3a;
            }
            QTableWidget::item:selected {
                background-color: #2b5b84;
            }
        """)
        
        # Populate table
        for index, (key, value) in enumerate(equipment_data.items()):
            field_item = QTableWidgetItem(key.replace('_', ' ').title())
            value_item = QTableWidgetItem(str(value))
            table.setItem(index, 0, field_item)
            table.setItem(index, 1, value_item)
        
        # Auto-adjust columns to content
        table.resizeColumnsToContents()
        table.resizeRowsToContents()
        
        # Set minimum width for better readability
        table.setMinimumWidth(400)
        
        layout.addWidget(table)
        
        # Add buttons
        button_layout = QHBoxLayout()
        
        confirm_button = QPushButton("Confirm and Register")
        confirm_button.setStyleSheet("""
            QPushButton {
                background-color: #2b5b84;
                border: 1px solid #3a7ab7;
                border-radius: 4px;
                padding: 10px 20px;
                color: #ffffff;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #3a7ab7;
            }
            QPushButton:pressed {
                background-color: #2b5b84;
            }
        """)
        
        cancel_button = QPushButton("Cancel")
        cancel_button.setStyleSheet("""
            QPushButton {
                background-color: #2a2a2a;
                border: 1px solid #3a3a3a;
                border-radius: 4px;
                padding: 10px 20px;
                color: #e0e0e0;
            }
            QPushButton:hover {
                background-color: #3a3a3a;
            }
            QPushButton:pressed {
                background-color: #404040;
            }
        """)
        
        confirm_button.clicked.connect(self.accept)
        cancel_button.clicked.connect(self.reject)
        
        button_layout.addWidget(cancel_button)
        button_layout.addWidget(confirm_button)
        
        layout.addLayout(button_layout)
        
        self.setMinimumWidth(500)
        self.setMinimumHeight(400)
