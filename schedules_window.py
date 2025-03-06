from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, 
                              QTableWidget, QTableWidgetItem, QPushButton, QLabel, 
                              QComboBox, QSpinBox, QDateEdit, QDialog, QFormLayout,
                              QLineEdit, QTextEdit, QMessageBox, QHeaderView)
from PySide6.QtCore import Qt, QDate
import json
from datetime import datetime, timedelta

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
            schedules = self.db_manager.get_pending_scheduled_work_orders()
            self.table.setRowCount(len(schedules))
            
            for row, schedule in enumerate(schedules):
                # Title
                self.table.setItem(row, 0, QTableWidgetItem(schedule['title']))
                
                # Equipment
                equipment = self.db_manager.get_equipment_by_id(schedule['equipment_id'])
                equipment_name = equipment['equipment_name'] if equipment else "Unknown"
                self.table.setItem(row, 1, QTableWidgetItem(equipment_name))
                
                # Frequency
                frequency = f"Every {schedule['frequency']} {schedule['frequency_unit']}"
                self.table.setItem(row, 2, QTableWidgetItem(frequency))
                
                # Next Due
                next_due = schedule['next_due_date']
                next_due_str = next_due.strftime('%Y-%m-%d') if next_due else "N/A"
                self.table.setItem(row, 3, QTableWidgetItem(next_due_str))
                
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
                self.table.setItem(row, 5, QTableWidgetItem(status))
                
                # Last Generated
                last_gen = schedule['last_generated']
                last_gen_str = last_gen.strftime('%Y-%m-%d') if last_gen else "Never"
                self.table.setItem(row, 6, QTableWidgetItem(last_gen_str))
                
                # Actions
                actions_widget = QWidget()
                actions_layout = QHBoxLayout(actions_widget)
                actions_layout.setContentsMargins(0, 0, 0, 0)
                
                edit_btn = QPushButton("Edit")
                delete_btn = QPushButton("Delete")
                
                edit_btn.clicked.connect(lambda checked, s=schedule: self.edit_schedule(s))
                delete_btn.clicked.connect(lambda checked, s=schedule: self.delete_schedule(s))
                
                actions_layout.addWidget(edit_btn)
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
        # Implement filtering functionality
        try:
            # Get filter values
            equipment_id = self.equipment_filter.currentData()
            assignee_type = self.assignee_type_filter.currentText()
            assignee_id = self.assignee_filter.currentData()
            frequency_unit = self.frequency_filter.currentText()
            
            # Build SQL query with filters
            query = """
                SELECT 
                    ms.schedule_id,
                    wot.title,
                    wot.description,
                    e.equipment_name,
                    ms.frequency,
                    ms.frequency_unit,
                    ms.start_date,
                    ms.end_date,
                    ms.last_generated,
                    CASE 
                        WHEN wot.assignment_type = 'Individual' THEN 
                            CONCAT(c.first_name, ' ', c.last_name)
                        ELSE t.team_name
                    END as assignee,
                    wot.assignment_type
                FROM maintenance_schedules ms
                JOIN work_order_templates wot ON ms.schedule_id = wot.schedule_id
                LEFT JOIN equipment_registry e ON wot.equipment_id = e.equipment_id
                LEFT JOIN craftsmen c ON wot.craftsman_id = c.craftsman_id
                LEFT JOIN craftsmen_teams t ON wot.team_id = t.team_id
                WHERE 1=1
            """
            
            params = []
            
            # Add equipment filter
            if equipment_id:
                query += " AND wot.equipment_id = %s"
                params.append(equipment_id)
            
            # Add assignee type filter
            if assignee_type != "All":
                query += " AND wot.assignment_type = %s"
                params.append(assignee_type)
                
                # Add specific assignee filter
                if assignee_id:
                    if assignee_type == "Individual":
                        query += " AND wot.craftsman_id = %s"
                    else:
                        query += " AND wot.team_id = %s"
                    params.append(assignee_id)
            
            # Add frequency filter
            if frequency_unit != "All":
                query += " AND ms.frequency_unit = %s"
                params.append(frequency_unit.lower())
            
            # Execute query
            connection = self.db_manager.connect()
            cursor = connection.cursor(dictionary=True)
            cursor.execute(query, params)
            schedules = cursor.fetchall()
            
            # Clear the table
            self.table.setRowCount(0)
            
            # Populate the table with filtered results
            for row, schedule in enumerate(schedules):
                self.table.insertRow(row)
                
                # Format dates for display
                start_date = schedule['start_date'].strftime('%Y-%m-%d') if schedule['start_date'] else ''
                end_date = schedule['end_date'].strftime('%Y-%m-%d') if schedule['end_date'] else 'None'
                last_generated = schedule['last_generated'].strftime('%Y-%m-%d') if schedule['last_generated'] else 'Never'
                
                # Calculate next run date
                if schedule['last_generated']:
                    if schedule['frequency_unit'] == 'days':
                        next_run = (schedule['last_generated'] + timedelta(days=schedule['frequency'])).strftime('%Y-%m-%d')
                    elif schedule['frequency_unit'] == 'weeks':
                        next_run = (schedule['last_generated'] + timedelta(weeks=schedule['frequency'])).strftime('%Y-%m-%d')
                    elif schedule['frequency_unit'] == 'months':
                        # Approximate months as 30 days
                        next_run = (schedule['last_generated'] + timedelta(days=30*schedule['frequency'])).strftime('%Y-%m-%d')
                else:
                    next_run = start_date
                
                # Add data to table
                self.table.setItem(row, 0, QTableWidgetItem(schedule['title']))
                self.table.setItem(row, 1, QTableWidgetItem(schedule['equipment_name'] or ''))
                self.table.setItem(row, 2, QTableWidgetItem(schedule['assignee'] or ''))
                self.table.setItem(row, 3, QTableWidgetItem(f"{schedule['frequency']} {schedule['frequency_unit']}"))
                self.table.setItem(row, 4, QTableWidgetItem(start_date))
                self.table.setItem(row, 5, QTableWidgetItem(last_generated))
                self.table.setItem(row, 6, QTableWidgetItem(next_run))
                
                # Add action buttons
                actions_widget = QWidget()
                actions_layout = QHBoxLayout(actions_widget)
                actions_layout.setContentsMargins(0, 0, 0, 0)
                
                edit_btn = QPushButton("Edit")
                delete_btn = QPushButton("Delete")
                
                edit_btn.clicked.connect(lambda checked, s=schedule: self.edit_schedule(s))
                delete_btn.clicked.connect(lambda checked, s=schedule: self.delete_schedule(s))
                
                actions_layout.addWidget(edit_btn)
                actions_layout.addWidget(delete_btn)
                self.table.setCellWidget(row, 7, actions_widget)
            
            self.update_status_bar()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to apply filters: {str(e)}")
        finally:
            self.db_manager.close(connection)

    def update_status_bar(self):
        total = self.table.rowCount()
        active = sum(1 for row in range(total) 
                    if self.table.item(row, 5).text() == "Active")
        overdue = sum(1 for row in range(total) 
                     if self.table.item(row, 5).text() == "Overdue")
        
        self.status_label.setText(
            f"Total Schedules: {total} | Active: {active} | Overdue: {overdue}"
        )