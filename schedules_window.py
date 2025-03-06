from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, 
                              QTableWidget, QTableWidgetItem, QPushButton, QLabel, 
                              QComboBox, QSpinBox, QDateEdit, QDialog, QFormLayout,
                              QLineEdit, QTextEdit, QMessageBox, QHeaderView)
from PySide6.QtCore import Qt, QDate
import json
from datetime import datetime, timedelta
from PySide6.QtGui import QColor

class AddScheduleDialog(QDialog):
    def __init__(self, db_manager, parent=None, schedule_id=None):
        super().__init__(parent)
        self.db_manager = db_manager
        self.schedule_id = schedule_id
        self.is_edit_mode = schedule_id is not None
        self.setWindowTitle("Add New Schedule" if not self.is_edit_mode else "Edit Schedule")
        self.setup_ui()
        
        if self.is_edit_mode:
            self.load_schedule_data()

    def setup_ui(self):
        layout = QFormLayout(self)

        # Work Order Details
        self.title = QLineEdit()
        self.description = QTextEdit()
        self.priority = QComboBox()
        self.priority.addItems(["Low", "Medium", "High", "Critical"])
        
        # Equipment Selection
        self.equipment = QComboBox()
        equipment_list = self.db_manager.get_all_equipment()
        for equip in equipment_list:
            self.equipment.addItem(equip['equipment_name'], equip['equipment_id'])

        # Assignment
        self.assignment_type = QComboBox()
        self.assignment_type.addItems(["Individual", "Team"])
        
        self.assignee = QComboBox()
        self.update_assignee_list()
        
        self.assignment_type.currentTextChanged.connect(self.update_assignee_list)

        # Schedule Details
        self.frequency = QSpinBox()
        self.frequency.setRange(1, 365)
        
        self.frequency_unit = QComboBox()
        self.frequency_unit.addItems(["days", "weeks", "months"])
        
        self.start_date = QDateEdit()
        self.start_date.setDate(QDate.currentDate())
        
        self.end_date = QDateEdit()
        self.end_date.setDate(QDate.currentDate().addYears(1))
        
        self.notification_days = QSpinBox()
        self.notification_days.setRange(1, 30)
        self.notification_days.setValue(2)
        
        self.notification_emails = QLineEdit()
        self.notification_emails.setPlaceholderText("Comma-separated email addresses")

        # Add fields to layout
        layout.addRow("Title:", self.title)
        layout.addRow("Description:", self.description)
        layout.addRow("Priority:", self.priority)
        layout.addRow("Equipment:", self.equipment)
        layout.addRow("Assignment Type:", self.assignment_type)
        layout.addRow("Assign To:", self.assignee)
        layout.addRow("Frequency:", self.frequency)
        layout.addRow("Frequency Unit:", self.frequency_unit)
        layout.addRow("Start Date:", self.start_date)
        layout.addRow("End Date:", self.end_date)
        layout.addRow("Notify Days Before:", self.notification_days)
        layout.addRow("Notification Emails:", self.notification_emails)

        # Buttons
        button_layout = QHBoxLayout()
        save_button = QPushButton("Save")
        cancel_button = QPushButton("Cancel")
        
        save_button.clicked.connect(self.save_schedule)
        cancel_button.clicked.connect(self.reject)
        
        button_layout.addWidget(save_button)
        button_layout.addWidget(cancel_button)
        layout.addRow("", button_layout)

    def update_assignee_list(self):
        self.assignee.clear()
        if self.assignment_type.currentText() == "Individual":
            craftsmen = self.db_manager.get_all_craftsmen()
            for craftsman in craftsmen:
                self.assignee.addItem(
                    f"{craftsman['first_name']} {craftsman['last_name']}", 
                    craftsman['craftsman_id']
                )
        else:
            teams = self.db_manager.get_all_teams()
            for team in teams:
                self.assignee.addItem(team['team_name'], team['team_id'])

    def save_schedule(self):
        try:
            # Prepare schedule data
            schedule_data = {
                'frequency': self.frequency.value(),
                'frequency_unit': self.frequency_unit.currentText(),
                'start_date': self.start_date.date().toPython(),
                'end_date': self.end_date.date().toPython(),
                'notification_days_before': self.notification_days.value(),
                'notification_emails': [
                    email.strip() 
                    for email in self.notification_emails.text().split(',')
                    if email.strip()
                ]
            }

            # Prepare work order data
            work_order_data = {
                'title': self.title.text(),
                'description': self.description.toPlainText(),
                'equipment_id': self.equipment.currentData(),
                'priority': self.priority.currentText(),
                'assignment_type': self.assignment_type.currentText()
            }

            # Set assignee based on type
            if self.assignment_type.currentText() == "Individual":
                work_order_data['craftsman_id'] = self.assignee.currentData()
                work_order_data['team_id'] = None
            else:
                work_order_data['team_id'] = self.assignee.currentData()
                work_order_data['craftsman_id'] = None

            # Create or update recurring work order
            if self.is_edit_mode:
                # Update existing schedule
                connection = self.db_manager.connect()
                cursor = connection.cursor()
                
                # Update maintenance schedule
                cursor.execute("""
                    UPDATE maintenance_schedules
                    SET frequency = %s,
                        frequency_unit = %s,
                        start_date = %s,
                        end_date = %s,
                        notification_days_before = %s,
                        notification_emails = %s
                    WHERE schedule_id = %s
                """, (
                    schedule_data['frequency'],
                    schedule_data['frequency_unit'],
                    schedule_data['start_date'],
                    schedule_data['end_date'],
                    schedule_data['notification_days_before'],
                    json.dumps(schedule_data['notification_emails']),
                    self.schedule_id
                ))
                
                # Update work order template
                cursor.execute("""
                    UPDATE work_order_templates
                    SET title = %s,
                        description = %s,
                        equipment_id = %s,
                        priority = %s,
                        assignment_type = %s,
                        craftsman_id = %s,
                        team_id = %s
                    WHERE schedule_id = %s
                """, (
                    work_order_data['title'],
                    work_order_data['description'],
                    work_order_data['equipment_id'],
                    work_order_data['priority'],
                    work_order_data['assignment_type'],
                    work_order_data['craftsman_id'],
                    work_order_data['team_id'],
                    self.schedule_id
                ))
                
                connection.commit()
                self.db_manager.close(connection)
                QMessageBox.information(self, "Success", "Schedule updated successfully!")
                self.accept()
            else:
                # Create new schedule
                if self.db_manager.create_recurring_work_order(work_order_data, schedule_data):
                    QMessageBox.information(self, "Success", "Schedule created successfully!")
                    self.accept()
                else:
                    QMessageBox.warning(self, "Error", "Failed to create schedule")
        
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred: {str(e)}")

    def load_schedule_data(self):
        """Load schedule data for editing"""
        try:
            connection = self.db_manager.connect()
            cursor = connection.cursor(dictionary=True)
            
            # Get schedule details
            cursor.execute("""
                SELECT ms.*, wot.* 
                FROM maintenance_schedules ms
                JOIN work_order_templates wot ON ms.schedule_id = wot.schedule_id
                WHERE ms.schedule_id = %s
            """, (self.schedule_id,))
            
            schedule_data = cursor.fetchone()
            
            if not schedule_data:
                QMessageBox.warning(self, "Warning", "Schedule not found!")
                return
            
            # Populate the dialog with existing data
            self.title.setText(schedule_data['title'])
            self.description.setText(schedule_data['description'])
            
            # Set priority
            index = self.priority.findText(schedule_data['priority'])
            if index >= 0:
                self.priority.setCurrentIndex(index)
            
            # Set equipment
            equipment_index = self.equipment.findData(schedule_data['equipment_id'])
            if equipment_index >= 0:
                self.equipment.setCurrentIndex(equipment_index)
            
            # Set assignment type and assignee
            if schedule_data['assignment_type'] == 'Team':
                self.assignment_type.setCurrentText('Team')
                team_index = self.assignee.findData(schedule_data['team_id'])
                if team_index >= 0:
                    self.assignee.setCurrentIndex(team_index)
            else:
                self.assignment_type.setCurrentText('Individual')
                craftsman_index = self.assignee.findData(schedule_data['craftsman_id'])
                if craftsman_index >= 0:
                    self.assignee.setCurrentIndex(craftsman_index)
            
            # Set schedule details
            self.frequency.setValue(schedule_data['frequency'])
            self.frequency_unit.setCurrentText(schedule_data['frequency_unit'])
            
            # Set dates
            start_date = QDate.fromString(str(schedule_data['start_date']), "yyyy-MM-dd")
            self.start_date.setDate(start_date)
            
            if schedule_data['end_date']:
                end_date = QDate.fromString(str(schedule_data['end_date']), "yyyy-MM-dd")
                self.end_date.setDate(end_date)
            
            # Set notification settings
            self.notification_days.setValue(schedule_data['notification_days_before'])
            
            if schedule_data['notification_emails']:
                emails = json.loads(schedule_data['notification_emails'])
                self.notification_emails.setText(", ".join(emails))
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load schedule data: {str(e)}")
        finally:
            self.db_manager.close(connection)

