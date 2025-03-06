"""
Maintenance Report Dialog - Dynamic form for maintenance reports
"""

import os
import json
from datetime import datetime

from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
                              QTabWidget, QWidget, QFormLayout, QLineEdit, QTextEdit,
                              QComboBox, QCheckBox, QSpinBox, QDoubleSpinBox, QDateEdit,
                              QTimeEdit, QScrollArea, QFileDialog, QMessageBox, QGroupBox,
                              QRadioButton, QButtonGroup, QGridLayout, QFrame, QListWidget, QListWidgetItem)
from PySide6.QtCore import Qt, QDate, QTime
from PySide6.QtGui import QFont, QPixmap

class MaintenanceReportDialog(QDialog):
    """Dialog for creating maintenance reports with dynamic fields based on equipment type"""
    
    def __init__(self, work_order, equipment, craftsman_id, db_manager, parent=None):
        super().__init__(parent)
        self.work_order = work_order
        self.equipment = equipment
        self.craftsman_id = craftsman_id
        self.db_manager = db_manager
        self.form_fields = {}
        self.uploaded_files = []
        
        self.setWindowTitle(f"Maintenance Report - Work Order #{work_order['work_order_id']}")
        self.setMinimumSize(800, 700)
        
        layout = QVBoxLayout(self)
        
        # Create header with work order and equipment info
        self.create_header(layout)
        
        # Create tab widget for report sections
        self.tab_widget = QTabWidget()
        layout.addWidget(self.tab_widget)
        
        # Create tabs based on equipment type
        self.create_report_tabs()
        
        # Add comments section
        self.create_comments_section(layout)
        
        # Add buttons
        buttons_layout = QHBoxLayout()
        
        save_btn = QPushButton("Submit Report")
        save_btn.clicked.connect(self.submit_report)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        
        buttons_layout.addWidget(save_btn)
        buttons_layout.addWidget(cancel_btn)
        
        layout.addLayout(buttons_layout)
    
    def create_header(self, layout):
        """Create header with work order and equipment info"""
        header_widget = QWidget()
        header_layout = QHBoxLayout(header_widget)
        
        # Work order info
        wo_layout = QVBoxLayout()
        
        wo_title = QLabel(f"<b>{self.work_order['title']}</b>")
        wo_title.setFont(QFont("Arial", 14))
        wo_layout.addWidget(wo_title)
        
        wo_details = QLabel(f"Work Order #{self.work_order['work_order_id']} - Due: {self.work_order['due_date']}")
        wo_layout.addWidget(wo_details)
        
        header_layout.addLayout(wo_layout)
        header_layout.addStretch()
        
        # Equipment info
        equip_layout = QVBoxLayout()
        
        equip_name = QLabel(f"<b>{self.equipment['equipment_name']}</b>")
        equip_name.setFont(QFont("Arial", 12))
        equip_layout.addWidget(equip_name)
        
        equip_details = QLabel(f"Model: {self.equipment.get('model', 'N/A')} - S/N: {self.equipment.get('serial_number', 'N/A')}")
        equip_layout.addWidget(equip_details)
        
        header_layout.addLayout(equip_layout)
        
        layout.addWidget(header_widget)
    
    def create_report_tabs(self):
        """Create tabs based on equipment type and specialization"""
        # Get equipment template to determine fields
        template_id = self.equipment.get('template_id')
        equipment_type = self.get_equipment_type()
        
        # Create general information tab (always present)
        self.create_general_tab()
        
        # Create inspection tab (always present)
        self.create_inspection_tab()
        
        # Create equipment-specific tabs
        if equipment_type == "mechanical":
            self.create_mechanical_tab()
        elif equipment_type == "electrical":
            self.create_electrical_tab()
        elif equipment_type == "hvac":
            self.create_hvac_tab()
        elif equipment_type == "plumbing":
            self.create_plumbing_tab()
        
        # Create measurements tab (always present)
        self.create_measurements_tab()
        
        # Create parts and materials tab (always present)
        self.create_parts_tab()
        
        # Create attachments tab (always present)
        self.create_attachments_tab()
    
    def get_equipment_type(self):
        """Determine equipment type based on template or name"""
        # First check if we have a specialization field
        if self.equipment.get('specialization'):
            return self.equipment['specialization'].lower()
        
        # Check custom fields
        custom_fields = self.equipment.get('custom_fields', {})
        if isinstance(custom_fields, str):
            try:
                custom_fields = json.loads(custom_fields)
            except:
                custom_fields = {}
        
        if custom_fields.get('equipment_type'):
            return custom_fields['equipment_type'].lower()
        
        # Try to determine from equipment name or model
        equipment_name = self.equipment['equipment_name'].lower()
        model = self.equipment.get('model', '').lower()
        
        # Check for keywords in name or model
        mechanical_keywords = ['pump', 'motor', 'engine', 'compressor', 'gear', 'valve', 'bearing']
        electrical_keywords = ['electrical', 'circuit', 'breaker', 'transformer', 'generator', 'panel', 'switch']
        hvac_keywords = ['hvac', 'air conditioner', 'heater', 'furnace', 'boiler', 'chiller', 'ventilation']
        plumbing_keywords = ['plumbing', 'pipe', 'drain', 'water', 'sewage', 'toilet', 'faucet']
        
        for keyword in mechanical_keywords:
            if keyword in equipment_name or keyword in model:
                return "mechanical"
        
        for keyword in electrical_keywords:
            if keyword in equipment_name or keyword in model:
                return "electrical"
        
        for keyword in hvac_keywords:
            if keyword in equipment_name or keyword in model:
                return "hvac"
        
        for keyword in plumbing_keywords:
            if keyword in equipment_name or keyword in model:
                return "plumbing"
        
        # Default to mechanical if we can't determine
        return "mechanical"
    
    def create_general_tab(self):
        """Create general information tab"""
        general_widget = QWidget()
        layout = QVBoxLayout(general_widget)
        
        # Create scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        # Create content widget
        content_widget = QWidget()
        form_layout = QFormLayout(content_widget)
        form_layout.setContentsMargins(20, 20, 20, 20)
        form_layout.setSpacing(15)
        
        # Add general information fields
        self.form_fields['general'] = {}
        
        # Maintenance type
        maintenance_type = QComboBox()
        maintenance_type.addItems(["Preventive", "Corrective", "Predictive", "Emergency"])
        form_layout.addRow("Maintenance Type:", maintenance_type)
        self.form_fields['general']['maintenance_type'] = maintenance_type
        
        # Maintenance date and time
        date_widget = QWidget()
        date_layout = QHBoxLayout(date_widget)
        date_layout.setContentsMargins(0, 0, 0, 0)
        
        maintenance_date = QDateEdit()
        maintenance_date.setCalendarPopup(True)
        maintenance_date.setDate(QDate.currentDate())
        
        maintenance_time = QTimeEdit()
        maintenance_time.setTime(QTime.currentTime())
        
        date_layout.addWidget(maintenance_date)
        date_layout.addWidget(maintenance_time)
        
        form_layout.addRow("Date & Time:", date_widget)
        self.form_fields['general']['maintenance_date'] = maintenance_date
        self.form_fields['general']['maintenance_time'] = maintenance_time
        
        # Duration
        duration_widget = QWidget()
        duration_layout = QHBoxLayout(duration_widget)
        duration_layout.setContentsMargins(0, 0, 0, 0)
        
        hours = QSpinBox()
        hours.setRange(0, 24)
        hours.setSuffix(" hours")
        
        minutes = QSpinBox()
        minutes.setRange(0, 59)
        minutes.setSuffix(" minutes")
        
        duration_layout.addWidget(hours)
        duration_layout.addWidget(minutes)
        
        form_layout.addRow("Duration:", duration_widget)
        self.form_fields['general']['duration_hours'] = hours
        self.form_fields['general']['duration_minutes'] = minutes
        
        # Maintenance personnel
        personnel = QLineEdit()
        personnel.setText(f"{self.craftsman_id}")  # Default to current craftsman
        form_layout.addRow("Personnel ID:", personnel)
        self.form_fields['general']['personnel'] = personnel
        
        # Initial condition
        initial_condition = QComboBox()
        initial_condition.addItems(["Operational", "Partially Operational", "Non-Operational", "Unknown"])
        form_layout.addRow("Initial Condition:", initial_condition)
        self.form_fields['general']['initial_condition'] = initial_condition
        
        # Final condition
        final_condition = QComboBox()
        final_condition.addItems(["Operational", "Partially Operational", "Non-Operational", "Requires Further Attention"])
        form_layout.addRow("Final Condition:", final_condition)
        self.form_fields['general']['final_condition'] = final_condition
        
        # Set the content widget as the scroll area's widget
        scroll.setWidget(content_widget)
        layout.addWidget(scroll)
        
        self.tab_widget.addTab(general_widget, "General Information")
    
    def create_inspection_tab(self):
        """Create inspection checklist tab"""
        inspection_widget = QWidget()
        layout = QVBoxLayout(inspection_widget)
        
        # Create scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        # Create content widget
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(20, 20, 20, 20)
        content_layout.setSpacing(15)
        
        # Add inspection fields
        self.form_fields['inspection'] = {}
        
        # Visual inspection section
        visual_group = QGroupBox("Visual Inspection")
        visual_layout = QFormLayout(visual_group)
        
        # Create visual inspection checkboxes
        visual_items = [
            "External damage", "Corrosion", "Leaks", "Loose parts",
            "Unusual wear", "Debris/contamination", "Alignment issues"
        ]
        
        for item in visual_items:
            checkbox = QCheckBox()
            visual_layout.addRow(item, checkbox)
            self.form_fields['inspection'][f"visual_{item.lower().replace('/', '_').replace(' ', '_')}"] = checkbox
        
        content_layout.addWidget(visual_group)
        
        # Operational inspection section
        operational_group = QGroupBox("Operational Inspection")
        operational_layout = QFormLayout(operational_group)
        
        # Create operational inspection checkboxes
        operational_items = [
            "Unusual noise", "Vibration", "Overheating", "Slow operation",
            "Intermittent operation", "Control issues", "Safety devices functioning"
        ]
        
        for item in operational_items:
            checkbox = QCheckBox()
            operational_layout.addRow(item, checkbox)
            self.form_fields['inspection'][f"operational_{item.lower().replace(' ', '_')}"] = checkbox
        
        content_layout.addWidget(operational_group)
        
        # Additional findings
        findings_label = QLabel("Additional Findings:")
        content_layout.addWidget(findings_label)
        
        findings_text = QTextEdit()
        findings_text.setPlaceholderText("Enter any additional inspection findings here...")
        content_layout.addWidget(findings_text)
        self.form_fields['inspection']['additional_findings'] = findings_text
        
        # Set the content widget as the scroll area's widget
        scroll.setWidget(content_widget)
        layout.addWidget(scroll)
        
        self.tab_widget.addTab(inspection_widget, "Inspection Checklist")
    
    def create_mechanical_tab(self):
        """Create mechanical-specific tab"""
        mechanical_widget = QWidget()
        layout = QVBoxLayout(mechanical_widget)
        
        # Create scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        # Create content widget
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(20, 20, 20, 20)
        content_layout.setSpacing(15)
        
        # Add mechanical fields
        self.form_fields['mechanical'] = {}
        
        # Lubrication section
        lubrication_group = QGroupBox("Lubrication")
        lubrication_layout = QFormLayout(lubrication_group)
        
        # Lubrication performed
        lubrication_performed = QCheckBox()
        lubrication_layout.addRow("Lubrication Performed:", lubrication_performed)
        self.form_fields['mechanical']['lubrication_performed'] = lubrication_performed
        
        # Lubricant type
        lubricant_type = QComboBox()
        lubricant_type.addItems(["N/A", "Oil", "Grease", "Other"])
        lubrication_layout.addRow("Lubricant Type:", lubricant_type)
        self.form_fields['mechanical']['lubricant_type'] = lubricant_type
        
        # Lubricant brand/specification
        lubricant_brand = QLineEdit()
        lubrication_layout.addRow("Brand/Specification:", lubricant_brand)
        self.form_fields['mechanical']['lubricant_brand'] = lubricant_brand
        
        # Lubricant quantity
        lubricant_quantity = QLineEdit()
        lubrication_layout.addRow("Quantity Used:", lubricant_quantity)
        self.form_fields['mechanical']['lubricant_quantity'] = lubricant_quantity
        
        content_layout.addWidget(lubrication_group)
        
        # Mechanical components section
        components_group = QGroupBox("Component Inspection")
        components_layout = QFormLayout(components_group)
        
        # Create component inspection fields
        component_items = [
            "Bearings", "Seals", "Belts/chains", "Couplings", 
            "Gears", "Shafts", "Valves", "Filters"
        ]
        
        for item in component_items:
            condition = QComboBox()
            condition.addItems(["Not Inspected", "Good", "Fair", "Poor", "Replaced"])
            components_layout.addRow(f"{item} Condition:", condition)
            self.form_fields['mechanical'][f"{item.lower().replace('/', '_')}_condition"] = condition
        
        content_layout.addWidget(components_group)
        
        # Alignment section
        alignment_group = QGroupBox("Alignment")
        alignment_layout = QFormLayout(alignment_group)
        
        # Alignment checked
        alignment_checked = QCheckBox()
        alignment_layout.addRow("Alignment Checked:", alignment_checked)
        self.form_fields['mechanical']['alignment_checked'] = alignment_checked
        
        # Alignment status
        alignment_status = QComboBox()
        alignment_status.addItems(["N/A", "Within Specification", "Adjusted", "Requires Further Adjustment"])
        alignment_layout.addRow("Alignment Status:", alignment_status)
        self.form_fields['mechanical']['alignment_status'] = alignment_status
        
        # Alignment method
        alignment_method = QLineEdit()
        alignment_layout.addRow("Alignment Method:", alignment_method)
        self.form_fields['mechanical']['alignment_method'] = alignment_method
        
        content_layout.addWidget(alignment_group)
        
        # Set the content widget as the scroll area's widget
        scroll.setWidget(content_widget)
        layout.addWidget(scroll)
        
        self.tab_widget.addTab(mechanical_widget, "Mechanical")
    
    def create_electrical_tab(self):
        """Create electrical-specific tab"""
        electrical_widget = QWidget()
        layout = QVBoxLayout(electrical_widget)
        
        # Create scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        # Create content widget
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(20, 20, 20, 20)
        content_layout.setSpacing(15)
        
        # Add electrical fields
        self.form_fields['electrical'] = {}
        
        # Power section
        power_group = QGroupBox("Power Measurements")
        power_layout = QFormLayout(power_group)
        
        # Voltage measurements
        voltage_widget = QWidget()
        voltage_layout = QHBoxLayout(voltage_widget)
        voltage_layout.setContentsMargins(0, 0, 0, 0)
        
        voltage_l1 = QDoubleSpinBox()
        voltage_l1.setRange(0, 1000)
        voltage_l1.setSuffix(" V")
        voltage_l1.setDecimals(1)
        
        voltage_l2 = QDoubleSpinBox()
        voltage_l2.setRange(0, 1000)
        voltage_l2.setSuffix(" V")
        voltage_l2.setDecimals(1)
        
        voltage_l3 = QDoubleSpinBox()
        voltage_l3.setRange(0, 1000)
        voltage_l3.setSuffix(" V")
        voltage_l3.setDecimals(1)
        
        voltage_layout.addWidget(QLabel("L1:"))
        voltage_layout.addWidget(voltage_l1)
        voltage_layout.addWidget(QLabel("L2:"))
        voltage_layout.addWidget(voltage_l2)
        voltage_layout.addWidget(QLabel("L3:"))
        voltage_layout.addWidget(voltage_l3)
        
        power_layout.addRow("Voltage:", voltage_widget)
        self.form_fields['electrical']['voltage_l1'] = voltage_l1
        self.form_fields['electrical']['voltage_l2'] = voltage_l2
        self.form_fields['electrical']['voltage_l3'] = voltage_l3
        
        # Current measurements
        current_widget = QWidget()
        current_layout = QHBoxLayout(current_widget)
        current_layout.setContentsMargins(0, 0, 0, 0)
        
        current_l1 = QDoubleSpinBox()
        current_l1.setRange(0, 1000)
        current_l1.setSuffix(" A")
        current_l1.setDecimals(2)
        
        current_l2 = QDoubleSpinBox()
        current_l2.setRange(0, 1000)
        current_l2.setSuffix(" A")
        current_l2.setDecimals(2)
        
        current_l3 = QDoubleSpinBox()
        current_l3.setRange(0, 1000)
        current_l3.setSuffix(" A")
        current_l3.setDecimals(2)
        
        current_layout.addWidget(QLabel("L1:"))
        current_layout.addWidget(current_l1)
        current_layout.addWidget(QLabel("L2:"))
        current_layout.addWidget(current_l2)
        current_layout.addWidget(QLabel("L3:"))
        current_layout.addWidget(current_l3)
        
        power_layout.addRow("Current:", current_widget)
        self.form_fields['electrical']['current_l1'] = current_l1
        self.form_fields['electrical']['current_l2'] = current_l2
        self.form_fields['electrical']['current_l3'] = current_l3
        
        # Power factor
        power_factor = QDoubleSpinBox()
        power_factor.setRange(0, 1)
        power_factor.setDecimals(2)
        power_factor.setSingleStep(0.01)
        power_layout.addRow("Power Factor:", power_factor)
        self.form_fields['electrical']['power_factor'] = power_factor
        
        # Frequency
        frequency = QDoubleSpinBox()
        frequency.setRange(0, 100)
        frequency.setValue(60)
        frequency.setSuffix(" Hz")
        frequency.setDecimals(1)
        power_layout.addRow("Frequency:", frequency)
        self.form_fields['electrical']['frequency'] = frequency
        
        content_layout.addWidget(power_group)
        
        # Insulation section
        insulation_group = QGroupBox("Insulation Testing")
        insulation_layout = QFormLayout(insulation_group)
        
        # Insulation test performed
        insulation_tested = QCheckBox()
        insulation_layout.addRow("Insulation Test Performed:", insulation_tested)
        self.form_fields['electrical']['insulation_tested'] = insulation_tested
        
        # Insulation resistance
        insulation_resistance = QDoubleSpinBox()
        insulation_resistance.setRange(0, 10000)
        insulation_resistance.setSuffix(" MΩ")
        insulation_layout.addRow("Insulation Resistance:", insulation_resistance)
        self.form_fields['electrical']['insulation_resistance'] = insulation_resistance
        
        # Test voltage
        test_voltage = QSpinBox()
        test_voltage.setRange(0, 5000)
        test_voltage.setSuffix(" V")
        insulation_layout.addRow("Test Voltage:", test_voltage)
        self.form_fields['electrical']['test_voltage'] = test_voltage
        
        content_layout.addWidget(insulation_group)
        
        # Components section
        components_group = QGroupBox("Component Inspection")
        components_layout = QFormLayout(components_group)
        
        # Create component inspection fields
        component_items = [
            "Contactors", "Relays", "Circuit breakers", "Fuses", 
            "Terminals", "Wiring", "Controls", "Grounding"
        ]
        
        for item in component_items:
            condition = QComboBox()
            condition.addItems(["Not Inspected", "Good", "Fair", "Poor", "Replaced"])
            components_layout.addRow(f"{item} Condition:", condition)
            self.form_fields['electrical'][f"{item.lower().replace(' ', '_')}_condition"] = condition
        
        content_layout.addWidget(components_group)
        
        # Set the content widget as the scroll area's widget
        scroll.setWidget(content_widget)
        layout.addWidget(scroll)
        
        self.tab_widget.addTab(electrical_widget, "Electrical")
    
    def create_hvac_tab(self):
        """Create HVAC-specific tab"""
        hvac_widget = QWidget()
        layout = QVBoxLayout(hvac_widget)
        
        # Create scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        # Create content widget
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(20, 20, 20, 20)
        content_layout.setSpacing(15)
        
        # Add HVAC fields
        self.form_fields['hvac'] = {}
        
        # Temperature measurements
        temp_group = QGroupBox("Temperature Measurements")
        temp_layout = QFormLayout(temp_group)
        
        # Supply air temperature
        supply_temp = QDoubleSpinBox()
        supply_temp.setRange(-50, 150)
        supply_temp.setSuffix(" °F")
        supply_temp.setDecimals(1)
        temp_layout.addRow("Supply Air Temperature:", supply_temp)
        self.form_fields['hvac']['supply_temp'] = supply_temp
        
        # Return air temperature
        return_temp = QDoubleSpinBox()
        return_temp.setRange(-50, 150)
        return_temp.setSuffix(" °F")
        return_temp.setDecimals(1)
        temp_layout.addRow("Return Air Temperature:", return_temp)
        self.form_fields['hvac']['return_temp'] = return_temp
        
        # Ambient temperature
        ambient_temp = QDoubleSpinBox()
        ambient_temp.setRange(-50, 150)
        ambient_temp.setSuffix(" °F")
        ambient_temp.setDecimals(1)
        temp_layout.addRow("Ambient Temperature:", ambient_temp)
        self.form_fields['hvac']['ambient_temp'] = ambient_temp
        
        # Temperature differential
        temp_differential = QDoubleSpinBox()
        temp_differential.setRange(0, 100)
        temp_differential.setSuffix(" °F")
        temp_differential.setDecimals(1)
        temp_layout.addRow("Temperature Differential:", temp_differential)
        self.form_fields['hvac']['temp_differential'] = temp_differential
        
        content_layout.addWidget(temp_group)
        
        # Pressure measurements
        pressure_group = QGroupBox("Pressure Measurements")
        pressure_layout = QFormLayout(pressure_group)
        
        # Suction pressure
        suction_pressure = QDoubleSpinBox()
        suction_pressure.setRange(0, 500)
        suction_pressure.setSuffix(" PSI")
        suction_pressure.setDecimals(1)
        pressure_layout.addRow("Suction Pressure:", suction_pressure)
        self.form_fields['hvac']['suction_pressure'] = suction_pressure
        
        # Discharge pressure
        discharge_pressure = QDoubleSpinBox()
        discharge_pressure.setRange(0, 500)
        discharge_pressure.setSuffix(" PSI")
        discharge_pressure.setDecimals(1)
        pressure_layout.addRow("Discharge Pressure:", discharge_pressure)
        self.form_fields['hvac']['discharge_pressure'] = discharge_pressure
        
        # Static pressure
        static_pressure = QDoubleSpinBox()
        static_pressure.setRange(0, 10)
        static_pressure.setSuffix(" inWC")
        static_pressure.setDecimals(2)
        pressure_layout.addRow("Static Pressure:", static_pressure)
        self.form_fields['hvac']['static_pressure'] = static_pressure
        
        content_layout.addWidget(pressure_group)
        
        # Refrigerant section
        refrigerant_group = QGroupBox("Refrigerant")
        refrigerant_layout = QFormLayout(refrigerant_group)
        
        # Refrigerant type
        refrigerant_type = QComboBox()
        refrigerant_type.addItems(["N/A", "R-22", "R-410A", "R-134a", "R-407C", "R-404A", "Other"])
        refrigerant_layout.addRow("Refrigerant Type:", refrigerant_type)
        self.form_fields['hvac']['refrigerant_type'] = refrigerant_type
        
        # Refrigerant added
        refrigerant_added = QDoubleSpinBox()
        refrigerant_added.setRange(0, 100)
        refrigerant_added.setSuffix(" lbs")
        refrigerant_added.setDecimals(2)
        refrigerant_layout.addRow("Refrigerant Added:", refrigerant_added)
        self.form_fields['hvac']['refrigerant_added'] = refrigerant_added
        
        # Refrigerant recovered
        refrigerant_recovered = QDoubleSpinBox()
        refrigerant_recovered.setRange(0, 100)
        refrigerant_recovered.setSuffix(" lbs")
        refrigerant_recovered.setDecimals(2)
        refrigerant_layout.addRow("Refrigerant Recovered:", refrigerant_recovered)
        self.form_fields['hvac']['refrigerant_recovered'] = refrigerant_recovered
        
        # Superheat
        superheat = QDoubleSpinBox()
        superheat.setRange(0, 100)
        superheat.setSuffix(" °F")
        superheat.setDecimals(1)
        refrigerant_layout.addRow("Superheat:", superheat)
        self.form_fields['hvac']['superheat'] = superheat
        
        # Subcooling
        subcooling = QDoubleSpinBox()
        subcooling.setRange(0, 100)
        subcooling.setSuffix(" °F")
        subcooling.setDecimals(1)
        refrigerant_layout.addRow("Subcooling:", subcooling)
        self.form_fields['hvac']['subcooling'] = subcooling
        
        content_layout.addWidget(refrigerant_group)
        
        # Components section
        components_group = QGroupBox("Component Inspection")
        components_layout = QFormLayout(components_group)
        
        # Create component inspection fields
        component_items = [
            "Filters", "Coils", "Condensate drain", "Blower/fan", 
            "Compressor", "Electrical connections", "Ductwork", "Thermostat"
        ]
        
        for item in component_items:
            condition = QComboBox()
            condition.addItems(["Not Inspected", "Good", "Fair", "Poor", "Replaced"])
            components_layout.addRow(f"{item} Condition:", condition)
            self.form_fields['hvac'][f"{item.lower().replace('/', '_').replace(' ', '_')}_condition"] = condition
        
        content_layout.addWidget(components_group)
        
        # Set the content widget as the scroll area's widget
        scroll.setWidget(content_widget)
        layout.addWidget(scroll)
        
        self.tab_widget.addTab(hvac_widget, "HVAC")
    
    def create_plumbing_tab(self):
        """Create plumbing-specific tab"""
        plumbing_widget = QWidget()
        layout = QVBoxLayout(plumbing_widget)
        
        # Create scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        # Create content widget
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(20, 20, 20, 20)
        content_layout.setSpacing(15)
        
        # Add plumbing fields
        self.form_fields['plumbing'] = {}
        
        # Pressure measurements
        pressure_group = QGroupBox("Pressure Measurements")
        pressure_layout = QFormLayout(pressure_group)
        
        # Water pressure
        water_pressure = QDoubleSpinBox()
        water_pressure.setRange(0, 200)
        water_pressure.setSuffix(" PSI")
        water_pressure.setDecimals(1)
        pressure_layout.addRow("Water Pressure:", water_pressure)
        self.form_fields['plumbing']['water_pressure'] = water_pressure
        
        # Flow rate
        flow_rate = QDoubleSpinBox()
        flow_rate.setRange(0, 100)
        flow_rate.setSuffix(" GPM")
        flow_rate.setDecimals(1)
        pressure_layout.addRow("Flow Rate:", flow_rate)
        self.form_fields['plumbing']['flow_rate'] = flow_rate
        
        content_layout.addWidget(pressure_group)
        
        # Leak testing
        leak_group = QGroupBox("Leak Testing")
        leak_layout = QFormLayout(leak_group)
        
        # Leak test performed
        leak_test_performed = QCheckBox()
        leak_layout.addRow("Leak Test Performed:", leak_test_performed)
        self.form_fields['plumbing']['leak_test_performed'] = leak_test_performed
        
        # Leak test method
        leak_test_method = QComboBox()
        leak_test_method.addItems(["N/A", "Visual", "Pressure Test", "Dye Test", "Ultrasonic", "Other"])
        leak_layout.addRow("Test Method:", leak_test_method)
        self.form_fields['plumbing']['leak_test_method'] = leak_test_method
        
        # Leak test result
        leak_test_result = QComboBox()
        leak_test_result.addItems(["N/A", "No Leaks Found", "Leaks Found and Repaired", "Leaks Found - Requires Further Repair"])
        leak_layout.addRow("Test Result:", leak_test_result)
        self.form_fields['plumbing']['leak_test_result'] = leak_test_result
        
        content_layout.addWidget(leak_group)
        
        # Water quality
        water_group = QGroupBox("Water Quality")
        water_layout = QFormLayout(water_group)
        
        # Water quality tested
        water_quality_tested = QCheckBox()
        water_layout.addRow("Water Quality Tested:", water_quality_tested)
        self.form_fields['plumbing']['water_quality_tested'] = water_quality_tested
        
        # pH level
        ph_level = QDoubleSpinBox()
        ph_level.setRange(0, 14)
        ph_level.setDecimals(1)
        ph_level.setSingleStep(0.1)
        water_layout.addRow("pH Level:", ph_level)
        self.form_fields['plumbing']['ph_level'] = ph_level
        
        # TDS level
        tds_level = QSpinBox()
        tds_level.setRange(0, 2000)
        tds_level.setSuffix(" ppm")
        water_layout.addRow("TDS Level:", tds_level)
        self.form_fields['plumbing']['tds_level'] = tds_level
        
        content_layout.addWidget(water_group)
        
        # Components section
        components_group = QGroupBox("Component Inspection")
        components_layout = QFormLayout(components_group)
        
        # Create component inspection fields
        component_items = [
            "Pipes", "Fittings", "Valves", "Fixtures", 
            "Drains", "Traps", "Water heater", "Pumps"
        ]
        
        for item in component_items:
            condition = QComboBox()
            condition.addItems(["Not Inspected", "Good", "Fair", "Poor", "Replaced"])
            components_layout.addRow(f"{item} Condition:", condition)
            self.form_fields['plumbing'][f"{item.lower().replace(' ', '_')}_condition"] = condition
        
        content_layout.addWidget(components_group)
        
        # Set the content widget as the scroll area's widget
        scroll.setWidget(content_widget)
        layout.addWidget(scroll)
        
        self.tab_widget.addTab(plumbing_widget, "Plumbing")
    
    def create_measurements_tab(self):
        """Create measurements tab"""
        measurements_widget = QWidget()
        layout = QVBoxLayout(measurements_widget)
        
        # Create scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        # Create content widget
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(20, 20, 20, 20)
        content_layout.setSpacing(15)
        
        # Add measurements fields
        self.form_fields['measurements'] = {}
        
        # Vibration measurements
        vibration_group = QGroupBox("Vibration Measurements")
        vibration_layout = QFormLayout(vibration_group)
        
        # Vibration measured
        vibration_measured = QCheckBox()
        vibration_layout.addRow("Vibration Measured:", vibration_measured)
        self.form_fields['measurements']['vibration_measured'] = vibration_measured
        
        # Vibration level
        vibration_level = QDoubleSpinBox()
        vibration_level.setRange(0, 100)
        vibration_level.setSuffix(" mm/s")
        vibration_level.setDecimals(2)
        vibration_layout.addRow("Vibration Level:", vibration_level)
        self.form_fields['measurements']['vibration_level'] = vibration_level
        
        # Vibration location
        vibration_location = QLineEdit()
        vibration_layout.addRow("Measurement Location:", vibration_location)
        self.form_fields['measurements']['vibration_location'] = vibration_location
        
        content_layout.addWidget(vibration_group)
        
        # Temperature measurements
        temp_group = QGroupBox("Temperature Measurements")
        temp_layout = QFormLayout(temp_group)
        
        # Temperature measured
        temp_measured = QCheckBox()
        temp_layout.addRow("Temperature Measured:", temp_measured)
        self.form_fields['measurements']['temp_measured'] = temp_measured
        
        # Temperature readings
        temp_widget = QWidget()
        temp_widget_layout = QGridLayout(temp_widget)
        temp_widget_layout.setContentsMargins(0, 0, 0, 0)
        
        # Add labels
        temp_widget_layout.addWidget(QLabel("Location"), 0, 0)
        temp_widget_layout.addWidget(QLabel("Temperature"), 0, 1)
        
        # Add 3 rows of temperature readings
        for i in range(3):
            location = QLineEdit()
            temperature = QDoubleSpinBox()
            temperature.setRange(0, 1000)
            temperature.setSuffix(" °F")
            temperature.setDecimals(1)
            
            temp_widget_layout.addWidget(location, i+1, 0)
            temp_widget_layout.addWidget(temperature, i+1, 1)
            
            self.form_fields['measurements'][f'temp_location_{i+1}'] = location
            self.form_fields['measurements'][f'temperature_{i+1}'] = temperature
        
        temp_layout.addRow("Temperature Readings:", temp_widget)
        
        content_layout.addWidget(temp_group)
        
        # Noise measurements
        noise_group = QGroupBox("Noise Measurements")
        noise_layout = QFormLayout(noise_group)
        
        # Noise measured
        noise_measured = QCheckBox()
        noise_layout.addRow("Noise Measured:", noise_measured)
        self.form_fields['measurements']['noise_measured'] = noise_measured
        
        # Noise level
        noise_level = QSpinBox()
        noise_level.setRange(0, 150)
        noise_level.setSuffix(" dB")
        noise_layout.addRow("Noise Level:", noise_level)
        self.form_fields['measurements']['noise_level'] = noise_level
        
        # Noise description
        noise_description = QComboBox()
        noise_description.addItems(["N/A", "Normal", "Whining", "Grinding", "Knocking", "Rattling", "Hissing", "Other"])
        noise_layout.addRow("Noise Description:", noise_description)
        self.form_fields['measurements']['noise_description'] = noise_description
        
        content_layout.addWidget(noise_group)
        
        # Other measurements
        other_group = QGroupBox("Other Measurements")
        other_layout = QFormLayout(other_group)
        
        # Add custom measurement fields
        for i in range(3):
            measurement_row = QWidget()
            measurement_layout = QHBoxLayout(measurement_row)
            measurement_layout.setContentsMargins(0, 0, 0, 0)
            
            measurement_name = QLineEdit()
            measurement_name.setPlaceholderText("Measurement name")
            
            measurement_value = QLineEdit()
            measurement_value.setPlaceholderText("Value")
            
            measurement_unit = QLineEdit()
            measurement_unit.setPlaceholderText("Unit")
            measurement_unit.setMaximumWidth(80)
            
            measurement_layout.addWidget(measurement_name)
            measurement_layout.addWidget(measurement_value)
            measurement_layout.addWidget(measurement_unit)
            
            other_layout.addRow(f"Custom {i+1}:", measurement_row)
            
            self.form_fields['measurements'][f'custom_name_{i+1}'] = measurement_name
            self.form_fields['measurements'][f'custom_value_{i+1}'] = measurement_value
            self.form_fields['measurements'][f'custom_unit_{i+1}'] = measurement_unit
        
        content_layout.addWidget(other_group)
        
        # Set the content widget as the scroll area's widget
        scroll.setWidget(content_widget)
        layout.addWidget(scroll)
        
        self.tab_widget.addTab(measurements_widget, "Measurements")
    
    def create_parts_tab(self):
        """Create parts and materials tab"""
        parts_widget = QWidget()
        layout = QVBoxLayout(parts_widget)
        
        # Create scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        # Create content widget
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(20, 20, 20, 20)
        content_layout.setSpacing(15)
        
        # Add parts fields
        self.form_fields['parts'] = {}
        
        # Parts used section
        parts_label = QLabel("Parts and Materials Used")
        parts_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        content_layout.addWidget(parts_label)
        
        # Create a grid for parts entry
        parts_grid = QWidget()
        parts_grid_layout = QGridLayout(parts_grid)
        
        # Add headers
        parts_grid_layout.addWidget(QLabel("Part Number"), 0, 0)
        parts_grid_layout.addWidget(QLabel("Description"), 0, 1)
        parts_grid_layout.addWidget(QLabel("Quantity"), 0, 2)
        parts_grid_layout.addWidget(QLabel("Unit Cost"), 0, 3)
        
        # Add 5 rows for parts entry
        for i in range(5):
            part_number = QLineEdit()
            description = QLineEdit()
            quantity = QSpinBox()
            quantity.setRange(0, 1000)
            
            unit_cost = QDoubleSpinBox()
            unit_cost.setRange(0, 10000)
            unit_cost.setPrefix("$")
            unit_cost.setDecimals(2)
            
            parts_grid_layout.addWidget(part_number, i+1, 0)
            parts_grid_layout.addWidget(description, i+1, 1)
            parts_grid_layout.addWidget(quantity, i+1, 2)
            parts_grid_layout.addWidget(unit_cost, i+1, 3)
            
            self.form_fields['parts'][f'part_number_{i+1}'] = part_number
            self.form_fields['parts'][f'description_{i+1}'] = description
            self.form_fields['parts'][f'quantity_{i+1}'] = quantity
            self.form_fields['parts'][f'unit_cost_{i+1}'] = unit_cost
        
        content_layout.addWidget(parts_grid)
        
        # Additional materials
        materials_label = QLabel("Additional Materials")
        materials_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        content_layout.addWidget(materials_label)
        
        materials_text = QTextEdit()
        materials_text.setPlaceholderText("Enter any additional materials used that are not listed above...")
        content_layout.addWidget(materials_text)
        self.form_fields['parts']['additional_materials'] = materials_text
        
        # Parts requested section
        requested_label = QLabel("Parts Requested for Future Maintenance")
        requested_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        content_layout.addWidget(requested_label)
        
        requested_text = QTextEdit()
        requested_text.setPlaceholderText("Enter any parts that should be ordered for future maintenance...")
        content_layout.addWidget(requested_text)
        self.form_fields['parts']['parts_requested'] = requested_text
        
        # Set the content widget as the scroll area's widget
        scroll.setWidget(content_widget)
        layout.addWidget(scroll)
        
        self.tab_widget.addTab(parts_widget, "Parts & Materials")
    
    def create_attachments_tab(self):
        """Create attachments tab"""
        attachments_widget = QWidget()
        layout = QVBoxLayout(attachments_widget)
        
        # Create scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        # Create content widget
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(20, 20, 20, 20)
        content_layout.setSpacing(15)
        
        # Add attachments fields
        self.form_fields['attachments'] = {}
        
        # Instructions
        instructions = QLabel("Upload photos, diagrams, or other files related to this maintenance task.")
        content_layout.addWidget(instructions)
        
        # Upload button
        upload_btn = QPushButton("Upload File")
        upload_btn.clicked.connect(self.upload_file)
        content_layout.addWidget(upload_btn)
        
        # List of uploaded files
        self.attachments_list = QListWidget()
        content_layout.addWidget(self.attachments_list)
        
        # Set the content widget as the scroll area's widget
        scroll.setWidget(content_widget)
        layout.addWidget(scroll)
        
        self.tab_widget.addTab(attachments_widget, "Attachments")
    
    def create_comments_section(self, layout):
        """Create comments section"""
        comments_label = QLabel("Additional Comments")
        comments_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        layout.addWidget(comments_label)
        
        self.comments_text = QTextEdit()
        self.comments_text.setPlaceholderText("Enter any additional comments, observations, or recommendations...")
        self.comments_text.setMinimumHeight(100)
        layout.addWidget(self.comments_text)
    
    def upload_file(self):
        """Handle file upload"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select File",
            "",
            "All Files (*);;Images (*.png *.jpg *.jpeg);;Documents (*.pdf *.doc *.docx)"
        )
        
        if file_path:
            # Add file to list
            file_name = os.path.basename(file_path)
            item = QListWidgetItem(file_name)
            item.setData(Qt.UserRole, file_path)
            self.attachments_list.addItem(item)
            
            # Add to uploaded files list
            self.uploaded_files.append(file_path)
    
    def submit_report(self):
        """Submit the maintenance report"""
        # Validate form
        if not self.validate_form():
            return
        
        # Collect form data
        report_data = self.collect_form_data()
        
        # Add metadata
        report_data['metadata'] = {
            'work_order_id': self.work_order['work_order_id'],
            'equipment_id': self.equipment['equipment_id'],
            'craftsman_id': self.craftsman_id,
            'report_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'equipment_type': self.get_equipment_type()
        }
        
        # Save report to database
        try:
            # Convert report data to JSON
            report_json = json.dumps(report_data)
            
            # Create report record
            report_id = self.db_manager.create_maintenance_report(
                self.work_order['work_order_id'],
                self.equipment['equipment_id'],
                self.craftsman_id,
                report_json,
                self.comments_text.toPlainText()
            )
            
            if not report_id:
                QMessageBox.critical(self, "Error", "Failed to save maintenance report!")
                return False
            
            # Upload attachments
            for file_path in self.uploaded_files:
                self.db_manager.add_report_attachment(report_id, file_path)
            
            # Update work order status if needed
            if self.work_order['status'] != "Completed":
                self.db_manager.update_work_order_status({
                    'work_order_id': self.work_order['work_order_id'],
                    'status': "Completed",
                    'completed_date': datetime.now().date(),
                    'notes': f"Maintenance report submitted by craftsman ID {self.craftsman_id}"
                })
            
            QMessageBox.information(self, "Success", "Maintenance report submitted successfully!")
            self.accept()
            return True
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to submit report: {str(e)}")
            return False
    
    def validate_form(self):
        """Validate the form data"""
        # Check general information
        if not self.form_fields['general']['maintenance_type'].currentText():
            QMessageBox.warning(self, "Validation Error", "Please select a maintenance type!")
            self.tab_widget.setCurrentIndex(0)  # Switch to general tab
            return False
        
        # Check if at least one inspection item is checked
        inspection_checked = False
        for field_name, field in self.form_fields['inspection'].items():
            if isinstance(field, QCheckBox) and field.isChecked():
                inspection_checked = True
                break
        
        if not inspection_checked:
            reply = QMessageBox.question(
                self,
                "Validation Warning",
                "No inspection items are checked. Continue anyway?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply == QMessageBox.No:
                self.tab_widget.setCurrentIndex(1)  # Switch to inspection tab
                return False
        
        return True
    
    def collect_form_data(self):
        """Collect all form data into a dictionary"""
        data = {}
        
        # Process each tab's data
        for section, fields in self.form_fields.items():
            data[section] = {}
            
            for field_name, field in fields.items():
                # Get value based on field type
                if isinstance(field, QLineEdit):
                    data[section][field_name] = field.text()
                elif isinstance(field, QTextEdit):
                    data[section][field_name] = field.toPlainText()
                elif isinstance(field, QComboBox):
                    data[section][field_name] = field.currentText()
                elif isinstance(field, QCheckBox):
                    data[section][field_name] = field.isChecked()
                elif isinstance(field, QSpinBox) or isinstance(field, QDoubleSpinBox):
                    data[section][field_name] = field.value()
                elif isinstance(field, QDateEdit):
                    data[section][field_name] = field.date().toString("yyyy-MM-dd")
                elif isinstance(field, QTimeEdit):
                    data[section][field_name] = field.time().toString("hh:mm")
        
        return data