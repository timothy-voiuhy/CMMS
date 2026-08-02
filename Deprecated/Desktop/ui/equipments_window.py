from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QTabWidget,
                              QMenuBar, QStatusBar, QMessageBox, QTabBar,
                              QDialog, QLabel, QSpinBox, QDialogButtonBox, QGridLayout)
from PySide6.QtCore import Qt
from ui.equipment_list import EquipmentListWindow
from ui.equipment_registration import EquipmentRegistrationWindow
import random
from datetime import datetime, timedelta
import json

class EquipmentGenerationDialog(QDialog):
    """Dialog to configure how many equipment items to generate for each type"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Configure Demo Equipment Generation")
        self.setMinimumWidth(400)
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Add description
        description = QLabel(
            "Specify how many equipment items to generate for each category in the "
            "Coca-Cola production line demo. The total number of items will affect "
            "generation time."
        )
        description.setWordWrap(True)
        description.setStyleSheet("margin-bottom: 15px;")
        layout.addWidget(description)
        
        # Create grid for spinboxes
        grid = QGridLayout()
        
        # Equipment types and their descriptions
        equipment_types = [
            ("conveyor_count", "Conveyor Belts:", "Transport bottles and packages through the production line"),
            ("forklift_count", "Forklifts:", "Move pallets of products in warehouses and loading areas"),
            ("agv_count", "AGVs:", "Automated Guided Vehicles for internal logistics"),
            ("cold_storage_count", "Cold Storage Units:", "Temperature-controlled storage for products"),
            ("bottling_count", "Bottling Machines:", "Fill and cap bottles with Coca-Cola products")
        ]
        
        # Create spinboxes for each equipment type
        self.spinboxes = {}
        for row, (name, label, tooltip) in enumerate(equipment_types):
            # Create label
            label_widget = QLabel(label)
            label_widget.setToolTip(tooltip)
            
            # Create spinbox
            spinbox = QSpinBox()
            spinbox.setMinimum(0)
            spinbox.setMaximum(10)  # Reasonable maximum to prevent excessive generation
            spinbox.setValue(1)  # Default value
            spinbox.setToolTip(tooltip)
            
            # Store spinbox reference
            self.spinboxes[name] = spinbox
            
            # Add to grid
            grid.addWidget(label_widget, row, 0)
            grid.addWidget(spinbox, row, 1)
        
        layout.addLayout(grid)
        
        # Add total count label
        self.total_label = QLabel("Total equipment items: 15")
        layout.addWidget(self.total_label)
        
        # Connect spinbox signals to update total
        for spinbox in self.spinboxes.values():
            spinbox.valueChanged.connect(self.update_total)
        
        # Add button box
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
        # Initialize total
        self.update_total()
        
    def update_total(self):
        """Update the total count label based on current spinbox values"""
        total = sum(spinbox.value() for spinbox in self.spinboxes.values())
        self.total_label.setText(f"Total equipment items: {total}")
        
    def get_counts(self):
        """Return a dictionary with the count for each equipment type"""
        return {name: spinbox.value() for name, spinbox in self.spinboxes.items()}

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
        
        # Add "Generate Demo Equipment" action
        demo_equipment_action = equipment_menu.addAction("Generate Coca-Cola Demo Equipment")
        demo_equipment_action.triggered.connect(self.generate_demo_equipment)
        
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
            
    def generate_demo_equipment(self):
        """Generate demo equipment for a Coca-Cola distribution and logistics production line"""
        # Show dialog to configure equipment counts
        dialog = EquipmentGenerationDialog(self)
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return
            
        # Get equipment counts
        counts = dialog.get_counts()
        
        # Ask for final confirmation
        total_count = sum(counts.values())
        if total_count == 0:
            QMessageBox.warning(
                self,
                "No Equipment Selected",
                "Please select at least one equipment type to generate."
            )
            return
            
        reply = QMessageBox.question(
            self,
            "Generate Demo Equipment",
            f"This will create {total_count} demo equipment items for a Coca-Cola production line.\n"
            "Do you want to continue?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply != QMessageBox.StandardButton.Yes:
            return
            
        # First, check if the default template exists
        connection = self.db_manager.connect()
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT template_id FROM equipment_templates WHERE template_name = 'Default Template'")
        template = cursor.fetchone()
        
        # If template doesn't exist, create it
        if not template:
            # Create a default template with basic fields
            default_fields = [
                {"name": "Serial Number", "type": "text", "required": True},
                {"name": "Manufacturer", "type": "text", "required": True},
                {"name": "Model", "type": "text", "required": True},
                {"name": "Installation Date", "type": "date", "required": True},
                {"name": "Location", "type": "text", "required": True},
                {"name": "Status", "type": "select", "options": ["Active", "Inactive", "Under Maintenance"], "required": True}
            ]
            
            # Create the template
            success = self.db_manager.create_equipment_template("Default Template", default_fields)
            if not success:
                self.db_manager.close(connection)
                QMessageBox.critical(
                    self,
                    "Error",
                    "Failed to create default equipment template."
                )
                return
            
            # Get the newly created template ID
            cursor.execute("SELECT template_id FROM equipment_templates WHERE template_name = 'Default Template'")
            template = cursor.fetchone()
            
            if not template:
                self.db_manager.close(connection)
                QMessageBox.critical(
                    self,
                    "Error",
                    "Failed to retrieve created template."
                )
                return
        
        template_id = template['template_id']
        self.db_manager.close(connection)
        
        # Define equipment categories and their specific attributes
        equipment_data = self.create_coca_cola_equipment_data(counts)
        
        # Register all equipment
        success_count = 0
        equipment_ids = []
        equipment_types = {}  # Store equipment type for each ID
        
        for equipment in equipment_data:
            # Determine equipment type from part number prefix
            part_number = equipment["part_number"]
            equipment_type = None
            if part_number.startswith("CB-"):
                equipment_type = "conveyor"
            elif part_number.startswith("FL-"):
                equipment_type = "forklift"
            elif part_number.startswith("AGV-"):
                equipment_type = "agv"
            elif part_number.startswith("CS-"):
                equipment_type = "cold_storage"
            elif part_number.startswith("BM-"):
                equipment_type = "bottling"
            
            equipment_id = self.db_manager.register_equipment(template_id, equipment)
            if equipment_id:
                success_count += 1
                equipment_ids.append(equipment_id)
                equipment_types[equipment_id] = equipment_type
        
        # Generate additional details for each equipment
        if equipment_ids:
            for equipment_id in equipment_ids:
                equipment_type = equipment_types[equipment_id]
                self.generate_equipment_details(equipment_id, equipment_type)
        
        # Refresh the equipment list
        self.equipment_list.load_equipment()
        
        # Show success message
        QMessageBox.information(
            self,
            "Demo Equipment Generated",
            f"Successfully created {success_count} demo equipment items for the Coca-Cola production line."
        )
    
    def generate_equipment_details(self, equipment_id, equipment_type):
        """Generate detailed information for an equipment item"""
        # Generate history entries
        self.generate_history_entries(equipment_id, equipment_type)
        
        # Generate maintenance tasks
        self.generate_maintenance_tasks(equipment_id, equipment_type)
        
        # Generate special tools
        self.generate_special_tools(equipment_id, equipment_type)
        
        # Generate safety information
        self.generate_safety_info(equipment_id, equipment_type)

    def generate_history_entries(self, equipment_id, equipment_type):
        """Generate history entries for the equipment"""
        current_date = datetime.now()
        
        # Common history entries for all equipment types
        common_entries = [
            {
                "date": (current_date - timedelta(days=random.randint(1, 30))).strftime("%Y-%m-%d"),
                "event_type": "Inspection",
                "description": "Routine inspection completed",
                "performed_by": random.choice(["John Smith", "Maria Garcia", "David Chen", "Sarah Johnson"]),
                "notes": "All systems functioning within normal parameters."
            },
            {
                "date": (current_date - timedelta(days=random.randint(31, 90))).strftime("%Y-%m-%d"),
                "event_type": "Maintenance",
                "description": "Preventive maintenance performed",
                "performed_by": random.choice(["Robert Williams", "Jennifer Lee", "Michael Brown", "Lisa Rodriguez"]),
                "notes": "Replaced wear components and lubricated moving parts."
            }
        ]
        
        # Type-specific history entries
        type_specific_entries = {
            "conveyor": [
                {
                    "date": (current_date - timedelta(days=random.randint(10, 60))).strftime("%Y-%m-%d"),
                    "event_type": "Repair",
                    "description": "Belt tension adjustment",
                    "performed_by": "Thomas Wilson",
                    "notes": "Belt was slipping under load. Tension adjusted to manufacturer specifications."
                }
            ],
            "forklift": [
                {
                    "date": (current_date - timedelta(days=random.randint(15, 45))).strftime("%Y-%m-%d"),
                    "event_type": "Certification",
                    "description": "Annual safety certification",
                    "performed_by": "Safety Inspector #42",
                    "notes": "Forklift passed all safety checks and is certified for operation until next year."
                }
            ],
            "agv": [
                {
                    "date": (current_date - timedelta(days=random.randint(5, 25))).strftime("%Y-%m-%d"),
                    "event_type": "Software Update",
                    "description": "Navigation software updated",
                    "performed_by": "Tech Support Team",
                    "notes": "Updated to version 4.2.1. Improved obstacle detection and path planning algorithms."
                }
            ],
            "cold_storage": [
                {
                    "date": (current_date - timedelta(days=random.randint(7, 35))).strftime("%Y-%m-%d"),
                    "event_type": "Maintenance",
                    "description": "Refrigerant level check",
                    "performed_by": "Cooling Systems Specialist",
                    "notes": "Refrigerant levels within acceptable range. No leaks detected."
                }
            ],
            "bottling": [
                {
                    "date": (current_date - timedelta(days=random.randint(3, 20))).strftime("%Y-%m-%d"),
                    "event_type": "Cleaning",
                    "description": "CIP (Clean-in-Place) procedure",
                    "performed_by": "Sanitation Team",
                    "notes": "Full sanitization cycle completed. All product contact surfaces verified clean."
                }
            ]
        }
        
        # Add installation entry
        installation_date = (current_date - timedelta(days=random.randint(180, 730))).strftime("%Y-%m-%d")
        installation_entry = {
            "date": installation_date,
            "event_type": "Installation",
            "description": "Initial equipment installation",
            "performed_by": "Installation Team",
            "notes": "Equipment installed and commissioned according to manufacturer specifications."
        }
        
        # Add all entries to database
        self.db_manager.add_history_entry(equipment_id, installation_entry)
        
        # Add common entries
        for entry in common_entries:
            self.db_manager.add_history_entry(equipment_id, entry)
        
        # Add type-specific entries if available
        if equipment_type in type_specific_entries:
            for entry in type_specific_entries[equipment_type]:
                self.db_manager.add_history_entry(equipment_id, entry)

    def generate_maintenance_tasks(self, equipment_id, equipment_type):
        """Generate maintenance tasks for the equipment"""
        # Generate random past dates for last maintenance and calculate next due dates
        current_date = datetime.now()
        
        # Helper function to calculate next due date based on last done and frequency
        def calculate_next_due(last_done_str, frequency, unit):
            last_done = datetime.strptime(last_done_str, "%Y-%m-%d")
            if unit == "days":
                next_due = last_done + timedelta(days=frequency)
            elif unit == "weeks":
                next_due = last_done + timedelta(weeks=frequency)
            elif unit == "months":
                # Approximate months as 30 days
                next_due = last_done + timedelta(days=frequency * 30)
            else:  # years
                next_due = last_done + timedelta(days=frequency * 365)
            return next_due.strftime("%Y-%m-%d")
        
        # Common maintenance tasks for all equipment types
        common_tasks = [
            {
                "task_name": "General Inspection",
                "description": "Perform visual inspection of all components",
                "frequency": 30,
                "frequency_unit": "days",
                "estimated_time": 30,
                "time_unit": "minutes",
                "maintenance_procedure": "1. Check for visible damage\n2. Verify all safety features\n3. Test basic functionality\n4. Document any issues",
                "last_done": (current_date - timedelta(days=random.randint(1, 30))).strftime("%Y-%m-%d"),
                "required_parts": "[]"  # Added empty JSON array for required parts
            },
            {
                "task_name": "Lubrication",
                "description": "Apply lubricant to all moving parts",
                "frequency": 90,
                "frequency_unit": "days",
                "estimated_time": 45,
                "time_unit": "minutes",
                "maintenance_procedure": "1. Clean surfaces\n2. Apply manufacturer-recommended lubricant\n3. Wipe excess\n4. Verify smooth operation",
                "last_done": (current_date - timedelta(days=random.randint(1, 90))).strftime("%Y-%m-%d"),
                "required_parts": json.dumps([{"part_name": "Industrial Lubricant", "quantity": 1}])  # Added JSON array with a part
            }
        ]
        
        # Calculate next_due for common tasks
        for task in common_tasks:
            task["next_due"] = calculate_next_due(
                task["last_done"], 
                task["frequency"], 
                task["frequency_unit"]
            )
        
        # Type-specific maintenance tasks with required parts
        type_specific_tasks = {
            "conveyor": [
                {
                    "task_name": "Belt Tension Check",
                    "description": "Verify and adjust belt tension",
                    "frequency": 60,
                    "frequency_unit": "days",
                    "estimated_time": 60,
                    "time_unit": "minutes",
                    "maintenance_procedure": "1. Measure belt sag\n2. Adjust tensioners as needed\n3. Check alignment\n4. Test under load",
                    "last_done": (current_date - timedelta(days=random.randint(1, 60))).strftime("%Y-%m-%d"),
                    "required_parts": "[]"  # No parts required
                },
                {
                    "task_name": "Roller Inspection",
                    "description": "Inspect and clean all rollers",
                    "frequency": 180,
                    "frequency_unit": "days",
                    "estimated_time": 120,
                    "time_unit": "minutes",
                    "maintenance_procedure": "1. Check for wear and damage\n2. Clean debris\n3. Verify free rotation\n4. Replace damaged rollers",
                    "last_done": (current_date - timedelta(days=random.randint(1, 180))).strftime("%Y-%m-%d"),
                    "required_parts": json.dumps([{"part_name": "Conveyor Roller", "quantity": 2}, {"part_name": "Roller Bearing", "quantity": 4}])
                }
            ],
            "forklift": [
                {
                    "task_name": "Battery Maintenance",
                    "description": "Check and maintain battery",
                    "frequency": 30,
                    "frequency_unit": "days",
                    "estimated_time": 45,
                    "time_unit": "minutes",
                    "maintenance_procedure": "1. Check electrolyte levels\n2. Clean terminals\n3. Check charging system\n4. Test voltage under load",
                    "last_done": (current_date - timedelta(days=random.randint(1, 30))).strftime("%Y-%m-%d"),
                    "required_parts": json.dumps([{"part_name": "Battery Terminal Cleaner", "quantity": 1}, {"part_name": "Distilled Water", "quantity": 1}])
                },
                {
                    "task_name": "Hydraulic System Check",
                    "description": "Inspect hydraulic system for leaks and function",
                    "frequency": 90,
                    "frequency_unit": "days",
                    "estimated_time": 60,
                    "time_unit": "minutes",
                    "maintenance_procedure": "1. Check fluid levels\n2. Inspect hoses and fittings\n3. Test lift and tilt functions\n4. Check for drift under load",
                    "last_done": (current_date - timedelta(days=random.randint(1, 90))).strftime("%Y-%m-%d"),
                    "required_parts": json.dumps([{"part_name": "Hydraulic Fluid", "quantity": 1}, {"part_name": "Hydraulic Filter", "quantity": 1}])
                }
            ],
            "agv": [
                {
                    "task_name": "Sensor Calibration",
                    "description": "Calibrate navigation and safety sensors",
                    "frequency": 90,
                    "frequency_unit": "days",
                    "estimated_time": 120,
                    "time_unit": "minutes",
                    "maintenance_procedure": "1. Run diagnostic software\n2. Calibrate according to manufacturer specs\n3. Perform test runs\n4. Verify safety stop functions",
                    "last_done": (current_date - timedelta(days=random.randint(1, 90))).strftime("%Y-%m-%d"),
                    "required_parts": json.dumps([{"part_name": "Calibration Target", "quantity": 1}])
                },
                {
                    "task_name": "Software Update",
                    "description": "Check for and apply software updates",
                    "frequency": 180,
                    "frequency_unit": "days",
                    "estimated_time": 90,
                    "time_unit": "minutes",
                    "maintenance_procedure": "1. Connect to manufacturer portal\n2. Download latest firmware\n3. Apply updates\n4. Test all functions",
                    "last_done": (current_date - timedelta(days=random.randint(1, 180))).strftime("%Y-%m-%d"),
                    "required_parts": "[]"  # No parts required
                }
            ],
            "cold_storage": [
                {
                    "task_name": "Temperature Sensor Verification",
                    "description": "Verify accuracy of temperature sensors",
                    "frequency": 30,
                    "frequency_unit": "days",
                    "estimated_time": 60,
                    "time_unit": "minutes",
                    "maintenance_procedure": "1. Use calibrated reference thermometer\n2. Check multiple locations\n3. Adjust if needed\n4. Document readings",
                    "last_done": (current_date - timedelta(days=random.randint(1, 30))).strftime("%Y-%m-%d"),
                    "required_parts": "[]"  # No parts required
                },
                {
                    "task_name": "Refrigerant System Check",
                    "description": "Check refrigerant system for leaks and pressure",
                    "frequency": 90,
                    "frequency_unit": "days",
                    "estimated_time": 120,
                    "time_unit": "minutes",
                    "maintenance_procedure": "1. Check pressure gauges\n2. Inspect for oil spots\n3. Use leak detector\n4. Check compressor operation",
                    "last_done": (current_date - timedelta(days=random.randint(1, 90))).strftime("%Y-%m-%d"),
                    "required_parts": json.dumps([{"part_name": "Refrigerant", "quantity": 1}, {"part_name": "O-rings", "quantity": 4}])
                }
            ],
            "bottling": [
                {
                    "task_name": "Filling Valve Maintenance",
                    "description": "Clean and inspect filling valves",
                    "frequency": 30,
                    "frequency_unit": "days",
                    "estimated_time": 180,
                    "time_unit": "minutes",
                    "maintenance_procedure": "1. Disassemble valves\n2. Clean all components\n3. Replace o-rings\n4. Test fill accuracy",
                    "last_done": (current_date - timedelta(days=random.randint(1, 30))).strftime("%Y-%m-%d"),
                    "required_parts": json.dumps([{"part_name": "Valve O-ring Kit", "quantity": 1}, {"part_name": "Valve Spring", "quantity": 2}])
                },
                {
                    "task_name": "CIP System Verification",
                    "description": "Verify Clean-in-Place system operation",
                    "frequency": 90,
                    "frequency_unit": "days",
                    "estimated_time": 120,
                    "time_unit": "minutes",
                    "maintenance_procedure": "1. Check chemical concentrations\n2. Verify flow rates\n3. Test temperature control\n4. Run test cycle",
                    "last_done": (current_date - timedelta(days=random.randint(1, 90))).strftime("%Y-%m-%d"),
                    "required_parts": json.dumps([{"part_name": "CIP Cleaning Solution", "quantity": 2}, {"part_name": "Sanitizer", "quantity": 1}])
                }
            ]
        }
        
        # Calculate next_due for type-specific tasks
        for equipment_tasks in type_specific_tasks.values():
            for task in equipment_tasks:
                task["next_due"] = calculate_next_due(
                    task["last_done"], 
                    task["frequency"], 
                    task["frequency_unit"]
                )
        
        # Add common tasks
        for task in common_tasks:
            self.db_manager.add_maintenance_task(equipment_id, task)
        
        # Add type-specific tasks if available
        if equipment_type in type_specific_tasks:
            for task in type_specific_tasks[equipment_type]:
                self.db_manager.add_maintenance_task(equipment_id, task)

    def generate_special_tools(self, equipment_id, equipment_type):
        """Generate special tools for the equipment"""
        # Common tools for all equipment types
        common_tools = [
            {
                "tool_name": "Digital Multimeter",
                "specification": "Fluke 87V Industrial Multimeter",
                "purpose": "Electrical troubleshooting and maintenance",
                "location": "Main Tool Room"
            },
            {
                "tool_name": "Torque Wrench",
                "specification": "10-150 Nm, Digital Display",
                "purpose": "Precise fastening of critical components",
                "location": "Main Tool Room"
            }
        ]
        
        # Type-specific tools
        type_specific_tools = {
            "conveyor": [
                {
                    "tool_name": "Belt Tension Gauge",
                    "specification": "Digital, 0-500N range",
                    "purpose": "Measuring and adjusting belt tension",
                    "location": "Conveyor Maintenance Cabinet"
                },
                {
                    "tool_name": "Alignment Laser Tool",
                    "specification": "Red Line Laser, 50m range",
                    "purpose": "Aligning conveyor components",
                    "location": "Precision Tools Cabinet"
                }
            ],
            "forklift": [
                {
                    "tool_name": "Hydraulic Pressure Gauge",
                    "specification": "0-5000 PSI, Digital Display",
                    "purpose": "Testing hydraulic system pressure",
                    "location": "Forklift Maintenance Area"
                },
                {
                    "tool_name": "Battery Hydrometer",
                    "specification": "Specific Gravity Range 1.100-1.300",
                    "purpose": "Testing battery cell condition",
                    "location": "Battery Charging Station"
                }
            ],
            "agv": [
                {
                    "tool_name": "Navigation Calibration Kit",
                    "specification": "Manufacturer-specific calibration tools",
                    "purpose": "Calibrating navigation sensors",
                    "location": "Robotics Maintenance Room"
                },
                {
                    "tool_name": "Diagnostic Laptop",
                    "specification": "Ruggedized laptop with proprietary software",
                    "purpose": "Running diagnostics and updating firmware",
                    "location": "IT Department"
                }
            ],
            "cold_storage": [
                {
                    "tool_name": "Refrigerant Leak Detector",
                    "specification": "Electronic, detects all common refrigerants",
                    "purpose": "Locating refrigerant leaks",
                    "location": "HVAC Maintenance Area"
                },
                {
                    "tool_name": "Calibrated Thermometer",
                    "specification": "Digital, -50°C to +50°C, ±0.1°C accuracy",
                    "purpose": "Verifying temperature sensor accuracy",
                    "location": "Quality Control Office"
                }
            ],
            "bottling": [
                {
                    "tool_name": "Fill Height Gauge",
                    "specification": "Precision stainless steel, various bottle sizes",
                    "purpose": "Verifying correct fill levels",
                    "location": "Quality Control Lab"
                },
                {
                    "tool_name": "Specialized Valve Tool Kit",
                    "specification": "Manufacturer-specific tools for valve maintenance",
                    "purpose": "Servicing filling valves",
                    "location": "Bottling Line Maintenance Cabinet"
                }
            ]
        }
        
        # Add common tools
        for tool in common_tools:
            self.db_manager.add_special_tool(equipment_id, tool)
        
        # Add type-specific tools if available
        if equipment_type in type_specific_tools:
            for tool in type_specific_tools[equipment_type]:
                self.db_manager.add_special_tool(equipment_id, tool)

    def generate_safety_info(self, equipment_id, equipment_type):
        """Generate safety information for the equipment"""
        # Default safety info
        safety_info = {
            "hazards": "Always follow standard safety protocols when operating or maintaining this equipment.",
            "operating_precautions": "Wear appropriate PPE including safety glasses, gloves, and steel-toed boots.",
            "emergency_procedures": "In case of emergency, press the emergency stop button and notify supervisor immediately.",
            "ppe_requirements": "Safety glasses, gloves, steel-toed boots, high-visibility vest.",
            "hazardous_materials": "None",
            "lockout_procedures": "1. Notify affected personnel\n2. Shut down equipment\n3. Disconnect main power source\n4. Apply lockout device and tag\n5. Verify zero energy state"
        }
        
        # Type-specific safety info
        if equipment_type == "conveyor":
            safety_info.update({
                "hazards": "Moving parts can cause entanglement, crushing, or pinching injuries. Electrical components pose shock hazard.",
                "operating_precautions": "Never reach into moving conveyor. Lock out/tag out before maintenance. Keep loose clothing and jewelry away from moving parts.",
                "emergency_procedures": "Press emergency stop button located at either end of conveyor. Clear area of personnel and notify maintenance.",
                "ppe_requirements": "Safety glasses, gloves, steel-toed boots, high-visibility vest. Hearing protection in high-noise areas.",
                "hazardous_materials": "Lubricants, cleaning solvents",
                "lockout_procedures": "1. Notify affected personnel\n2. Turn off conveyor at control panel\n3. Turn main disconnect to OFF position\n4. Apply lock and tag to disconnect\n5. Test start button to verify power is off\n6. Release any stored energy (gravity, pneumatic, etc.)"
            })
        elif equipment_type == "forklift":
            safety_info.update({
                "hazards": "Tipping hazard, collision hazard, falling load hazard, battery acid exposure (electric models).",
                "operating_precautions": "Only certified operators may use this equipment. Always wear seatbelt. Never exceed load capacity. Maintain clear visibility.",
                "emergency_procedures": "In case of tipping, brace yourself and lean away from the direction of the tip. For battery issues, use emergency eyewash station.",
                "ppe_requirements": "Safety glasses, gloves, steel-toed boots, high-visibility vest. Face shield when handling batteries.",
                "hazardous_materials": "Battery acid, hydraulic fluid, engine oil, fuel",
                "lockout_procedures": "1. Park forklift in designated area\n2. Lower forks to ground\n3. Set parking brake\n4. Turn off ignition and remove key\n5. For electric models: disconnect battery\n6. For fuel models: close fuel valve\n7. Place 'Do Not Operate' tag on steering wheel"
            })
        elif equipment_type == "agv":
            safety_info.update({
                "hazards": "Collision hazard, crushing hazard, electrical hazard during maintenance.",
                "operating_precautions": "Maintain clear pathways. Never stand in AGV travel paths. Follow lockout/tagout procedures during maintenance.",
                "emergency_procedures": "Press emergency stop button on AGV or at control stations. Clear area and notify robotics technician.",
                "ppe_requirements": "Safety glasses, steel-toed boots, high-visibility vest. Anti-static wristband during electronic maintenance.",
                "hazardous_materials": "Battery chemicals, electronic components",
                "lockout_procedures": "1. Stop AGV using control system\n2. Press emergency stop button\n3. Power down using main switch\n4. Disconnect battery or power supply\n5. Apply lock and tag\n6. Wait 5 minutes for capacitors to discharge\n7. Verify zero energy with voltmeter"
            })
        elif equipment_type == "cold_storage":
            safety_info.update({
                "hazards": "Cold temperature exposure, refrigerant leaks, slippery surfaces, confined space hazards.",
                "operating_precautions": "Limit exposure time in cold areas. Check refrigerant levels regularly. Use caution on potentially icy surfaces.",
                "emergency_procedures": "For refrigerant leaks, evacuate area and ventilate. For cold exposure, move to warm area and seek medical attention if needed.",
                "ppe_requirements": "Insulated gloves, cold-weather clothing, non-slip footwear, respirator (for refrigerant work).",
                "hazardous_materials": "Refrigerants (R-404A, R-134a, Ammonia), glycol",
                "lockout_procedures": "1. Shut down system at control panel\n2. Turn main electrical disconnect to OFF\n3. Close main refrigerant valves\n4. Apply locks and tags to disconnects and valves\n5. Verify system pressure is zero before opening refrigerant lines\n6. For confined space entry: test atmosphere and use buddy system"
            })
        elif equipment_type == "bottling":
            safety_info.update({
                "hazards": "Moving mechanical parts, pressurized systems, chemical exposure during cleaning.",
                "operating_precautions": "Never reach into operating machinery. Follow proper lockout/tagout procedures. Use proper ventilation during cleaning.",
                "emergency_procedures": "Press emergency stop button. For chemical exposure, use emergency shower/eyewash and refer to SDS.",
                "ppe_requirements": "Safety glasses, gloves, steel-toed boots, chemical-resistant apron during cleaning operations.",
                "hazardous_materials": "Cleaning chemicals, sanitizers, lubricants",
                "lockout_procedures": "1. Complete current production cycle if possible\n2. Shut down at control panel\n3. Turn main power disconnect to OFF\n4. Close air supply and water supply valves\n5. Relieve pressure from pneumatic lines\n6. Apply locks and tags to all energy sources\n7. Verify zero energy state before maintenance"
            })
        
        # Save safety info to database
        self.db_manager.save_safety_info(equipment_id, safety_info)

    def create_coca_cola_equipment_data(self, counts):
        """Create detailed equipment data for a Coca-Cola production line"""
        equipment_list = []
        current_year = datetime.now().year
        
        # 1. Conveyor Belts
        conveyor_manufacturers = ["Dematic", "Interroll", "Siemens Logistics", "Honeywell Intelligrated", "Daifuku"]
        conveyor_models = ["SpeedLine", "FlexConveyor", "PowerRoller", "GravityFlow", "AccuGlide"]
        conveyor_locations = ["Bottling Line A", "Bottling Line B", "Packaging Area", "Distribution Center", "Loading Dock"]
        
        for i in range(1, counts["conveyor_count"] + 1):
            manufacturer = random.choice(conveyor_manufacturers)
            model = random.choice(conveyor_models)
            location = random.choice(conveyor_locations)
            
            # Create custom fields based on conveyor type
            custom_fields = {
                "Belt Width": f"{random.choice([400, 500, 600, 800])} mm",
                "Belt Length": f"{random.randint(5, 30)} meters",
                "Speed Range": f"{random.randint(10, 30)}-{random.randint(40, 100)} m/min",
                "Load Capacity": f"{random.randint(50, 200)} kg/m",
                "Motor Power": f"{random.choice([0.75, 1.1, 1.5, 2.2, 3.0])} kW"
            }
            
            equipment_list.append({
                "part_number": f"CB-{current_year}-{i:03d}",
                "equipment_name": f"Coca-Cola {model} Conveyor Belt #{i}",
                "manufacturer": manufacturer,
                "model": f"{model}-{random.randint(1000, 9999)}",
                "serial_number": f"SN-CB-{current_year}-{random.randint(10000, 99999)}",
                "location": location,
                "installation_date": (datetime.now() - timedelta(days=random.randint(30, 365))).strftime("%Y-%m-%d"),
                "status": random.choice(["Active", "Active", "Active", "Under Maintenance"]),
                "custom_fields": json.dumps(custom_fields)
            })
        
        # 2. Forklifts
        forklift_manufacturers = ["Toyota", "Hyster", "Crown", "Yale", "Jungheinrich"]
        forklift_models = ["ReachTruck", "CounterBalance", "OrderPicker", "PalletJack", "TurretTruck"]
        forklift_locations = ["Warehouse A", "Warehouse B", "Distribution Center", "Loading Bay", "Cold Storage"]
        
        for i in range(1, counts["forklift_count"] + 1):
            manufacturer = random.choice(forklift_manufacturers)
            model = random.choice(forklift_models)
            location = random.choice(forklift_locations)
            
            # Create custom fields based on forklift type
            custom_fields = {
                "Lift Capacity": f"{random.choice([1.5, 2.0, 2.5, 3.0, 3.5])} tons",
                "Lift Height": f"{random.randint(3, 12)} meters",
                "Power Source": random.choice(["Electric", "LPG", "Diesel", "Hybrid"]),
                "Battery Capacity": f"{random.randint(48, 80)} V / {random.randint(400, 1200)} Ah",
                "Operating Hours": f"{random.randint(2000, 8000)} hours",
                "Last Maintenance": (datetime.now() - timedelta(days=random.randint(1, 90))).strftime("%Y-%m-%d")
            }
            
            equipment_list.append({
                "part_number": f"FL-{current_year}-{i:03d}",
                "equipment_name": f"Coca-Cola {manufacturer} {model} Forklift #{i}",
                "manufacturer": manufacturer,
                "model": f"{model}-{random.randint(1000, 9999)}",
                "serial_number": f"SN-FL-{current_year}-{random.randint(10000, 99999)}",
                "location": location,
                "installation_date": (datetime.now() - timedelta(days=random.randint(30, 730))).strftime("%Y-%m-%d"),
                "status": random.choice(["Active", "Active", "Under Maintenance", "Inactive"]),
                "custom_fields": json.dumps(custom_fields)
            })
        
        # 3. Automated Guided Vehicles (AGVs)
        agv_manufacturers = ["Seegrid", "Fetch Robotics", "MiR", "Locus Robotics", "Vecna Robotics"]
        agv_models = ["TugBot", "CarryBot", "PalletMover", "PickBot", "FlexNav"]
        agv_locations = ["Production Floor", "Warehouse Aisles", "Cross-Docking Area", "Staging Area", "Shipping Zone"]
        
        for i in range(1, counts["agv_count"] + 1):
            manufacturer = random.choice(agv_manufacturers)
            model = random.choice(agv_models)
            location = random.choice(agv_locations)
            
            # Create custom fields based on AGV type
            custom_fields = {
                "Navigation System": random.choice(["LiDAR", "Vision-based", "Magnetic Tape", "QR Code", "Hybrid"]),
                "Payload Capacity": f"{random.randint(100, 1500)} kg",
                "Battery Runtime": f"{random.randint(6, 16)} hours",
                "Charging Time": f"{random.randint(1, 4)} hours",
                "Maximum Speed": f"{random.randint(1, 7)} m/s",
                "Safety Features": random.choice([
                    "360° Sensors, Emergency Stop", 
                    "Obstacle Detection, Path Planning", 
                    "Human Detection, Automatic Braking"
                ]),
                "Software Version": f"{random.randint(1, 9)}.{random.randint(0, 9)}.{random.randint(0, 9)}"
            }
            
            equipment_list.append({
                "part_number": f"AGV-{current_year}-{i:03d}",
                "equipment_name": f"Coca-Cola {manufacturer} {model} AGV #{i}",
                "manufacturer": manufacturer,
                "model": f"{model}-{random.randint(1000, 9999)}",
                "serial_number": f"SN-AGV-{current_year}-{random.randint(10000, 99999)}",
                "location": location,
                "installation_date": (datetime.now() - timedelta(days=random.randint(30, 365))).strftime("%Y-%m-%d"),
                "status": random.choice(["Active", "Active", "Active", "Under Maintenance"]),
                "custom_fields": json.dumps(custom_fields)
            })
        
        # 4. Cold Storage Units
        cold_manufacturers = ["Carrier", "Thermo King", "Trane", "Danfoss", "Emerson"]
        cold_models = ["CryoStore", "FreezeMaster", "CoolCell", "ArcticVault", "PolarKeep"]
        cold_locations = ["Finished Goods Area", "Raw Materials Storage", "Distribution Hub", "Shipping Prep", "Quality Control"]
        
        for i in range(1, counts["cold_storage_count"] + 1):
            manufacturer = random.choice(cold_manufacturers)
            model = random.choice(cold_models)
            location = random.choice(cold_locations)
            
            # Create custom fields based on cold storage type
            custom_fields = {
                "Temperature Range": f"{random.choice([-30, -25, -20, -15, -10, -5, 0, 2, 4])}°C to {random.choice([-5, 0, 2, 4, 8])}°C",
                "Storage Capacity": f"{random.randint(50, 500)} m³",
                "Refrigerant Type": random.choice(["R-404A", "R-134a", "R-507", "R-290", "R-717 (Ammonia)"]),
                "Power Consumption": f"{random.randint(5, 50)} kW/h",
                "Humidity Control": f"{random.randint(30, 90)}%",
                "Backup System": random.choice(["Generator", "Battery", "Dual Compressor", "None"]),
                "Temperature Monitoring": random.choice([
                    "IoT Sensors with Cloud Reporting", 
                    "SCADA Integration", 
                    "Local Digital Display with Alarms"
                ])
            }
            
            equipment_list.append({
                "part_number": f"CS-{current_year}-{i:03d}",
                "equipment_name": f"Coca-Cola {model} Cold Storage Unit #{i}",
                "manufacturer": manufacturer,
                "model": f"{model}-{random.randint(1000, 9999)}",
                "serial_number": f"SN-CS-{current_year}-{random.randint(10000, 99999)}",
                "location": location,
                "installation_date": (datetime.now() - timedelta(days=random.randint(30, 1095))).strftime("%Y-%m-%d"),
                "status": random.choice(["Active", "Active", "Under Maintenance", "Inactive"]),
                "custom_fields": json.dumps(custom_fields)
            })
            
        # 5. Bottling Machines
        bottling_manufacturers = ["Krones", "KHS", "Sidel", "GEA", "Tetra Pak"]
        bottling_models = ["SpeedFill", "CleanCap", "PrecisionFill", "UltraRinse", "QuickSeal"]
        bottling_locations = ["Bottling Hall A", "Bottling Hall B", "Production Line 1", "Production Line 2", "Production Line 3"]
        
        for i in range(1, counts["bottling_count"] + 1):
            manufacturer = random.choice(bottling_manufacturers)
            model = random.choice(bottling_models)
            location = random.choice(bottling_locations)
            
            # Create custom fields based on bottling machine type
            custom_fields = {
                "Filling Speed": f"{random.randint(10000, 50000)} bottles/hour",
                "Bottle Size Range": f"{random.choice([250, 330, 500])} ml to {random.choice([1000, 1500, 2000])} ml",
                "Cleaning System": random.choice(["CIP (Clean-in-Place)", "SIP (Sterilize-in-Place)", "Manual"]),
                "Control System": random.choice(["Siemens S7", "Allen Bradley", "Mitsubishi", "Omron"]),
                "Sanitization Method": random.choice(["Hot Water", "Steam", "Chemical", "UV Light"]),
                "Last Validation": (datetime.now() - timedelta(days=random.randint(1, 180))).strftime("%Y-%m-%d"),
                "Production Efficiency": f"{random.randint(85, 99)}%"
            }
            
            equipment_list.append({
                "part_number": f"BM-{current_year}-{i:03d}",
                "equipment_name": f"Coca-Cola {manufacturer} {model} Bottling Machine #{i}",
                "manufacturer": manufacturer,
                "model": f"{model}-{random.randint(1000, 9999)}",
                "serial_number": f"SN-BM-{current_year}-{random.randint(10000, 99999)}",
                "location": location,
                "installation_date": (datetime.now() - timedelta(days=random.randint(30, 1825))).strftime("%Y-%m-%d"),
                "status": random.choice(["Active", "Active", "Under Maintenance"]),
                "custom_fields": json.dumps(custom_fields)
            })
            
        return equipment_list 