class SchedulesWindow(QWidget):
    def __init__(self, db_manager, parent=None):
        super().__init__(parent)
        self.db_manager = db_manager
        self.setup_ui()
        self.load_schedules()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        # Header
        header_layout = QHBoxLayout()
        title_label = QLabel("Maintenance Schedules")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        
        # Add Schedule Button
        add_button = QPushButton("Add New Schedule")
        add_button.clicked.connect(self.show_add_dialog)
        header_layout.addWidget(add_button)
        
        layout.addLayout(header_layout)

        # Filter Section
        filter_layout = QHBoxLayout()
        
        self.status_filter = QComboBox()
        self.status_filter.addItems(["All", "Active", "Completed", "Overdue"])
        self.status_filter.currentTextChanged.connect(self.apply_filters)
        
        self.equipment_filter = QComboBox()
        self.equipment_filter.addItem("All Equipment")
        equipment_list = self.db_manager.get_all_equipment()
        for equip in equipment_list:
            self.equipment_filter.addItem(equip['equipment_name'], equip['equipment_id'])
        self.equipment_filter.currentTextChanged.connect(self.apply_filters)
        
        filter_layout.addWidget(QLabel("Status:"))
        filter_layout.addWidget(self.status_filter)
        filter_layout.addWidget(QLabel("Equipment:"))
        filter_layout.addWidget(self.equipment_filter)
        filter_layout.addStretch()
        
        layout.addLayout(filter_layout)

        # Schedules Table
        self.table = QTableWidget()
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels([
            "Title", "Equipment", "Frequency", "Next Due",
            "Assigned To", "Status", "Last Generated", "Actions"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        
        layout.addWidget(self.table)

        # Status Summary
        status_layout = QHBoxLayout()
        self.status_label = QLabel()
        status_layout.addWidget(self.status_label)
        status_layout.addStretch()
        layout.addLayout(status_layout)

    def load_schedules(self):
        try:
            # Get all scheduled work orders, not just pending ones
            connection = self.db_manager.connect()
            cursor = connection.cursor(dictionary=True)
            
            # This query gets all schedules with their templates and calculates next due dates
            query = """
                SELECT 
                    ms.schedule_id,
                    ms.frequency,
                    ms.frequency_unit,
                    ms.start_date,
                    ms.end_date,
                    ms.last_generated,
                    ms.notification_days_before,
                    ms.notification_emails,
                    wot.template_id,
                    wot.title,
                    wot.description,
                    wot.equipment_id,
                    wot.priority,
                    wot.assignment_type,
                    wot.craftsman_id,
                    wot.team_id,
                    e.equipment_name,
                    CASE 
                        WHEN ms.last_generated IS NULL THEN ms.start_date
                        WHEN ms.frequency_unit = 'days' THEN DATE_ADD(ms.last_generated, INTERVAL ms.frequency DAY)
                        WHEN ms.frequency_unit = 'weeks' THEN DATE_ADD(ms.last_generated, INTERVAL ms.frequency WEEK)
                        WHEN ms.frequency_unit = 'months' THEN DATE_ADD(ms.last_generated, INTERVAL ms.frequency MONTH)
                    END as next_due_date,
                    (SELECT COUNT(*) FROM work_orders WHERE schedule_id = ms.schedule_id) as work_order_count
                FROM maintenance_schedules ms
                JOIN work_order_templates wot ON ms.schedule_id = wot.schedule_id
                LEFT JOIN equipment_registry e ON wot.equipment_id = e.equipment_id
                ORDER BY next_due_date ASC
            """
            
            cursor.execute(query)
            schedules = cursor.fetchall()
            self.db_manager.close(connection)
            
            self.table.setRowCount(len(schedules))
            
            for row, schedule in enumerate(schedules):
                # Title
                title_item = QTableWidgetItem(schedule['title'])
                title_item.setData(Qt.UserRole, schedule['schedule_id'])  # Store schedule_id for later use
                self.table.setItem(row, 0, title_item)
                
                # Equipment
                equipment_name = schedule['equipment_name'] if schedule['equipment_name'] else "Unknown"
                self.table.setItem(row, 1, QTableWidgetItem(equipment_name))
                
                # Frequency
                frequency = f"Every {schedule['frequency']} {schedule['frequency_unit']}"
                self.table.setItem(row, 2, QTableWidgetItem(frequency))
                
                # Next Due
                next_due = schedule['next_due_date']
                next_due_str = next_due.strftime('%Y-%m-%d') if next_due else "N/A"
                next_due_item = QTableWidgetItem(next_due_str)
                
                # Color-code based on due date
                if next_due:
                    days_until_due = (next_due - datetime.now().date()).days
                    if days_until_due < 0:
                        next_due_item.setBackground(QColor(255, 200, 200))  # Light red for overdue
                    elif days_until_due == 0:
                        next_due_item.setBackground(QColor(255, 255, 200))  # Light yellow for today
                    elif days_until_due <= 7:
                        next_due_item.setBackground(QColor(200, 255, 200))  # Light green for upcoming
                
                self.table.setItem(row, 3, next_due_item)
                
                # Assigned To
                if schedule['assignment_type'] == 'Individual':
                    craftsman = self.db_manager.get_craftsman_by_id(schedule['craftsman_id'])
                    assignee = f"{craftsman['first_name']} {craftsman['last_name']}" if craftsman else "Unknown"
                else:
                    team_name = self.db_manager.get_team_name(schedule['team_id'])
                    assignee = f"Team: {team_name}"
                self.table.setItem(row, 4, QTableWidgetItem(assignee))
                
                # Status
                days_until_due = (next_due - datetime.now().date()).days if next_due else 0
                if days_until_due < 0:
                    status = "Overdue"
                elif days_until_due == 0:
                    status = "Due Today"
                else:
                    status = "Active"
                
                status_item = QTableWidgetItem(status)
                if status == "Overdue":
                    status_item.setBackground(QColor(255, 200, 200))  # Light red
                elif status == "Due Today":
                    status_item.setBackground(QColor(255, 255, 200))  # Light yellow
                else:
                    status_item.setBackground(QColor(200, 255, 200))  # Light green
                
                self.table.setItem(row, 5, status_item)
                
                # Last Generated
                last_gen = schedule['last_generated']
                last_gen_str = last_gen.strftime('%Y-%m-%d') if last_gen else "Never"
                
                # Add count of work orders generated
                work_order_count = schedule.get('work_order_count', 0)
                if work_order_count > 0:
                    last_gen_str += f" ({work_order_count} WOs)"
                
                self.table.setItem(row, 6, QTableWidgetItem(last_gen_str))
                
                # Actions
                actions_widget = QWidget()
                actions_layout = QHBoxLayout(actions_widget)
                actions_layout.setContentsMargins(4, 0, 4, 0)
                actions_layout.setSpacing(4)
                
                edit_btn = QPushButton("Edit")
                edit_btn.setMaximumWidth(60)
                
                view_btn = QPushButton("View WOs")
                view_btn.setMaximumWidth(80)
                
                generate_btn = QPushButton("Generate")
                generate_btn.setMaximumWidth(80)
                
                delete_btn = QPushButton("Delete")
                delete_btn.setMaximumWidth(60)
                
                # Connect buttons to their respective functions
                edit_btn.clicked.connect(lambda checked, s=schedule: self.edit_schedule(s))
                view_btn.clicked.connect(lambda checked, s=schedule: self.view_work_orders(s))
                generate_btn.clicked.connect(lambda checked, s=schedule: self.generate_work_order(s))
                delete_btn.clicked.connect(lambda checked, s=schedule: self.delete_schedule(s))
                
                actions_layout.addWidget(edit_btn)
                actions_layout.addWidget(view_btn)
                actions_layout.addWidget(generate_btn)
                actions_layout.addWidget(delete_btn)
                self.table.setCellWidget(row, 7, actions_widget)
            
            self.update_status_bar()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load schedules: {str(e)}")

    def show_add_dialog(self):
        dialog = AddScheduleDialog(self.db_manager, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.load_schedules()

    def edit_schedule(self, schedule):
        # Implement edit functionality
        try:
            # Get the full schedule data
            connection = self.db_manager.connect()
            cursor = connection.cursor(dictionary=True)
            
            # Get schedule details
            cursor.execute("""
                SELECT ms.*, wot.* 
                FROM maintenance_schedules ms
                JOIN work_order_templates wot ON ms.schedule_id = wot.schedule_id
                WHERE ms.schedule_id = %s
            """, (schedule['schedule_id'],))
            
            schedule_data = cursor.fetchone()
            
            if not schedule_data:
                QMessageBox.warning(self, "Warning", "Schedule not found!")
                return
            
            # Create and configure the edit dialog
            dialog = AddScheduleDialog(self.db_manager, self, schedule['schedule_id'])
            
            # Set the dialog title
            dialog.setWindowTitle("Edit Schedule")
            
            # Populate the dialog with existing data
            dialog.title.setText(schedule_data['title'])
            dialog.description.setText(schedule_data['description'])
            
            # Set priority
            index = dialog.priority.findText(schedule_data['priority'])
            if index >= 0:
                dialog.priority.setCurrentIndex(index)
            
            # Set equipment
            equipment_index = dialog.equipment.findData(schedule_data['equipment_id'])
            if equipment_index >= 0:
                dialog.equipment.setCurrentIndex(equipment_index)
            
            # Set assignment type and assignee
            if schedule_data['assignment_type'] == 'Team':
                dialog.assignment_type.setCurrentText('Team')
                team_index = dialog.assignee.findData(schedule_data['team_id'])
                if team_index >= 0:
                    dialog.assignee.setCurrentIndex(team_index)
            else:
                dialog.assignment_type.setCurrentText('Individual')
                craftsman_index = dialog.assignee.findData(schedule_data['craftsman_id'])
                if craftsman_index >= 0:
                    dialog.assignee.setCurrentIndex(craftsman_index)
            
            # Set schedule details
            dialog.frequency.setValue(schedule_data['frequency'])
            dialog.frequency_unit.setCurrentText(schedule_data['frequency_unit'])
            
            # Set dates
            start_date = QDate.fromString(str(schedule_data['start_date']), "yyyy-MM-dd")
            dialog.start_date.setDate(start_date)
            
            if schedule_data['end_date']:
                end_date = QDate.fromString(str(schedule_data['end_date']), "yyyy-MM-dd")
                dialog.end_date.setDate(end_date)
            
            # Set notification settings
            dialog.notification_days.setValue(schedule_data['notification_days_before'])
            
            if schedule_data['notification_emails']:
                emails = json.loads(schedule_data['notification_emails'])
                dialog.notification_emails.setText(", ".join(emails))
            
            # Show the dialog
            if dialog.exec() == QDialog.DialogCode.Accepted:
                self.load_schedules()
        
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to edit schedule: {str(e)}")
        finally:
            self.db_manager.close(connection)

    def delete_schedule(self, schedule):
        reply = QMessageBox.question(
            self, "Confirm Delete",
            "Are you sure you want to delete this schedule?\nThis action cannot be undone.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                connection = self.db_manager.connect()
                cursor = connection.cursor()
                
                # First, check if there are any work orders using this schedule
                cursor.execute("""
                    SELECT COUNT(*) FROM work_orders 
                    WHERE schedule_id = %s
                """, (schedule['schedule_id'],))
                
                count = cursor.fetchone()[0]
                
                if count > 0:
                    # Ask if user wants to delete associated work orders
                    reply = QMessageBox.question(
                        self, "Associated Work Orders",
                        f"There are {count} work orders associated with this schedule. "
                        "Do you want to delete them as well?",
                        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No | 
                        QMessageBox.StandardButton.Cancel
                    )
                    
                    if reply == QMessageBox.StandardButton.Cancel:
                        return
                    
                    if reply == QMessageBox.StandardButton.Yes:
                        # Delete associated work orders
                        cursor.execute("""
                            DELETE FROM work_orders 
                            WHERE schedule_id = %s
                        """, (schedule['schedule_id'],))
                    else:
                        # Just remove the schedule_id from work orders
                        cursor.execute("""
                            UPDATE work_orders 
                            SET schedule_id = NULL 
                            WHERE schedule_id = %s
                        """, (schedule['schedule_id'],))
                
                # Delete the work order template
                cursor.execute("""
                    DELETE FROM work_order_templates 
                    WHERE schedule_id = %s
                """, (schedule['schedule_id'],))
                
                # Delete the schedule
                cursor.execute("""
                    DELETE FROM maintenance_schedules 
                    WHERE schedule_id = %s
                """, (schedule['schedule_id'],))
                
                connection.commit()
                QMessageBox.information(self, "Success", "Schedule deleted successfully!")
                self.load_schedules()
                
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to delete schedule: {str(e)}")
            finally:
                self.db_manager.close(connection)

    def apply_filters(self):
        """Apply filters to the schedules table"""
        try:
            status_filter = self.status_filter.currentText()
            equipment_filter = self.equipment_filter.currentData()
            
            # Loop through all rows and hide/show based on filters
            for row in range(self.table.rowCount()):
                show_row = True
                
                # Apply status filter
                if status_filter != "All":
                    status_item = self.table.item(row, 5)  # Status column
                    if status_item and status_item.text() != status_filter:
                        # Special case for "Overdue" which might be "Due Today" in the filter
                        if not (status_filter == "Overdue" and status_item.text() == "Due Today"):
                            show_row = False
                
                # Apply equipment filter
                if equipment_filter and show_row:
                    equipment_item = self.table.item(row, 1)  # Equipment column
                    equipment_name = self.equipment_filter.currentText()
                    if equipment_item and equipment_item.text() != equipment_name:
                        show_row = False
                
                # Show or hide the row
                self.table.setRowHidden(row, not show_row)
            
            # Update status bar with filtered counts
            self.update_status_bar()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to apply filters: {str(e)}")

    def update_status_bar(self):
        total = self.table.rowCount()
        active = sum(1 for row in range(total) 
                    if self.table.item(row, 5).text() == "Active")
        overdue = sum(1 for row in range(total) 
                     if self.table.item(row, 5).text() == "Overdue")
        
        self.status_label.setText(
            f"Total Schedules: {total} | Active: {active} | Overdue: {overdue}"
        )

    def view_work_orders(self, schedule):
        """View all work orders generated from this schedule"""
        try:
            schedule_id = schedule['schedule_id']
            
            # Get all work orders for this schedule
            connection = self.db_manager.connect()
            cursor = connection.cursor(dictionary=True)
            
            cursor.execute("""
                SELECT wo.*, e.equipment_name,
                       CASE 
                           WHEN wo.assignment_type = 'Individual' THEN 
                               CONCAT(c.first_name, ' ', c.last_name)
                           ELSE t.team_name
                       END as assignee
                FROM work_orders wo
                LEFT JOIN equipment_registry e ON wo.equipment_id = e.equipment_id
                LEFT JOIN craftsmen c ON wo.craftsman_id = c.craftsman_id
                LEFT JOIN craftsmen_teams t ON wo.team_id = t.team_id
                WHERE wo.schedule_id = %s
                ORDER BY wo.created_date DESC
            """, (schedule_id,))
            
            work_orders = cursor.fetchall()
            self.db_manager.close(connection)
            
            if not work_orders:
                QMessageBox.information(self, "No Work Orders", 
                                       "No work orders have been generated from this schedule yet.")
                return
            
            # Create a dialog to display the work orders
            dialog = QDialog(self)
            dialog.setWindowTitle(f"Work Orders for Schedule: {schedule['title']}")
            dialog.resize(800, 500)
            
            layout = QVBoxLayout(dialog)
            
            # Add header
            header = QLabel(f"Work Orders for: {schedule['title']}")
            header.setStyleSheet("font-size: 16px; font-weight: bold;")
            layout.addWidget(header)
            
            # Create table for work orders
            table = QTableWidget()
            table.setColumnCount(7)
            table.setHorizontalHeaderLabels([
                "ID", "Status", "Due Date", "Completed Date", 
                "Assigned To", "Priority", "Actions"
            ])
            
            table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
            table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
            
            table.setRowCount(len(work_orders))
            
            for row, wo in enumerate(work_orders):
                # ID
                table.setItem(row, 0, QTableWidgetItem(str(wo['work_order_id'])))
                
                # Status
                status_item = QTableWidgetItem(wo['status'])
                if wo['status'] == 'Completed':
                    status_item.setBackground(QColor(200, 255, 200))  # Light green
                elif wo['status'] == 'Open':
                    status_item.setBackground(QColor(200, 200, 255))  # Light blue
                elif wo['status'] == 'In Progress':
                    status_item.setBackground(QColor(255, 255, 200))  # Light yellow
                elif wo['status'] == 'Overdue':
                    status_item.setBackground(QColor(255, 200, 200))  # Light red
                table.setItem(row, 1, status_item)
                
                # Due Date
                due_date = wo['due_date'].strftime('%Y-%m-%d') if wo['due_date'] else "N/A"
                table.setItem(row, 2, QTableWidgetItem(due_date))
                
                # Completed Date
                completed_date = wo['completed_date'].strftime('%Y-%m-%d') if wo['completed_date'] else "N/A"
                table.setItem(row, 3, QTableWidgetItem(completed_date))
                
                # Assigned To
                table.setItem(row, 4, QTableWidgetItem(wo['assignee'] if wo.get('assignee') else "Unassigned"))
                
                # Priority
                priority_item = QTableWidgetItem(wo['priority'])
                if wo['priority'] == 'Critical':
                    priority_item.setBackground(QColor(255, 150, 150))  # Red
                elif wo['priority'] == 'High':
                    priority_item.setBackground(QColor(255, 200, 150))  # Orange
                elif wo['priority'] == 'Medium':
                    priority_item.setBackground(QColor(255, 255, 150))  # Yellow
                table.setItem(row, 5, priority_item)
                
                # Actions
                actions_widget = QWidget()
                actions_layout = QHBoxLayout(actions_widget)
                actions_layout.setContentsMargins(4, 0, 4, 0)
                
                view_btn = QPushButton("View")
                view_btn.clicked.connect(lambda checked, work_order_id=wo['work_order_id']: 
                                        self.view_work_order_details(work_order_id))
                
                actions_layout.addWidget(view_btn)
                table.setCellWidget(row, 6, actions_widget)
            
            layout.addWidget(table)
            
            # Add close button
            close_btn = QPushButton("Close")
            close_btn.clicked.connect(dialog.accept)
            layout.addWidget(close_btn)
            
            dialog.exec()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to view work orders: {str(e)}")

    def view_work_order_details(self, work_order_id):
        """View details of a specific work order"""
        try:
            # Get the work order data
            work_order = self.db_manager.get_work_order_by_id(work_order_id)
            if not work_order:
                QMessageBox.warning(self, "Not Found", "Work order not found.")
                return
            
            # Create a dialog to show work order details
            from workOrders.work_order_dialog import WorkOrderDialog
            dialog = WorkOrderDialog(self.db_manager, work_order, parent=self)
            dialog.exec()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to view work order details: {str(e)}")

    def generate_work_order(self, schedule):
        """Manually generate a work order from this schedule"""
        try:
            reply = QMessageBox.question(
                self, "Generate Work Order",
                f"Are you sure you want to generate a new work order from the schedule '{schedule['title']}'?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                # Calculate the next due date
                next_due_date = schedule['next_due_date']
                
                # Generate the work order
                work_order_id = self.db_manager.generate_scheduled_work_order(schedule, next_due_date)
                
                if work_order_id:
                    QMessageBox.information(
                        self, "Success", 
                        f"Work order #{work_order_id} has been generated successfully!"
                    )
                    # Refresh the schedules list
                    self.load_schedules()
                else:
                    QMessageBox.warning(
                        self, "Warning", 
                        "Failed to generate work order. Please check the logs for details."
                    )
        
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to generate work order: {str(e)}")