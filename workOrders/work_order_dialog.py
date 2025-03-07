from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QLabel, QLineEdit, 
    QTextEdit, QComboBox, QDateEdit, QSpinBox, QPushButton, QScrollArea,
    QWidget, QMessageBox, QTableWidget, QTableWidgetItem, QHeaderView, QCheckBox
)
from PySide6.QtCore import Qt, QDate
import json

class WorkOrderDialog(QDialog):
    """Dialog for creating or editing a work order"""
    def __init__(self, db_manager, work_order=None, parent=None):
        super().__init__(parent)
        self.db_manager = db_manager
        self.work_order = work_order
        self.is_edit_mode = work_order is not None
        self.selected_tools = []  # Store selected tools
        self.selected_spares = []  # Store selected spare parts
        
        self.setWindowTitle("Create Work Order" if not self.is_edit_mode else "Edit Work Order")
        # self.setMinimumWidth(800)  # Increased width to accommodate tables
        # self.setMinimumHeight(800)  # Increased height
        
        self.setup_ui()
        
        if self.is_edit_mode:
            self.load_work_order_data()
    
    def setup_ui(self):
        """Set up the dialog UI"""
        layout = QVBoxLayout(self)
        
        # Create scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        # Create content widget
        content_widget = QWidget()
        self.form_layout = QFormLayout(content_widget)
        
        # Basic information section
        self.form_layout.addRow(QLabel("<b>Basic Information</b>"))
        
        self.title_edit = QLineEdit()
        self.form_layout.addRow("Title:", self.title_edit)
        
        self.description_edit = QTextEdit()
        self.description_edit.setMinimumHeight(100)
        self.form_layout.addRow("Description:", self.description_edit)
        
        # Equipment selection
        self.equipment_combo = QComboBox()
        self.load_equipment_list()
        self.form_layout.addRow("Equipment:", self.equipment_combo)
        
        # Assignment type selection
        self.assignment_type = QComboBox()
        self.assignment_type.addItems(["Individual", "Team"])
        self.assignment_type.currentTextChanged.connect(self.on_assignment_type_changed)
        self.form_layout.addRow("Assignment Type:", self.assignment_type)
        
        # Create assignment container widget
        self.assignment_container = QWidget()
        assignment_layout = QVBoxLayout(self.assignment_container)
        assignment_layout.setContentsMargins(0, 0, 0, 0)
        
        # Individual assignment (Craftsman selection)
        self.craftsman_container = QWidget()
        craftsman_layout = QHBoxLayout(self.craftsman_container)
        craftsman_layout.setContentsMargins(0, 0, 0, 0)
        
        self.craftsman_combo = QComboBox()
        self.load_craftsmen_list()
        craftsman_layout.addWidget(self.craftsman_combo)
        
        # Team assignment
        self.team_container = QWidget()
        team_layout = QHBoxLayout(self.team_container)
        team_layout.setContentsMargins(0, 0, 0, 0)
        
        self.team_combo = QComboBox()
        self.load_teams_list()
        team_layout.addWidget(self.team_combo)
        
        # Add both containers to assignment container
        assignment_layout.addWidget(self.craftsman_container)
        assignment_layout.addWidget(self.team_container)
        
        self.form_layout.addRow("Assigned To:", self.assignment_container)
        
        # Initially hide team selection
        self.team_container.hide()
        
        # Priority selection
        self.priority_combo = QComboBox()
        self.priority_combo.addItems(["Low", "Medium", "High", "Critical"])
        self.priority_combo.setCurrentText("Medium")  # Default
        self.form_layout.addRow("Priority:", self.priority_combo)
        
        # Status selection
        self.status_combo = QComboBox()
        self.status_combo.addItems(["Open", "In Progress", "On Hold", "Completed", "Cancelled"])
        self.form_layout.addRow("Status:", self.status_combo)
        
        # Dates section
        self.form_layout.addRow(QLabel("<b>Dates</b>"))
        
        self.due_date_edit = QDateEdit()
        self.due_date_edit.setCalendarPopup(True)
        self.due_date_edit.setDate(QDate.currentDate().addDays(7))  # Default to 1 week from now
        self.form_layout.addRow("Due Date:", self.due_date_edit)
        
        self.completed_date_edit = QDateEdit()
        self.completed_date_edit.setCalendarPopup(True)
        self.completed_date_edit.setDate(QDate.currentDate())
        self.completed_date_edit.setEnabled(False)  # Disabled by default
        self.form_layout.addRow("Completion Date:", self.completed_date_edit)
        
        # Connect status change to enable/disable completion date
        self.status_combo.currentTextChanged.connect(self.on_status_changed)
        
        # Time and cost section
        self.form_layout.addRow(QLabel("<b>Time and Cost</b>"))
        
        self.estimated_hours_spin = QSpinBox()
        self.estimated_hours_spin.setRange(0, 1000)
        self.estimated_hours_spin.setSuffix(" hours")
        self.form_layout.addRow("Estimated Hours:", self.estimated_hours_spin)
        
        self.actual_hours_spin = QSpinBox()
        self.actual_hours_spin.setRange(0, 1000)
        self.actual_hours_spin.setSuffix(" hours")
        self.form_layout.addRow("Actual Hours:", self.actual_hours_spin)
        
        # Replace the old parts section with new Tools and Spare Parts sections
        self.form_layout.addRow(QLabel("<b>Tools Required</b>"))
        
        # Tools table
        self.tools_table = QTableWidget()
        self.tools_table.setColumnCount(5)
        self.tools_table.setHorizontalHeaderLabels([
            "Tool ID", "Name", "Available Quantity", "Required Quantity", "Location"
        ])
        self.tools_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        self.tools_table.setMinimumHeight(150)
        self.form_layout.addRow(self.tools_table)
        
        # Tool selection controls
        tool_controls = QHBoxLayout()
        self.tool_combo = QComboBox()
        self.tool_combo.setMinimumWidth(300)
        self.tool_quantity_spin = QSpinBox()
        self.tool_quantity_spin.setMinimum(1)
        add_tool_btn = QPushButton("Add Tool")
        add_tool_btn.clicked.connect(self.add_tool)
        remove_tool_btn = QPushButton("Remove Selected")
        remove_tool_btn.clicked.connect(lambda: self.remove_selected(self.tools_table))
        
        tool_controls.addWidget(QLabel("Select Tool:"))
        tool_controls.addWidget(self.tool_combo)
        tool_controls.addWidget(QLabel("Quantity:"))
        tool_controls.addWidget(self.tool_quantity_spin)
        tool_controls.addWidget(add_tool_btn)
        tool_controls.addWidget(remove_tool_btn)
        self.form_layout.addRow(tool_controls)

        # Spare Parts section
        self.form_layout.addRow(QLabel("<b>Spare Parts Required</b>"))
        
        # Spare parts table
        self.spares_table = QTableWidget()
        self.spares_table.setColumnCount(5)
        self.spares_table.setHorizontalHeaderLabels([
            "Part ID", "Name", "Available Quantity", "Required Quantity", "Location"
        ])
        self.spares_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        self.spares_table.setMinimumHeight(150)
        self.form_layout.addRow(self.spares_table)
        
        # Spare part selection controls
        spare_controls = QHBoxLayout()
        self.spare_combo = QComboBox()
        self.spare_combo.setMinimumWidth(300)
        self.spare_quantity_spin = QSpinBox()
        self.spare_quantity_spin.setMinimum(1)
        add_spare_btn = QPushButton("Add Spare Part")
        add_spare_btn.clicked.connect(self.add_spare)
        remove_spare_btn = QPushButton("Remove Selected")
        remove_spare_btn.clicked.connect(lambda: self.remove_selected(self.spares_table))
        
        spare_controls.addWidget(QLabel("Select Spare Part:"))
        spare_controls.addWidget(self.spare_combo)
        spare_controls.addWidget(QLabel("Quantity:"))
        spare_controls.addWidget(self.spare_quantity_spin)
        spare_controls.addWidget(add_spare_btn)
        spare_controls.addWidget(remove_spare_btn)
        self.form_layout.addRow(spare_controls)
        
        # Notes section
        self.form_layout.addRow(QLabel("<b>Additional Notes</b>"))
        
        self.notes_edit = QTextEdit()
        self.notes_edit.setMinimumHeight(80)
        self.form_layout.addRow("Notes:", self.notes_edit)
        
        # Add scheduling section
        self.form_layout.addRow(QLabel("<b>Scheduling</b>"))
        
        # Create scheduling container
        scheduling_container = QWidget()
        scheduling_layout = QVBoxLayout(scheduling_container)
        scheduling_layout.setContentsMargins(0, 0, 0, 0)
        
        # Checkbox to enable scheduling
        self.enable_scheduling = QCheckBox("Create recurring work order")
        scheduling_layout.addWidget(self.enable_scheduling)
        
        # Scheduling details container
        self.scheduling_details = QWidget()
        scheduling_details_layout = QFormLayout(self.scheduling_details)
        scheduling_details_layout.setContentsMargins(0, 0, 0, 0)
        
        # Frequency settings
        self.frequency = QSpinBox()
        self.frequency.setRange(1, 365)
        self.frequency.setValue(1)
        
        self.frequency_unit = QComboBox()
        self.frequency_unit.addItems(["days", "weeks", "months"])
        self.frequency_unit.setCurrentText("weeks")
        
        # End date (optional)
        self.end_date = QDateEdit()
        self.end_date.setCalendarPopup(True)
        self.end_date.setDate(QDate.currentDate().addYears(1))
        
        # Notification settings
        self.notification_days = QSpinBox()
        self.notification_days.setRange(1, 30)
        self.notification_days.setValue(2)
        
        self.notification_emails = QLineEdit()
        self.notification_emails.setPlaceholderText("Comma-separated email addresses")
        
        # Add fields to layout
        scheduling_details_layout.addRow("Repeat every:", self.frequency)
        scheduling_details_layout.addRow("Frequency unit:", self.frequency_unit)
        scheduling_details_layout.addRow("End date:", self.end_date)
        scheduling_details_layout.addRow("Notify days before:", self.notification_days)
        scheduling_details_layout.addRow("Notification emails:", self.notification_emails)
        
        # Add scheduling details to container
        scheduling_layout.addWidget(self.scheduling_details)
        
        # Initially hide scheduling details
        self.scheduling_details.setVisible(False)
        
        # Connect checkbox to show/hide scheduling details and update emails
        self.enable_scheduling.toggled.connect(self.on_scheduling_toggled)
        
        # Add scheduling container to form
        self.form_layout.addRow("", scheduling_container)
        
        # Add content widget to scroll area
        scroll.setWidget(content_widget)
        layout.addWidget(scroll)
        
        # Buttons
        buttons_layout = QHBoxLayout()
        
        self.save_btn = QPushButton("Save Work Order")
        self.save_btn.clicked.connect(self.save_work_order)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        
        buttons_layout.addWidget(self.save_btn)
        buttons_layout.addWidget(cancel_btn)
        layout.addLayout(buttons_layout)
        
        # After setting up the UI, load available tools and spares
        self.load_available_tools()
        self.load_available_spares()
    
    def load_equipment_list(self):
        """Load equipment list into combo box"""
        equipment_list = self.db_manager.get_all_equipment()
        
        for equipment in equipment_list:
            self.equipment_combo.addItem(
                f"{equipment['equipment_name']} ({equipment['equipment_id']})",
                equipment['equipment_id']
            )
    
    def load_craftsmen_list(self):
        """Load craftsmen list into combo box"""
        craftsmen_list = self.db_manager.get_all_craftsmen()
        
        for craftsman in craftsmen_list:
            self.craftsman_combo.addItem(
                f"{craftsman['first_name']} {craftsman['last_name']}",
                craftsman['craftsman_id']
            )
    
    def load_teams_list(self):
        """Load teams list into combo box"""
        teams = self.db_manager.get_all_teams()
        self.team_combo.clear()
        
        for team in teams:
            self.team_combo.addItem(team['team_name'], team['team_id'])

    def on_assignment_type_changed(self, assignment_type):
        """Handle assignment type change"""
        # Safely disconnect any existing connections
        try:
            self.craftsman_combo.currentIndexChanged.disconnect()
        except TypeError:
            # Signal was not connected
            pass
        try:
            self.team_combo.currentIndexChanged.disconnect()
        except TypeError:
            # Signal was not connected
            pass
        
        if assignment_type == "Individual":
            self.craftsman_container.show()
            self.team_container.hide()
            
            # Connect craftsman signal
            self.craftsman_combo.currentIndexChanged.connect(self.update_notification_emails)
            
            # Update emails immediately if scheduling is enabled
            if self.enable_scheduling.isChecked():
                self.update_notification_emails()
        else:
            self.craftsman_container.hide()
            self.team_container.show()
            
            # Connect team signal
            self.team_combo.currentIndexChanged.connect(self.update_notification_emails)
            
            # Update emails immediately if scheduling is enabled
            if self.enable_scheduling.isChecked():
                self.update_notification_emails()

    def update_notification_emails(self):
        """Update notification emails based on assigned craftsman or team"""
        if not self.enable_scheduling.isChecked():
            return
        
        emails = []
        
        if self.assignment_type.currentText() == "Individual":
            # Get craftsman email
            craftsman_id = self.craftsman_combo.currentData()
            if craftsman_id:
                craftsman = self.db_manager.get_craftsman_by_id(craftsman_id)
                if craftsman and craftsman.get('email'):
                    emails.append(craftsman['email'])
        else:
            # Get team members' emails
            team_id = self.team_combo.currentData()
            if team_id:
                team_members = self.db_manager.get_team_members(team_id)
                for member in team_members:
                    if member.get('email'):
                        emails.append(member['email'])
        
        # Update the notification emails field
        if emails:
            self.notification_emails.setText(", ".join(emails))

    def on_status_changed(self, status):
        """Handle status change"""
        # Enable completion date only if status is Completed
        self.completed_date_edit.setEnabled(status == "Completed")
        
        # If changing to Completed, set completion date to today
        if status == "Completed" and not self.is_edit_mode:
            self.completed_date_edit.setDate(QDate.currentDate())
    
    def load_available_tools(self):
        """Load available tools into the combo box"""
        tools = self.db_manager.get_inventory_items_by_category('Tool')
        self.tool_combo.clear()
        for tool in tools:
            if tool['quantity'] > 0:  # Only show available tools
                self.tool_combo.addItem(
                    f"{tool['name']} (Available: {tool['quantity']})",
                    tool
                )
        self.update_tool_quantity_limit()
        self.tool_combo.currentIndexChanged.connect(self.update_tool_quantity_limit)

    def load_available_spares(self):
        """Load available spare parts into the combo box"""
        spares = self.db_manager.get_inventory_items()
        self.spare_combo.clear()
        for spare in spares:
            if spare['category'] != 'Tool' and spare['quantity'] > 0:  # Only show available non-tool items
                self.spare_combo.addItem(
                    f"{spare['name']} (Available: {spare['quantity']})",
                    spare
                )
        self.update_spare_quantity_limit()
        self.spare_combo.currentIndexChanged.connect(self.update_spare_quantity_limit)

    def update_tool_quantity_limit(self):
        """Update the tool quantity spinner maximum based on selected tool"""
        if self.tool_combo.currentData():
            available = self.tool_combo.currentData()['quantity']
            self.tool_quantity_spin.setMaximum(available)
            self.tool_quantity_spin.setValue(min(1, available))

    def update_spare_quantity_limit(self):
        """Update the spare quantity spinner maximum based on selected spare part"""
        if self.spare_combo.currentData():
            available = self.spare_combo.currentData()['quantity']
            self.spare_quantity_spin.setMaximum(available)
            self.spare_quantity_spin.setValue(min(1, available))

    def add_tool(self):
        """Add selected tool to the tools table"""
        tool_data = self.tool_combo.currentData()
        if not tool_data:
            return

        quantity = self.tool_quantity_spin.value()
        
        # Check if tool is already in table
        for row in range(self.tools_table.rowCount()):
            if self.tools_table.item(row, 0).text() == str(tool_data['item_id']):
                QMessageBox.warning(self, "Warning", "This tool is already added!")
                return

        # Add new row
        row = self.tools_table.rowCount()
        self.tools_table.insertRow(row)
        
        self.tools_table.setItem(row, 0, QTableWidgetItem(str(tool_data['item_id'])))
        self.tools_table.setItem(row, 1, QTableWidgetItem(tool_data['name']))
        self.tools_table.setItem(row, 2, QTableWidgetItem(str(tool_data['quantity'])))
        self.tools_table.setItem(row, 3, QTableWidgetItem(str(quantity)))
        self.tools_table.setItem(row, 4, QTableWidgetItem(tool_data.get('location', '')))
        
        # Add to selected tools list
        self.selected_tools.append({
            'item_id': tool_data['item_id'],
            'quantity': quantity
        })

    def add_spare(self):
        """Add selected spare part to the spares table"""
        spare_data = self.spare_combo.currentData()
        if not spare_data:
            return

        quantity = self.spare_quantity_spin.value()
        
        # Check if spare is already in table
        for row in range(self.spares_table.rowCount()):
            if self.spares_table.item(row, 0).text() == str(spare_data['item_id']):
                QMessageBox.warning(self, "Warning", "This spare part is already added!")
                return

        # Add new row
        row = self.spares_table.rowCount()
        self.spares_table.insertRow(row)
        
        self.spares_table.setItem(row, 0, QTableWidgetItem(str(spare_data['item_id'])))
        self.spares_table.setItem(row, 1, QTableWidgetItem(spare_data['name']))
        self.spares_table.setItem(row, 2, QTableWidgetItem(str(spare_data['quantity'])))
        self.spares_table.setItem(row, 3, QTableWidgetItem(str(quantity)))
        self.spares_table.setItem(row, 4, QTableWidgetItem(spare_data.get('location', '')))
        
        # Add to selected spares list
        self.selected_spares.append({
            'item_id': spare_data['item_id'],
            'quantity': quantity
        })

    def remove_selected(self, table):
        """Remove selected row from the specified table"""
        selected_rows = set(item.row() for item in table.selectedItems())
        
        # Remove rows in reverse order to avoid index shifting
        for row in sorted(selected_rows, reverse=True):
            item_id = int(table.item(row, 0).text())
            
            # Remove from selected lists
            if table == self.tools_table:
                self.selected_tools = [t for t in self.selected_tools if t['item_id'] != item_id]
            else:
                self.selected_spares = [s for s in self.selected_spares if s['item_id'] != item_id]
            
            table.removeRow(row)

    def save_work_order(self):
        """Save work order data"""
        # Validate required fields
        if not self.title_edit.text().strip():
            QMessageBox.warning(self, "Validation Error", "Title is required!")
            return
        
        # Prepare data
        work_order_data = {
            'title': self.title_edit.text().strip(),
            'description': self.description_edit.toPlainText().strip(),
            'equipment_id': self.equipment_combo.currentData(),
            'assignment_type': self.assignment_type.currentText(),
            'craftsman_id': None,
            'team_id': None,
            'priority': self.priority_combo.currentText(),
            'status': self.status_combo.currentText(),
            'due_date': self.due_date_edit.date().toPython(),
            'estimated_hours': self.estimated_hours_spin.value(),
            'actual_hours': self.actual_hours_spin.value(),
            'tools_required': self.selected_tools,
            'spares_required': self.selected_spares,
            'notes': self.notes_edit.toPlainText().strip()
        }
        
        # Set craftsman_id or team_id based on assignment type
        if work_order_data['assignment_type'] == "Individual":
            work_order_data['craftsman_id'] = self.craftsman_combo.currentData()
        else:
            work_order_data['team_id'] = self.team_combo.currentData()
        
        # Add completed date if status is Completed
        if self.status_combo.currentText() == "Completed":
            work_order_data['completed_date'] = self.completed_date_edit.date().toPython()
        else:
            work_order_data['completed_date'] = None
        
        # Check if this is a recurring work order
        if self.enable_scheduling.isChecked():
            # Prepare schedule data
            schedule_data = {
                'frequency': self.frequency.value(),
                'frequency_unit': self.frequency_unit.currentText(),
                'start_date': self.due_date_edit.date().toPython(),
                'end_date': self.end_date.date().toPython(),
                'notification_days_before': self.notification_days.value(),
                'notification_emails': [
                    email.strip() 
                    for email in self.notification_emails.text().split(',')
                    if email.strip()
                ]
            }
            
            # If editing an existing work order with a schedule
            if self.is_edit_mode and self.work_order.get('schedule_id'):
                work_order_data['schedule_id'] = self.work_order['schedule_id']
                success = self.update_recurring_work_order(work_order_data, schedule_data)
                message = "Recurring work order updated successfully!"
            else:
                # Save new recurring work order
                success = self.db_manager.create_recurring_work_order(work_order_data, schedule_data)
                message = "Recurring work order created successfully!"
        else:
            # Save regular work order
            if self.is_edit_mode:
                work_order_data['work_order_id'] = self.work_order['work_order_id']
                success = self.db_manager.update_work_order(work_order_data)
                message = "Work order updated successfully!"
            else:
                success = self.db_manager.create_work_order(work_order_data)
                message = "Work order created successfully!"
        
        if success:
            QMessageBox.information(self, "Success", message)
            self.accept()
        else:
            QMessageBox.critical(self, "Error", "Failed to save work order!")

    def update_recurring_work_order(self, work_order_data, schedule_data):
        """Update an existing recurring work order"""
        try:
            connection = self.db_manager.connect()
            cursor = connection.cursor()
            
            # Update the schedule
            cursor.execute("""
                UPDATE maintenance_schedules
                SET frequency = %s,
                    frequency_unit = %s,
                    end_date = %s,
                    notification_days_before = %s,
                    notification_emails = %s
                WHERE schedule_id = %s
            """, (
                schedule_data['frequency'],
                schedule_data['frequency_unit'],
                schedule_data['end_date'],
                schedule_data['notification_days_before'],
                json.dumps(schedule_data['notification_emails']),
                work_order_data['schedule_id']
            ))
            
            # Get the current work order ID
            cursor.execute("""
                SELECT work_order_id 
                FROM work_orders 
                WHERE schedule_id = %s 
                ORDER BY created_date DESC 
                LIMIT 1
            """, (work_order_data['schedule_id'],))
            
            result = cursor.fetchone()
            if not result:
                raise Exception("Could not find associated work order")
            
            current_work_order_id = result[0]
            
            # Update the work order
            cursor.execute("""
                UPDATE work_orders
                SET title = %s,
                    description = %s,
                    equipment_id = %s,
                    assignment_type = %s,
                    craftsman_id = %s,
                    team_id = %s,
                    priority = %s,
                    status = %s,
                    due_date = %s,
                    completed_date = %s,
                    estimated_hours = %s,
                    actual_hours = %s,
                    tools_required = %s,
                    spares_required = %s,
                    notes = %s
                WHERE work_order_id = %s
            """, (
                work_order_data['title'],
                work_order_data['description'],
                work_order_data['equipment_id'],
                work_order_data['assignment_type'],
                work_order_data['craftsman_id'],
                work_order_data['team_id'],
                work_order_data['priority'],
                work_order_data['status'],
                work_order_data['due_date'],
                work_order_data['completed_date'],
                work_order_data['estimated_hours'],
                work_order_data['actual_hours'],
                json.dumps(work_order_data['tools_required']),
                json.dumps(work_order_data['spares_required']),
                work_order_data['notes'],
                current_work_order_id
            ))
            
            # Update the work order template
            cursor.execute("""
                UPDATE work_order_templates
                SET title = %s,
                    description = %s,
                    equipment_id = %s,
                    assignment_type = %s,
                    craftsman_id = %s,
                    team_id = %s,
                    priority = %s,
                    estimated_hours = %s,
                    tools_required = %s,
                    spares_required = %s
                WHERE schedule_id = %s
            """, (
                work_order_data['title'],
                work_order_data['description'],
                work_order_data['equipment_id'],
                work_order_data['assignment_type'],
                work_order_data['craftsman_id'],
                work_order_data['team_id'],
                work_order_data['priority'],
                work_order_data['estimated_hours'],
                json.dumps(work_order_data['tools_required']),
                json.dumps(work_order_data['spares_required']),
                work_order_data['schedule_id']
            ))
            
            connection.commit()
            return True
        except Exception as e:
            print(f"Error updating recurring work order: {e}")
            if connection:
                connection.rollback()
            return False
        finally:
            if connection:
                self.db_manager.close(connection)

    def load_work_order_data(self):
        """Load work order data into form fields"""
        if not self.work_order:
            return
        
        # Set basic information
        self.title_edit.setText(self.work_order['title'])
        self.description_edit.setText(self.work_order['description'])
        
        # Set equipment
        equipment_index = self.equipment_combo.findData(self.work_order['equipment_id'])
        if equipment_index >= 0:
            self.equipment_combo.setCurrentIndex(equipment_index)
        
        # Set assignment type and assignee
        if self.work_order.get('team_id'):
            self.assignment_type.setCurrentText("Team")
            team_index = self.team_combo.findData(self.work_order['team_id'])
            if team_index >= 0:
                self.team_combo.setCurrentIndex(team_index)
        else:
            self.assignment_type.setCurrentText("Individual")
            craftsman_index = self.craftsman_combo.findData(self.work_order['craftsman_id'])
            if craftsman_index >= 0:
                self.craftsman_combo.setCurrentIndex(craftsman_index)
        
        # Set priority and status
        self.priority_combo.setCurrentText(self.work_order['priority'])
        self.status_combo.setCurrentText(self.work_order['status'])
        
        # Set dates
        if self.work_order['due_date']:
            self.due_date_edit.setDate(QDate.fromString(str(self.work_order['due_date']), "yyyy-MM-dd"))
        
        if self.work_order['completed_date']:
            self.completed_date_edit.setDate(QDate.fromString(str(self.work_order['completed_date']), "yyyy-MM-dd"))
            self.completed_date_edit.setEnabled(True)
        
        # Set time and cost
        self.estimated_hours_spin.setValue(self.work_order['estimated_hours'] or 0)
        self.actual_hours_spin.setValue(self.work_order['actual_hours'] or 0)
        
        # Load tools and spares if they exist
        if 'tools_required' in self.work_order and self.work_order['tools_required']:
            try:
                tools = json.loads(self.work_order['tools_required']) if isinstance(self.work_order['tools_required'], str) else self.work_order['tools_required']
                for tool in tools:
                    tool_data = self.db_manager.get_inventory_item(tool['item_id'])
                    if tool_data:
                        self.tool_combo.setCurrentText(f"{tool_data['name']} (Available: {tool_data['quantity']})")
                        self.tool_quantity_spin.setValue(tool['quantity'])
                        self.add_tool()
            except json.JSONDecodeError:
                print("Error decoding tools JSON data")
        
        if 'spares_required' in self.work_order and self.work_order['spares_required']:
            try:
                spares = json.loads(self.work_order['spares_required']) if isinstance(self.work_order['spares_required'], str) else self.work_order['spares_required']
                for spare in spares:
                    spare_data = self.db_manager.get_inventory_item(spare['item_id'])
                    if spare_data:
                        self.spare_combo.setCurrentText(f"{spare_data['name']} (Available: {spare_data['quantity']})")
                        self.spare_quantity_spin.setValue(spare['quantity'])
                        self.add_spare()
            except json.JSONDecodeError:
                print("Error decoding spares JSON data")
        
        # Set notes
        self.notes_edit.setText(self.work_order['notes'] or "")
        
        # Load scheduling information if this is a scheduled work order
        if self.work_order.get('schedule_id'):
            # Enable scheduling checkbox
            self.enable_scheduling.setChecked(True)
            self.scheduling_details.setVisible(True)
            
            # Get schedule details from database
            schedule = self.get_schedule_details(self.work_order['schedule_id'])
            if schedule:
                # Set frequency
                self.frequency.setValue(schedule['frequency'])
                self.frequency_unit.setCurrentText(schedule['frequency_unit'])
                
                # Set end date
                if schedule['end_date']:
                    self.end_date.setDate(QDate.fromString(str(schedule['end_date']), "yyyy-MM-dd"))
                
                # Set notification settings
                self.notification_days.setValue(schedule['notification_days_before'])
                
                # Set notification emails
                if schedule['notification_emails']:
                    try:
                        emails = json.loads(schedule['notification_emails'])
                        if isinstance(emails, list):
                            self.notification_emails.setText(", ".join(emails))
                    except json.JSONDecodeError:
                        print("Error decoding notification emails JSON")

    def get_schedule_details(self, schedule_id):
        """Get schedule details from database"""
        try:
            connection = self.db_manager.connect()
            cursor = connection.cursor(dictionary=True)
            
            cursor.execute("""
                SELECT * FROM maintenance_schedules
                WHERE schedule_id = %s
            """, (schedule_id,))
            
            schedule = cursor.fetchone()
            self.db_manager.close(connection)
            return schedule
        except Exception as e:
            print(f"Error getting schedule details: {e}")
            return None

    def on_scheduling_toggled(self, checked):
        """Handle scheduling checkbox toggle"""
        self.scheduling_details.setVisible(checked)
        if checked:
            # When scheduling is enabled, populate notification emails
            self.update_notification_emails()
