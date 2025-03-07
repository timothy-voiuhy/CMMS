from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                              QPushButton, QLabel, QTabWidget, QLineEdit,
                              QComboBox, QDateEdit, QTableWidget, QTableWidgetItem,
                              QDialog, QFormLayout, QMessageBox, QScrollArea,
                              QSplitter, QTextEdit, QMenuBar, QMenu, QSizePolicy,
                              )
from PySide6.QtCore import Qt, Signal, QRect
from PySide6.QtGui import QPainter, QColor
from PySide6.QtPrintSupport import QPrinter
from datetime import datetime, timedelta
import random
import os
import json
from ui.card_table_widget import CardTableWidget

# Add this class definition to the file

class CraftsmanDetailsDialog(QDialog):
    def __init__(self, craftsman_id, db_manager, parent=None, read_only=False):
        super().__init__(parent)
        self.craftsman_id = craftsman_id
        self.db_manager = db_manager
        self.setWindowTitle("Craftsman Details")
        self.setMinimumWidth(800)
        
        layout = QVBoxLayout(self)
        
        # Create tab widget for different sections
        self.tab_widget = QTabWidget()
        layout.addWidget(self.tab_widget)
        
        # Setup tabs
        self.setup_basic_info_tab()
        self.setup_skills_tab()
        self.setup_work_history_tab()
        self.setup_training_tab()
        self.setup_schedule_tab()
        self.setup_teams_tab()
        
        # Add close button
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.close)
        layout.addWidget(close_btn)

    def setup_basic_info_tab(self):
        basic_info = QWidget()
        layout = QFormLayout(basic_info)
        
        # Get craftsman data
        craftsman = self.db_manager.get_craftsman_by_id(self.craftsman_id)
        if not craftsman:
            return
        
        # Create fields
        self.edit_first_name = QLineEdit(craftsman['first_name'])
        self.edit_last_name = QLineEdit(craftsman['last_name'])
        self.edit_phone = QLineEdit(craftsman['phone'])
        self.edit_email = QLineEdit(craftsman['email'])
        self.edit_specialization = QComboBox()
        self.edit_specialization.addItems(["Mechanical", "Electrical", "HVAC", "Plumbing"])
        self.edit_specialization.setCurrentText(craftsman['specialization'])
        self.edit_status = QComboBox()
        self.edit_status.addItems(["Active", "Inactive"])
        self.edit_status.setCurrentText(craftsman['status'])
        
        # Add fields to layout
        layout.addRow("Employee ID:", QLabel(craftsman['employee_id']))
        layout.addRow("First Name:", self.edit_first_name)
        layout.addRow("Last Name:", self.edit_last_name)
        layout.addRow("Phone:", self.edit_phone)
        layout.addRow("Email:", self.edit_email)
        layout.addRow("Specialization:", self.edit_specialization)
        layout.addRow("Status:", self.edit_status)
        layout.addRow("Hire Date:", QLabel(str(craftsman['hire_date'])))
        
        # Add update button
        update_btn = QPushButton("Update Information")
        update_btn.clicked.connect(self.update_basic_info)
        layout.addRow("", update_btn)
        
        self.tab_widget.addTab(basic_info, "Basic Information")

    def setup_skills_tab(self):
        skills_widget = QWidget()
        layout = QVBoxLayout(skills_widget)
        
        # Add skills table
        self.skills_table = QTableWidget()
        self.skills_table.setColumnCount(6)
        self.skills_table.setHorizontalHeaderLabels([
            "Skill Name", "Level", "Certification",
            "Cert. Date", "Expiry Date", "Authority"
        ])
        
        # Set column widths
        self.skills_table.setColumnWidth(0, 120)  # Skill Name
        self.skills_table.setColumnWidth(1, 80)   # Level
        self.skills_table.setColumnWidth(2, 150)  # Certification
        self.skills_table.setColumnWidth(3, 100)  # Cert. Date
        self.skills_table.setColumnWidth(4, 100)  # Expiry Date
        self.skills_table.setColumnWidth(5, 150)  # Authority
        
        # Make table stretch to fill available space
        self.skills_table.horizontalHeader().setStretchLastSection(True)
        self.skills_table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        layout.addWidget(self.skills_table)
        
        # Add new skill button
        add_skill_btn = QPushButton("Add New Skill")
        add_skill_btn.clicked.connect(self.add_skill_dialog)
        layout.addWidget(add_skill_btn)
        
        self.load_skills()
        self.tab_widget.addTab(skills_widget, "Skills & Certifications")

    def setup_work_history_tab(self):
        history_widget = QWidget()
        layout = QVBoxLayout(history_widget)
        
        # Add work history table
        self.history_table = QTableWidget()
        self.history_table.setColumnCount(6)
        self.history_table.setHorizontalHeaderLabels([
            "Date", "Equipment", "Task Type",
            "Description", "Performance", "Time Taken"
        ])
        layout.addWidget(self.history_table)
        
        self.load_work_history()
        self.tab_widget.addTab(history_widget, "Work History")

    def setup_training_tab(self):
        training_widget = QWidget()
        layout = QVBoxLayout(training_widget)
        
        # Add training table
        self.training_table = QTableWidget()
        self.training_table.setColumnCount(6)
        self.training_table.setHorizontalHeaderLabels([
            "Training Name", "Start Date", "Completion Date",
            "Provider", "Certification", "Status"
        ])
        layout.addWidget(self.training_table)
        
        # Add new training button
        add_training_btn = QPushButton("Add Training Record")
        add_training_btn.clicked.connect(self.add_training_dialog)
        layout.addWidget(add_training_btn)
        
        self.load_training_records()
        self.tab_widget.addTab(training_widget, "Training Records")

    def setup_schedule_tab(self):
        schedule_widget = QWidget()
        layout = QVBoxLayout(schedule_widget)
        
        # Add schedule table
        self.schedule_table = QTableWidget()
        self.schedule_table.setColumnCount(5)
        self.schedule_table.setHorizontalHeaderLabels([
            "Date", "Shift Start", "Shift End", "Status", "Notes"
        ])
        layout.addWidget(self.schedule_table)
        
        self.load_schedule()
        self.tab_widget.addTab(schedule_widget, "Schedule")

    def setup_teams_tab(self):
        """Setup tab showing teams the craftsman belongs to"""
        teams_widget = QWidget()
        layout = QVBoxLayout(teams_widget)
        
        # Add teams table
        self.teams_table = QTableWidget()
        self.teams_table.setColumnCount(5)
        self.teams_table.setHorizontalHeaderLabels([
            "Team Name", "Team Leader", "Role", "Joined Date", "Description"
        ])
        
        # Set column widths
        self.teams_table.setColumnWidth(0, 150)  # Team Name
        self.teams_table.setColumnWidth(1, 150)  # Team Leader
        self.teams_table.setColumnWidth(2, 100)  # Role
        self.teams_table.setColumnWidth(3, 100)  # Joined Date
        self.teams_table.setColumnWidth(4, 250)  # Description
        
        layout.addWidget(self.teams_table)
        
        self.tab_widget.addTab(teams_widget, "Teams")
        self.load_teams()

    # Add helper methods for loading data and handling updates
    def update_basic_info(self):
        try:
            data = {
                'employee_id': self.craftsman_id,  # This is the employee_id we received in constructor
                'first_name': self.edit_first_name.text(),
                'last_name': self.edit_last_name.text(),
                'phone': self.edit_phone.text(),
                'email': self.edit_email.text(),
                'specialization': self.edit_specialization.currentText(),
                'status': self.edit_status.currentText()
            }
            
            if self.db_manager.update_craftsman(data):
                QMessageBox.information(self, "Success", "Craftsman information updated successfully!")
                self.accept()  # Close dialog with success
                return True
            else:
                QMessageBox.warning(self, "Error", "Failed to update craftsman information!")
                return False
        except Exception as e:
            QMessageBox.warning(self, "Error", f"An error occurred while updating: {str(e)}")
            return False

    def add_skill_dialog(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Add New Skill")
        layout = QFormLayout(dialog)
        
        # Create input fields
        skill_name = QLineEdit()
        skill_level = QComboBox()
        skill_level.addItems(["Basic", "Intermediate", "Advanced", "Expert"])
        certification = QLineEdit()
        cert_date = QDateEdit()
        cert_date.setCalendarPopup(True)
        cert_date.setDate(datetime.now().date())
        expiry_date = QDateEdit()
        expiry_date.setCalendarPopup(True)
        expiry_date.setDate(datetime.now().date())
        authority = QLineEdit()
        
        # Add fields to layout
        layout.addRow("Skill Name:", skill_name)
        layout.addRow("Skill Level:", skill_level)
        layout.addRow("Certification:", certification)
        layout.addRow("Certification Date:", cert_date)
        layout.addRow("Expiry Date:", expiry_date)
        layout.addRow("Authority:", authority)
        
        # Add buttons
        buttons = QHBoxLayout()
        save_btn = QPushButton("Save")
        cancel_btn = QPushButton("Cancel")
        buttons.addWidget(save_btn)
        buttons.addWidget(cancel_btn)
        layout.addRow("", buttons)
        
        # Connect buttons
        save_btn.clicked.connect(lambda: self.save_skill({
            'craftsman_id': self.craftsman_id,
            'skill_name': skill_name.text(),
            'skill_level': skill_level.currentText(),
            'certification': certification.text(),
            'certification_date': cert_date.date().toPython(),
            'expiry_date': expiry_date.date().toPython(),
            'certification_authority': authority.text()
        }, dialog))
        cancel_btn.clicked.connect(dialog.reject)
        
        dialog.exec()

    def save_skill(self, data, dialog):
        if self.db_manager.add_craftsman_skill(data):
            QMessageBox.information(self, "Success", "Skill added successfully!")
            self.load_skills()
            dialog.accept()
        else:
            QMessageBox.warning(self, "Error", "Failed to add skill!")

    def load_skills(self):
        skills = self.db_manager.get_craftsman_skills(self.craftsman_id)
        self.skills_table.setRowCount(len(skills))
        
        for row, skill in enumerate(skills):
            self.skills_table.setItem(row, 0, QTableWidgetItem(skill['skill_name']))
            self.skills_table.setItem(row, 1, QTableWidgetItem(skill['skill_level']))
            self.skills_table.setItem(row, 2, QTableWidgetItem(skill['certification']))
            self.skills_table.setItem(row, 3, QTableWidgetItem(str(skill['certification_date'])))
            self.skills_table.setItem(row, 4, QTableWidgetItem(str(skill['expiry_date'])))
            self.skills_table.setItem(row, 5, QTableWidgetItem(skill['certification_authority']))

    def add_training_dialog(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Add Training Record")
        layout = QFormLayout(dialog)
        
        # Create input fields
        training_name = QLineEdit()
        start_date = QDateEdit()
        start_date.setCalendarPopup(True)
        start_date.setDate(datetime.now().date())
        completion_date = QDateEdit()
        completion_date.setCalendarPopup(True)
        completion_date.setDate(datetime.now().date())
        provider = QLineEdit()
        certification = QLineEdit()
        status = QComboBox()
        status.addItems(["Scheduled", "In Progress", "Completed", "Failed"])
        
        # Add fields to layout
        layout.addRow("Training Name:", training_name)
        layout.addRow("Start Date:", start_date)
        layout.addRow("Completion Date:", completion_date)
        layout.addRow("Provider:", provider)
        layout.addRow("Certification:", certification)
        layout.addRow("Status:", status)
        
        # Add buttons
        buttons = QHBoxLayout()
        save_btn = QPushButton("Save")
        cancel_btn = QPushButton("Cancel")
        buttons.addWidget(save_btn)
        buttons.addWidget(cancel_btn)
        layout.addRow("", buttons)
        
        # Connect buttons
        save_btn.clicked.connect(lambda: self.save_training({
            'craftsman_id': self.craftsman_id,
            'training_name': training_name.text(),
            'training_date': start_date.date().toPython(),
            'completion_date': completion_date.date().toPython(),
            'training_provider': provider.text(),
            'certification_received': certification.text(),
            'training_status': status.currentText()
        }, dialog))
        cancel_btn.clicked.connect(dialog.reject)
        
        dialog.exec()

    def save_training(self, data, dialog):
        if self.db_manager.add_craftsman_training(data):
            QMessageBox.information(self, "Success", "Training record added successfully!")
            self.load_training_records()
            dialog.accept()
        else:
            QMessageBox.warning(self, "Error", "Failed to add training record!")

    def load_training_records(self):
        records = self.db_manager.get_craftsman_training(self.craftsman_id)
        self.training_table.setRowCount(len(records))
        
        for row, record in enumerate(records):
            self.training_table.setItem(row, 0, QTableWidgetItem(record['training_name']))
            self.training_table.setItem(row, 1, QTableWidgetItem(str(record['training_date'])))
            self.training_table.setItem(row, 2, QTableWidgetItem(str(record['completion_date'])))
            self.training_table.setItem(row, 3, QTableWidgetItem(record['training_provider']))
            self.training_table.setItem(row, 4, QTableWidgetItem(record['certification_received']))
            self.training_table.setItem(row, 5, QTableWidgetItem(record['training_status']))

    def load_work_history(self):
        history = self.db_manager.get_craftsman_work_history(self.craftsman_id)
        self.history_table.setRowCount(len(history))
        
        for row, entry in enumerate(history):
            self.history_table.setItem(row, 0, QTableWidgetItem(str(entry['task_date'])))
            self.history_table.setItem(row, 1, QTableWidgetItem(str(entry['equipment_id'])))
            self.history_table.setItem(row, 2, QTableWidgetItem(entry['task_type']))
            self.history_table.setItem(row, 3, QTableWidgetItem(entry['task_description']))
            self.history_table.setItem(row, 4, QTableWidgetItem(str(entry['performance_rating'])))
            self.history_table.setItem(row, 5, QTableWidgetItem(str(entry['completion_time'])))

    def load_schedule(self):
        schedule = self.db_manager.get_craftsman_schedule(self.craftsman_id)
        self.schedule_table.setRowCount(len(schedule))
        
        for row, shift in enumerate(schedule):
            self.schedule_table.setItem(row, 0, QTableWidgetItem(str(shift['date'])))
            self.schedule_table.setItem(row, 1, QTableWidgetItem(str(shift['shift_start'])))
            self.schedule_table.setItem(row, 2, QTableWidgetItem(str(shift['shift_end'])))
            self.schedule_table.setItem(row, 3, QTableWidgetItem(shift['status']))
            self.schedule_table.setItem(row, 4, QTableWidgetItem(shift['notes']))

    def load_teams(self):
        """Load teams that the craftsman belongs to"""
        try:
            # First, we need to get the craftsman's internal ID (craftsman_id) from the employee_id
            connection = self.db_manager.connect()
            cursor = connection.cursor(dictionary=True)
            
            # Get the craftsman's internal ID if we received an employee_id
            if not str(self.craftsman_id).isdigit():
                cursor.execute("""
                    SELECT craftsman_id FROM craftsmen 
                    WHERE employee_id = %s
                """, (self.craftsman_id,))
                
                result = cursor.fetchone()
                if result:
                    internal_id = result['craftsman_id']
                else:
                    print(f"Could not find craftsman with ID: {self.craftsman_id}")
                    return
            else:
                internal_id = self.craftsman_id
            
            # Now get the teams using the internal ID
            teams = self.db_manager.get_craftsman_teams(internal_id)
            self.teams_table.setRowCount(len(teams))
            
            for row, team in enumerate(teams):
                self.teams_table.setItem(row, 0, QTableWidgetItem(team['team_name']))
                
                # Format team leader name
                leader_name = "Not Assigned"
                if team.get('leader_first_name') and team.get('leader_last_name'):
                    leader_name = f"{team['leader_first_name']} {team['leader_last_name']}"
                self.teams_table.setItem(row, 1, QTableWidgetItem(leader_name))
                
                # Role and joined date
                self.teams_table.setItem(row, 2, QTableWidgetItem(team['role']))
                self.teams_table.setItem(row, 3, QTableWidgetItem(str(team['joined_date'])))
                
                # Description
                self.teams_table.setItem(row, 4, QTableWidgetItem(team.get('description', '')))
                
        except Exception as e:
            print(f"Error loading craftsman teams: {e}")
        finally:
            if 'connection' in locals() and connection:
                self.db_manager.close(connection)


class CraftsMenWindow(QMainWindow):
    def __init__(self, parent=None, db_manager=None):
        super().__init__(parent=parent)
        self.db_manager = db_manager
        self.setWindowTitle("Craftsmen Management")

        # Create central widget and layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.central_layout = QVBoxLayout(self.central_widget)
        
        # Create search bar
        self.setup_search_bar()
        
        # Create tab widget
        self.tab_widget = QTabWidget()
        self.central_layout.addWidget(self.tab_widget)
        
        # Setup tabs
        self.setup_craftsmen_list_tab()
        self.setup_registration_tab()
        self.setup_schedule_tab()
        self.setup_reports_tab()
        self.setup_teams_tab()
        
        # Setup menu bar
        self.setup_menu_bar()

    def setup_search_bar(self):
        """Setup the search bar with filters"""
        search_widget = QWidget()
        search_layout = QHBoxLayout(search_widget)
        
        # Create search fields
        self.search_name = QLineEdit()
        self.search_name.setPlaceholderText("Search by name...")
        self.search_name.textChanged.connect(self.search_craftsmen)
        
        self.search_specialization = QComboBox()
        self.search_specialization.addItems(["All Specializations", "Mechanical", "Electrical", "HVAC", "Plumbing"])
        self.search_specialization.currentTextChanged.connect(self.search_craftsmen)
        
        self.search_status = QComboBox()
        self.search_status.addItems(["All Status", "Active", "Inactive"])
        self.search_status.currentTextChanged.connect(self.search_craftsmen)
        
        self.search_experience = QComboBox()
        self.search_experience.addItems(["All Experience Levels", "Entry Level", "Intermediate", "Expert", "Master"])
        self.search_experience.currentTextChanged.connect(self.search_craftsmen)
        
        search_layout.addWidget(QLabel("Name:"))
        search_layout.addWidget(self.search_name)
        search_layout.addWidget(QLabel("Specialization:"))
        search_layout.addWidget(self.search_specialization)
        search_layout.addWidget(QLabel("Experience Level:"))
        search_layout.addWidget(self.search_experience)
        search_layout.addWidget(QLabel("Status:"))
        search_layout.addWidget(self.search_status)
        
        self.central_layout.addWidget(search_widget)

    def setup_craftsmen_list_tab(self):
        list_widget = QWidget()
        list_layout = QVBoxLayout(list_widget)
        
        # Create card table widget instead of regular table
        self.craftsmen_cards = CardTableWidget()
        
        # Define display fields
        display_fields = [
            {'field': 'full_name', 'display': 'Name'},
            {'field': 'specialization', 'display': 'Specialization'},
            {'field': 'experience_level', 'display': 'Experience'},
            {'field': 'phone', 'display': 'Phone'},
            {'field': 'email', 'display': 'Email'},
            {'field': 'status', 'display': 'Status', 'type': 'status', 
             'colors': {'Active': '#4CAF50', 'Inactive': '#F44336'}}
        ]
        self.craftsmen_cards.set_display_fields(display_fields)
        
        # Connect signals
        self.craftsmen_cards.itemClicked.connect(self.handle_craftsman_click)
        # self.craftsmen_cards.itemDoubleClicked.connect(self.show_craftsman_details)
        self.craftsmen_cards.itemEditClicked.connect(self.edit_craftsman)
        
        list_layout.addWidget(self.craftsmen_cards)
        
        # Create hidden table for compatibility with existing code
        self.craftsmen_table = QTableWidget()
        self.craftsmen_table.setColumnCount(8)
        self.craftsmen_table.setHorizontalHeaderLabels([
            "ID", "Name", "Specialization", "Experience",
            "Phone", "Email", "Status", "Hire Date"
        ])
        self.craftsmen_table.hide()  # Hide the table since we're using cards
        list_layout.addWidget(self.craftsmen_table)
        
        # Keep the refresh button
        refresh_btn = QPushButton("Refresh List")
        refresh_btn.clicked.connect(self.load_craftsmen)
        list_layout.addWidget(refresh_btn)
        
        self.tab_widget.addTab(list_widget, "Craftsmen List")
        self.load_craftsmen()

    def setup_registration_tab(self):
        reg_widget = QWidget()
        reg_layout = QFormLayout(reg_widget)
        
        # Create registration fields
        self.emp_id = QLineEdit()
        self.first_name = QLineEdit()
        self.last_name = QLineEdit()
        self.phone = QLineEdit()
        self.email = QLineEdit()
        self.specialization = QComboBox()
        self.specialization.addItems(["Mechanical", "Electrical", "HVAC", "Plumbing"])
        self.experience = QComboBox()
        self.experience.addItems(["Entry Level", "Intermediate", "Expert", "Master"])
        self.hire_date = QDateEdit()
        self.hire_date.setCalendarPopup(True)
        self.hire_date.setDate(datetime.now().date())
        
        # Add fields to layout
        reg_layout.addRow("Employee ID:", self.emp_id)
        reg_layout.addRow("First Name:", self.first_name)
        reg_layout.addRow("Last Name:", self.last_name)
        reg_layout.addRow("Phone:", self.phone)
        reg_layout.addRow("Email:", self.email)
        reg_layout.addRow("Specialization:", self.specialization)
        reg_layout.addRow("Experience Level:", self.experience)
        reg_layout.addRow("Hire Date:", self.hire_date)
        
        # Add buttons layout
        buttons_layout = QHBoxLayout()
        
        # Add register button
        register_btn = QPushButton("Register Craftsman")
        register_btn.clicked.connect(self.register_craftsman)
        buttons_layout.addWidget(register_btn)
        
        # Add generate demo data button
        demo_btn = QPushButton("Generate Demo Data")
        demo_btn.clicked.connect(self.fill_demo_data)
        buttons_layout.addWidget(demo_btn)
        
        # Add bulk demo data button
        bulk_demo_btn = QPushButton("Add 10 Demo Craftsmen")
        bulk_demo_btn.clicked.connect(self.add_bulk_demo_data)
        buttons_layout.addWidget(bulk_demo_btn)
        
        reg_layout.addRow("", buttons_layout)
        
        self.tab_widget.addTab(reg_widget, "Registration")

    def setup_schedule_tab(self):
        schedule_widget = QWidget()
        schedule_layout = QVBoxLayout(schedule_widget)
        
        # Add date selection
        date_widget = QWidget()
        date_layout = QHBoxLayout(date_widget)
        
        self.schedule_date = QDateEdit()
        self.schedule_date.setCalendarPopup(True)
        self.schedule_date.setDate(datetime.now().date())
        date_layout.addWidget(QLabel("Select Date:"))
        date_layout.addWidget(self.schedule_date)
        
        view_btn = QPushButton("View Schedule")
        view_btn.clicked.connect(self.load_day_schedule)
        date_layout.addWidget(view_btn)
        
        schedule_layout.addWidget(date_widget)
        
        # Add schedule table
        self.schedule_table = QTableWidget()
        self.schedule_table.setColumnCount(5)
        self.schedule_table.setHorizontalHeaderLabels([
            "Craftsman", "Shift Start", "Shift End", "Status", "Notes"
        ])
        schedule_layout.addWidget(self.schedule_table)
        
        # Add buttons for schedule management
        button_widget = QWidget()
        button_layout = QHBoxLayout(button_widget)
        
        add_shift_btn = QPushButton("Add Shift")
        add_shift_btn.clicked.connect(self.add_shift_dialog)
        edit_shift_btn = QPushButton("Edit Shift")
        edit_shift_btn.clicked.connect(lambda: self.edit_shift_dialog(self.schedule_table.currentRow()))
        delete_shift_btn = QPushButton("Delete Shift")
        delete_shift_btn.clicked.connect(lambda: self.delete_shift(self.schedule_table.currentRow()))
        
        button_layout.addWidget(add_shift_btn)
        button_layout.addWidget(edit_shift_btn)
        button_layout.addWidget(delete_shift_btn)
        
        schedule_layout.addWidget(button_widget)
        
        self.tab_widget.addTab(schedule_widget, "Schedule")
        
        # Load initial schedule
        self.load_day_schedule()

    def setup_reports_tab(self):
        reports_widget = QWidget()
        layout = QVBoxLayout(reports_widget)
        
        # Create craftsman selection
        selection_layout = QHBoxLayout()
        self.report_craftsman = QComboBox()
        self.report_craftsman.currentIndexChanged.connect(self.load_craftsman_reports)
        selection_layout.addWidget(QLabel("Select Craftsman:"))
        selection_layout.addWidget(self.report_craftsman)
        layout.addLayout(selection_layout)
        
        # Create tab widget for different report types
        self.reports_tab_widget = QTabWidget()
        layout.addWidget(self.reports_tab_widget)
        
        # Setup report tabs
        self.setup_performance_report_tab()
        self.setup_skills_report_tab()
        self.setup_training_report_tab()
        self.setup_workload_report_tab()
        
        # Add export button
        export_btn = QPushButton("Export Reports")
        export_btn.clicked.connect(self.export_reports)
        layout.addWidget(export_btn)
        
        self.tab_widget.addTab(reports_widget, "Reports")
        self.load_craftsmen_for_reports()

    def setup_teams_tab(self):
        teams_widget = QWidget()
        layout = QVBoxLayout(teams_widget)
        
        # Split view: Teams list on left, members on right
        splitter = QSplitter(Qt.Horizontal)
        layout.addWidget(splitter)
        
        # Teams list
        teams_list_widget = QWidget()
        teams_list_layout = QVBoxLayout(teams_list_widget)
        
        # Teams table
        self.teams_table = QTableWidget()
        self.teams_table.setColumnCount(3)
        self.teams_table.setHorizontalHeaderLabels([
            "Team Name", "Team Leader", "Description"
        ])
        
        # Set column widths
        self.teams_table.setColumnWidth(0, 150)  # Team Name
        self.teams_table.setColumnWidth(1, 150)  # Team Leader
        self.teams_table.setColumnWidth(2, 300)  # Description
        
        # Make table stretch to fill available space
        self.teams_table.horizontalHeader().setStretchLastSection(True)
        self.teams_table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        self.teams_table.itemSelectionChanged.connect(self.load_team_members)
        teams_list_layout.addWidget(self.teams_table)
        
        # Team management buttons
        team_buttons = QHBoxLayout()
        add_team_btn = QPushButton("Create Team")
        add_team_btn.clicked.connect(self.create_team_dialog)
        edit_team_btn = QPushButton("Edit Team")
        edit_team_btn.clicked.connect(lambda: self.edit_team_dialog(self.teams_table.currentRow()))
        team_buttons.addWidget(add_team_btn)
        team_buttons.addWidget(edit_team_btn)
        teams_list_layout.addLayout(team_buttons)
        
        # Members list
        members_widget = QWidget()
        members_layout = QVBoxLayout(members_widget)
        
        self.members_table = QTableWidget()
        self.members_table.setColumnCount(4)
        self.members_table.setHorizontalHeaderLabels([
            "Name", "Specialization", "Role", "Joined Date"
        ])
        
        # Set column widths
        self.members_table.setColumnWidth(0, 150)  # Name
        self.members_table.setColumnWidth(1, 120)  # Specialization
        self.members_table.setColumnWidth(2, 100)  # Role
        self.members_table.setColumnWidth(3, 100)  # Joined Date
        
        # Make table stretch to fill available space
        self.members_table.horizontalHeader().setStretchLastSection(True)
        self.members_table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        members_layout.addWidget(self.members_table)
        
        # Member management buttons
        member_buttons = QHBoxLayout()
        add_member_btn = QPushButton("Add Member")
        add_member_btn.clicked.connect(self.add_team_member_dialog)
        remove_member_btn = QPushButton("Remove Member")
        remove_member_btn.clicked.connect(self.remove_team_member)
        member_buttons.addWidget(add_member_btn)
        member_buttons.addWidget(remove_member_btn)
        members_layout.addLayout(member_buttons)
        
        # Add to splitter
        splitter.addWidget(teams_list_widget)
        splitter.addWidget(members_widget)
        
        # Set initial splitter sizes (40% for teams, 60% for members)
        splitter.setSizes([400, 600])
        
        self.tab_widget.addTab(teams_widget, "Teams")
        self.load_teams()

    def setup_menu_bar(self):
        """Setup the menu bar with various reporting options"""
        menu_bar = self.menuBar()
        menu_bar.setStyleSheet("""
            QMenuBar {
                background-color: #2a2a2a;
                color: #e0e0e0;
                border-bottom: 1px solid #3a3a3a;
            }
            QMenuBar::item:selected {
                background-color: #3a3a3a;
            }
            QMenu {
                background-color: #2a2a2a;
                color: #e0e0e0;
                border: 1px solid #3a3a3a;
            }
            QMenu::item:selected {
                background-color: #3a3a3a;
            }
        """)

        # Reports menu
        reports_menu = menu_bar.addMenu("Reports")
        
        # Individual reports
        individual_menu = reports_menu.addMenu("Individual Reports")
        complete_report = individual_menu.addAction("Complete Craftsman Report")
        complete_report.triggered.connect(self.generate_complete_craftsman_report)
        
        performance_report = individual_menu.addAction("Performance Report")
        performance_report.triggered.connect(lambda: self.generate_craftsman_report("performance"))
        
        skills_report = individual_menu.addAction("Skills & Certifications Report")
        skills_report.triggered.connect(lambda: self.generate_craftsman_report("skills"))
        
        training_report = individual_menu.addAction("Training Report")
        training_report.triggered.connect(lambda: self.generate_craftsman_report("training"))
        
        # Team reports
        team_menu = reports_menu.addMenu("Team Reports")
        team_summary = team_menu.addAction("Team Summary Report")
        team_summary.triggered.connect(self.generate_team_report)
        
        # Export menu
        export_menu = menu_bar.addMenu("Export")
        export_all = export_menu.addAction("Export All Data")
        export_all.triggered.connect(self.export_all_data)
        
        export_menu.addSeparator()
        export_skills = export_menu.addAction("Export Skills Matrix")
        export_skills.triggered.connect(lambda: self.export_specific_data("skills"))
        export_training = export_menu.addAction("Export Training Records")
        export_training.triggered.connect(lambda: self.export_specific_data("training"))
        export_schedule = export_menu.addAction("Export Schedule")
        export_schedule.triggered.connect(lambda: self.export_specific_data("schedule"))

    def generate_complete_craftsman_report(self):
        """Generate a comprehensive report for the selected craftsman"""
        # Get selected craftsman data
        selected_data = self.craftsmen_cards.get_selected_data()
        
        if not selected_data:
            QMessageBox.warning(self, "Warning", "Please select a craftsman first!")
            return
        
        # Get craftsman ID from the selected data
        craftsman_id = selected_data.get('craftsman_id') or selected_data.get('employee_id')

        try:
            # Use the new reporting module to generate the report
            from reporting import create_craftsman_report, open_containing_folder, open_report_file
            
            # Generate the report
            report_path = create_craftsman_report(self.db_manager, craftsman_id, "complete")
            
            if report_path:
                # Show success message with file path
                msg = QMessageBox(self)
                msg.setIcon(QMessageBox.Information)
                msg.setWindowTitle("Report Generated")
                msg.setText("Report generated successfully!")
                msg.setInformativeText(f"The report has been saved to:\n{report_path}")
                
                # Add button to open containing folder
                open_folder_button = msg.addButton("Open Folder", QMessageBox.ActionRole)
                open_report_button = msg.addButton("Open Report", QMessageBox.ActionRole)
                msg.addButton(QMessageBox.Ok)
                
                result = msg.exec()
                
                # Handle button clicks
                if msg.clickedButton() == open_folder_button:
                    open_containing_folder(report_path)
                elif msg.clickedButton() == open_report_button:
                    open_report_file(report_path)
            else:
                QMessageBox.warning(self, "Warning", "Failed to generate report!")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to generate report: {str(e)}")

    def generate_craftsman_report(self, report_type):
        """Generate specific type of craftsman report"""
        # Get selected craftsman data
        selected_data = self.craftsmen_cards.get_selected_data()
        
        if not selected_data:
            QMessageBox.warning(self, "Warning", "Please select a craftsman first!")
            return
        
        # Get craftsman ID from the selected data
        craftsman_id = selected_data.get('craftsman_id') or selected_data.get('employee_id')
        
        try:
            # Use the new reporting module to generate the report
            from reporting import create_craftsman_report, open_containing_folder, open_report_file
            
            # Generate the report
            report_path = create_craftsman_report(self.db_manager, craftsman_id, report_type)
            
            if report_path:
                # Show success message with file path
                msg = QMessageBox(self)
                msg.setIcon(QMessageBox.Information)
                msg.setWindowTitle("Report Generated")
                msg.setText("Report generated successfully!")
                msg.setInformativeText(f"The report has been saved to:\n{report_path}")
                
                # Add button to open containing folder
                open_folder_button = msg.addButton("Open Folder", QMessageBox.ActionRole)
                open_report_button = msg.addButton("Open Report", QMessageBox.ActionRole)
                msg.addButton(QMessageBox.Ok)
                
                result = msg.exec()
                
                # Handle button clicks
                if msg.clickedButton() == open_folder_button:
                    open_containing_folder(report_path)
                elif msg.clickedButton() == open_report_button:
                    open_report_file(report_path)
            else:
                QMessageBox.warning(self, "Warning", "Failed to generate report!")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to generate report: {str(e)}")

    def generate_team_report(self):
        """Generate a summary report for the selected team"""
        current_row = self.teams_table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Warning", "Please select a team first!")
            return

        team_name = self.teams_table.item(current_row, 0).text()
        
        try:
            # Use the new reporting module to generate the report
            from reporting import create_team_report, open_containing_folder, open_report_file
            
            # Generate the report
            report_path = create_team_report(self.db_manager, team_name)
            
            if report_path:
                # Show success message with file path
                msg = QMessageBox(self)
                msg.setIcon(QMessageBox.Information)
                msg.setWindowTitle("Report Generated")
                msg.setText("Team report generated successfully!")
                msg.setInformativeText(f"The report has been saved to:\n{report_path}")
                
                # Add button to open containing folder
                open_folder_button = msg.addButton("Open Folder", QMessageBox.ActionRole)
                open_report_button = msg.addButton("Open Report", QMessageBox.ActionRole)
                msg.addButton(QMessageBox.Ok)
                
                result = msg.exec()
                
                # Handle button clicks
                if msg.clickedButton() == open_folder_button:
                    open_containing_folder(report_path)
                elif msg.clickedButton() == open_report_button:
                    open_report_file(report_path)
            else:
                QMessageBox.warning(self, "Warning", "Failed to generate team report!")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to generate team report: {str(e)}")

    def check_page_break(self, current_y, needed_space, margin, printer):
        """Check if we need a new page and return the new y position"""
        page_rect = printer.pageRect(QPrinter.Unit.DevicePixel)
        if current_y + needed_space > page_rect.height() - margin:
            printer.newPage()
            return margin
        return current_y

    def open_containing_folder(self, file_path):
        """Open the folder containing the file in the system's file explorer"""
        import platform
        import subprocess
        
        try:
            if platform.system() == "Windows":
                subprocess.run(['explorer', '/select,', file_path])
            elif platform.system() == "Darwin":  # macOS
                subprocess.run(['open', '-R', file_path])
            else:  # Linux and other Unix-like
                subprocess.run(['xdg-open', os.path.dirname(file_path)])
        except Exception as e:
            QMessageBox.warning(
                self,
                "Warning",
                f"Could not open folder: {str(e)}"
            )

    def register_craftsman(self):
        data = {
            'employee_id': self.emp_id.text(),
            'first_name': self.first_name.text(),
            'last_name': self.last_name.text(),
            'phone': self.phone.text(),
            'email': self.email.text(),
            'specialization': self.specialization.currentText(),
            'experience_level': self.experience.currentText(),
            'hire_date': self.hire_date.date().toPython(),
            'status': 'Active'
        }
        
        if self.db_manager.register_craftsman(data):
            QMessageBox.information(self, "Success", "Craftsman registered successfully!")
            self.load_craftsmen()
            # Clear fields
            self.emp_id.clear()
            self.first_name.clear()
            self.last_name.clear()
            self.phone.clear()
            self.email.clear()
        else:
            QMessageBox.warning(self, "Error", "Failed to register craftsman!")

    def load_craftsmen(self):
        craftsmen = self.db_manager.get_all_craftsmen()
        
        # Keep the existing table code for compatibility
        self.craftsmen_table.setRowCount(len(craftsmen))
        
        for row, craftsman in enumerate(craftsmen):
            self.craftsmen_table.setItem(row, 0, QTableWidgetItem(craftsman['employee_id']))
            self.craftsmen_table.setItem(row, 1, QTableWidgetItem(
                f"{craftsman['first_name']} {craftsman['last_name']}"
            ))
            self.craftsmen_table.setItem(row, 2, QTableWidgetItem(craftsman['specialization']))
            self.craftsmen_table.setItem(row, 3, QTableWidgetItem(craftsman['experience_level']))
            self.craftsmen_table.setItem(row, 4, QTableWidgetItem(craftsman['phone']))
            self.craftsmen_table.setItem(row, 5, QTableWidgetItem(craftsman['email']))
            self.craftsmen_table.setItem(row, 6, QTableWidgetItem(craftsman['status']))
            self.craftsmen_table.setItem(row, 7, QTableWidgetItem(str(craftsman['hire_date'])))
        
        # Prepare data for card view
        card_data = []
        for craftsman in craftsmen:
            card_item = {
                'craftsman_id': craftsman['craftsman_id'],
                'employee_id': craftsman['employee_id'],
                'full_name': f"{craftsman['first_name']} {craftsman['last_name']}",
                'first_name': craftsman['first_name'],
                'last_name': craftsman['last_name'],
                'specialization': craftsman['specialization'],
                'experience_level': craftsman['experience_level'],
                'phone': craftsman['phone'],
                'email': craftsman['email'],
                'status': craftsman['status'],
                'hire_date': str(craftsman['hire_date'])
            }
            card_data.append(card_item)
        
        # Update card view
        self.craftsmen_cards.set_data(card_data)

    def search_craftsmen(self):
        try:
            # Get search criteria
            search_text = self.search_name.text().strip().lower()
            specialization = self.search_specialization.currentText()
            experience = self.search_experience.currentText()
            status = self.search_status.currentText()
            
            # Define filter function for card view
            def filter_func(craftsman):
                # Check if any field contains the search text
                if search_text:
                    found = False
                    # Search through all text fields
                    searchable_fields = [
                        'full_name', 'employee_id', 'specialization', 
                        'experience_level', 'phone', 'email', 'status'
                    ]
                    for field in searchable_fields:
                        if field in craftsman and str(craftsman[field]).lower().find(search_text) != -1:
                            found = True
                            break
                    if not found:
                        return False
                
                # Apply specialization filter
                if specialization != "All Specializations" and specialization != craftsman['specialization']:
                    return False
                
                # Apply experience filter
                if experience != "All Experience Levels" and experience != craftsman['experience_level']:
                    return False
                
                # Apply status filter
                if status != "All Status" and status != craftsman['status']:
                    return False
                
                return True
            
            # Apply filter to card view
            self.craftsmen_cards.filter_data(filter_func)
            
            # Keep the table filtering for compatibility
            for row in range(self.craftsmen_table.rowCount()):
                show_row = True
                
                # Search in all columns
                if search_text:
                    found = False
                    for col in range(self.craftsmen_table.columnCount()):
                        item = self.craftsmen_table.item(row, col)
                        if item and search_text in item.text().lower():
                            found = True
                            break
                    if not found:
                        show_row = False
                
                # Apply other filters
                row_specialization = self.craftsmen_table.item(row, 2).text()
                row_experience = self.craftsmen_table.item(row, 3).text()
                row_status = self.craftsmen_table.item(row, 6).text()
                
                if specialization != "All Specializations" and specialization != row_specialization:
                    show_row = False
                if experience != "All Experience Levels" and experience != row_experience:
                    show_row = False
                if status != "All Status" and status != row_status:
                    show_row = False
                
                # Show/hide row
                self.craftsmen_table.setRowHidden(row, not show_row)
            
            # Count visible rows
            visible_rows = sum(1 for row in range(self.craftsmen_table.rowCount()) 
                             if not self.craftsmen_table.isRowHidden(row))
        except Exception as e:
            QMessageBox.warning(
                self,
                "Search Error",
                f"An error occurred while searching: {str(e)}"
            )

    def show_craftsman_details(self, data):
        """Show details dialog for a craftsman"""
        # Now this will only show a read-only view of the craftsman details
        if isinstance(data, dict):
            craftsman_id = data.get('craftsman_id') or data.get('employee_id')
        else:
            row = data.row()
            craftsman_id = self.craftsmen_table.item(row, 0).text()
        
        # Create a read-only version of the details dialog
        dialog = CraftsmanDetailsDialog(craftsman_id, self.db_manager, self, read_only=True)
        dialog.exec_()

    def edit_craftsman(self, data):
        """Show edit dialog for a craftsman"""
        # Get the employee_id instead of craftsman_id
        employee_id = data.get('employee_id')
        if not employee_id:
            # If somehow we don't have employee_id, try to get it from the database using craftsman_id
            craftsman = self.db_manager.get_craftsman_by_id(data.get('craftsman_id'))
            if craftsman:
                employee_id = craftsman['employee_id']
            else:
                QMessageBox.warning(self, "Error", "Could not find craftsman details!")
                return
            
        dialog = CraftsmanDetailsDialog(employee_id, self.db_manager, self)
        if dialog.exec_():  # If dialog is accepted (closed with success)
            # Refresh the craftsmen list to show updated data
            self.load_craftsmen()

    def add_shift_dialog(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Add Shift")
        layout = QFormLayout(dialog)
        
        # Create input fields
        craftsman_combo = QComboBox()
        craftsmen = self.db_manager.get_all_craftsmen()
        for craftsman in craftsmen:
            craftsman_combo.addItem(
                f"{craftsman['first_name']} {craftsman['last_name']}",
                craftsman['craftsman_id']
            )
        
        shift_start = QDateEdit()
        shift_start.setDisplayFormat("HH:mm")
        shift_start.setCalendarPopup(True)
        
        shift_end = QDateEdit()
        shift_end.setDisplayFormat("HH:mm")
        shift_end.setCalendarPopup(True)
        
        status = QComboBox()
        status.addItems(["Scheduled", "On Duty", "Completed", "Absent"])
        
        notes = QLineEdit()
        
        # Add fields to layout
        layout.addRow("Craftsman:", craftsman_combo)
        layout.addRow("Shift Start:", shift_start)
        layout.addRow("Shift End:", shift_end)
        layout.addRow("Status:", status)
        layout.addRow("Notes:", notes)
        
        # Add buttons
        buttons = QHBoxLayout()
        save_btn = QPushButton("Save")
        cancel_btn = QPushButton("Cancel")
        buttons.addWidget(save_btn)
        buttons.addWidget(cancel_btn)
        layout.addRow("", buttons)
        
        # Connect buttons
        save_btn.clicked.connect(lambda: self.save_shift({
            'craftsman_id': craftsman_combo.currentData(),
            'date': self.schedule_date.date().toPython(),
            'shift_start': shift_start.time().toString(),
            'shift_end': shift_end.time().toString(),
            'status': status.currentText(),
            'notes': notes.text()
        }, dialog))
        cancel_btn.clicked.connect(dialog.reject)
        
        dialog.exec_()

    def save_shift(self, data, dialog):
        if self.db_manager.add_craftsman_schedule(data):
            QMessageBox.information(self, "Success", "Shift added successfully!")
            self.load_day_schedule()
            dialog.accept()
        else:
            QMessageBox.warning(self, "Error", "Failed to add shift!")

    def load_day_schedule(self):
        date = self.schedule_date.date().toPython()
        schedule = self.db_manager.get_day_schedule(date)
        self.schedule_table.setRowCount(len(schedule))
        
        for row, shift in enumerate(schedule):
            craftsman = self.db_manager.get_craftsman_by_id(shift['craftsman_id'])
            self.schedule_table.setItem(row, 0, QTableWidgetItem(
                f"{craftsman['first_name']} {craftsman['last_name']}"
            ))
            self.schedule_table.setItem(row, 1, QTableWidgetItem(str(shift['shift_start'])))
            self.schedule_table.setItem(row, 2, QTableWidgetItem(str(shift['shift_end'])))
            self.schedule_table.setItem(row, 3, QTableWidgetItem(shift['status']))
            self.schedule_table.setItem(row, 4, QTableWidgetItem(shift['notes']))

    def fill_demo_data(self):
        demo_data = DemoDataGenerator.generate_craftsman_data()
        
        self.emp_id.setText(demo_data['employee_id'])
        self.first_name.setText(demo_data['first_name'])
        self.last_name.setText(demo_data['last_name'])
        self.phone.setText(demo_data['phone'])
        self.email.setText(demo_data['email'])
        self.specialization.setCurrentText(demo_data['specialization'])
        self.experience.setCurrentText(demo_data['experience_level'])
        self.hire_date.setDate(demo_data['hire_date'])

    def add_bulk_demo_data(self):
        success_count = 0
        for _ in range(10):
            demo_data = DemoDataGenerator.generate_craftsman_data()
            if self.db_manager.register_craftsman(demo_data):
                success_count += 1
        
        self.load_craftsmen()
        QMessageBox.information(
            self,
            "Bulk Demo Data",
            f"Successfully added {success_count} demo craftsmen!"
        )

    def create_team_dialog(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Create New Team")
        layout = QFormLayout(dialog)
        
        # Create input fields
        team_name = QLineEdit()
        team_leader = QComboBox()
        craftsmen = self.db_manager.get_all_craftsmen()
        for craftsman in craftsmen:
            team_leader.addItem(
                f"{craftsman['first_name']} {craftsman['last_name']}",
                craftsman['craftsman_id']
            )
        description = QTextEdit()
        
        # Add fields to layout
        layout.addRow("Team Name:", team_name)
        layout.addRow("Team Leader:", team_leader)
        layout.addRow("Description:", description)
        
        # Add buttons
        buttons = QHBoxLayout()
        save_btn = QPushButton("Create")
        cancel_btn = QPushButton("Cancel")
        buttons.addWidget(save_btn)
        buttons.addWidget(cancel_btn)
        layout.addRow("", buttons)
        
        # Connect buttons
        save_btn.clicked.connect(lambda: self.save_team({
            'team_name': team_name.text(),
            'team_leader_id': team_leader.currentData(),
            'description': description.toPlainText()
        }, dialog))
        cancel_btn.clicked.connect(dialog.reject)
        
        dialog.exec()

    def save_team(self, data, dialog):
        if self.db_manager.create_team(data):
            QMessageBox.information(self, "Success", "Team created successfully!")
            self.load_teams()
            dialog.accept()
        else:
            QMessageBox.warning(self, "Error", "Failed to create team!")

    def load_teams(self):
        teams = self.db_manager.get_all_teams()
        self.teams_table.setRowCount(len(teams))
        
        for row, team in enumerate(teams):
            self.teams_table.setItem(row, 0, QTableWidgetItem(team['team_name']))
            
            # Format team leader name
            leader_name = "Not Assigned"
            if team.get('first_name') and team.get('last_name'):
                leader_name = f"{team['first_name']} {team['last_name']}"
            self.teams_table.setItem(row, 1, QTableWidgetItem(leader_name))
            
            self.teams_table.setItem(row, 2, QTableWidgetItem(team.get('description', '')))

    def load_team_members(self):
        """Load members for the selected team"""
        current_row = self.teams_table.currentRow()
        if current_row < 0:
            return
        
        # Get the team name from the selected row
        team_name = self.teams_table.item(current_row, 0).text()
        
        # First get the team_id from the team_name
        connection = self.db_manager.connect()
        cursor = connection.cursor(dictionary=True)
        
        try:
            cursor.execute("""
                SELECT team_id FROM craftsmen_teams 
                WHERE team_name = %s
            """, (team_name,))
            
            result = cursor.fetchone()
            if not result:
                print(f"Could not find team ID for: {team_name}")
                return
            
            team_id = result['team_id']
            
            # Now get the members using the team_id
            members = self.db_manager.get_team_members(team_id)
            self.members_table.setRowCount(len(members))
            
            for row, member in enumerate(members):
                self.members_table.setItem(row, 0, QTableWidgetItem(
                    f"{member['first_name']} {member['last_name']}"
                ))
                self.members_table.setItem(row, 1, QTableWidgetItem(member['specialization']))
                self.members_table.setItem(row, 2, QTableWidgetItem(member['role']))
                self.members_table.setItem(row, 3, QTableWidgetItem(str(member['joined_date'])))
        except Exception as e:
            print(f"Error loading team members: {e}")
        finally:
            self.db_manager.close(connection)

    def add_team_member_dialog(self):
        """Open dialog to add a team member"""
        # First check if a team is selected
        current_row = self.teams_table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Warning", "Please select a team first!")
            return
        
        # Get the team name from the selected row
        team_name = self.teams_table.item(current_row, 0).text()
        
        dialog = QDialog(self)
        dialog.setWindowTitle("Add Team Member")
        layout = QFormLayout(dialog)
        
        # Create craftsman selection
        craftsman_combo = QComboBox()
        craftsmen = self.db_manager.get_all_craftsmen()
        for craftsman in craftsmen:
            craftsman_combo.addItem(
                f"{craftsman['first_name']} {craftsman['last_name']}",
                craftsman['craftsman_id']  # Store craftsman_id as item data
            )
        
        # Create role selection
        role_combo = QComboBox()
        role_combo.addItems(["Member", "Lead", "Specialist", "Trainee"])
        
        # Add fields to layout
        layout.addRow("Craftsman:", craftsman_combo)
        layout.addRow("Role:", role_combo)
        
        # Add buttons
        buttons = QHBoxLayout()
        add_btn = QPushButton("Add Member")
        cancel_btn = QPushButton("Cancel")
        buttons.addWidget(add_btn)
        buttons.addWidget(cancel_btn)
        layout.addRow("", buttons)
        
        # Connect buttons
        add_btn.clicked.connect(lambda: self.add_member_to_team(
            team_name,
            craftsman_combo.currentData(),  # Get the craftsman_id from item data
            role_combo.currentText(),
            dialog
        ))
        cancel_btn.clicked.connect(dialog.reject)
        
        dialog.exec()

    def add_member_to_team(self, team_name, craftsman_id, role, dialog):
        """Add member to the selected team"""
        if self.db_manager.add_team_member(team_name, craftsman_id, role):
            QMessageBox.information(self, "Success", "Team member added successfully!")
            dialog.accept()
            
            # Refresh the members table to show the new member
            current_row = self.teams_table.currentRow()
            if current_row >= 0:
                self.load_team_members()
        else:
            QMessageBox.warning(self, "Error", "Failed to add team member!")

    def remove_team_member(self):
        """Remove selected member from the team"""
        current_team_row = self.teams_table.currentRow()
        current_member_row = self.members_table.currentRow()
        
        if current_team_row < 0:
            QMessageBox.warning(self, "Error", "Please select a team first!")
            return
        
        if current_member_row < 0:
            QMessageBox.warning(self, "Error", "Please select a member to remove!")
            return
        
        team_name = self.teams_table.item(current_team_row, 0).text()
        member_name = self.members_table.item(current_member_row, 0).text()
        
        # Confirm deletion
        reply = QMessageBox.question(
            self,
            "Confirm Removal",
            f"Are you sure you want to remove {member_name} from {team_name}?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            if self.db_manager.remove_team_member(team_name, member_name):
                QMessageBox.information(self, "Success", "Team member removed successfully!")
                self.load_team_members()  # Refresh the members list
            else:
                QMessageBox.warning(self, "Error", "Failed to remove team member!")

    def setup_performance_report_tab(self):
        performance_widget = QWidget()
        layout = QVBoxLayout(performance_widget)
        
        # Performance metrics table
        self.performance_table = QTableWidget()
        self.performance_table.setColumnCount(4)
        self.performance_table.setHorizontalHeaderLabels([
            "Metric", "Last Month", "Last 3 Months", "Last Year"
        ])
        layout.addWidget(self.performance_table)
        
        # Performance chart placeholder
        chart_label = QLabel("Performance Trend Chart")
        chart_label.setAlignment(Qt.AlignCenter)
        chart_label.setStyleSheet("background-color: #f0f0f0; padding: 20px;")
        layout.addWidget(chart_label)
        
        self.reports_tab_widget.addTab(performance_widget, "Performance")

    def setup_skills_report_tab(self):
        skills_widget = QWidget()
        layout = QVBoxLayout(skills_widget)
        
        # Skills summary table
        self.skills_summary_table = QTableWidget()
        self.skills_summary_table.setColumnCount(4)
        self.skills_summary_table.setHorizontalHeaderLabels([
            "Skill Category", "Current Level", "Certifications", "Expiring Soon"
        ])
        layout.addWidget(self.skills_summary_table)
        
        # Skills development chart placeholder
        chart_label = QLabel("Skills Development Timeline")
        chart_label.setAlignment(Qt.AlignCenter)
        chart_label.setStyleSheet("background-color: #f0f0f0; padding: 20px;")
        layout.addWidget(chart_label)
        
        self.reports_tab_widget.addTab(skills_widget, "Skills Analysis")

    def setup_training_report_tab(self):
        training_widget = QWidget()
        layout = QVBoxLayout(training_widget)
        
        # Training summary table
        self.training_summary_table = QTableWidget()
        self.training_summary_table.setColumnCount(4)
        self.training_summary_table.setHorizontalHeaderLabels([
            "Training Type", "Completed", "In Progress", "Required"
        ])
        layout.addWidget(self.training_summary_table)
        
        # Training completion chart placeholder
        chart_label = QLabel("Training Completion Status")
        chart_label.setAlignment(Qt.AlignCenter)
        chart_label.setStyleSheet("background-color: #f0f0f0; padding: 20px;")
        layout.addWidget(chart_label)
        
        self.reports_tab_widget.addTab(training_widget, "Training Status")

    def setup_workload_report_tab(self):
        workload_widget = QWidget()
        layout = QVBoxLayout(workload_widget)
        
        # Time period selection
        period_layout = QHBoxLayout()
        self.workload_period = QComboBox()
        self.workload_period.addItems(["Last Week", "Last Month", "Last Quarter", "Last Year"])
        self.workload_period.currentIndexChanged.connect(self.update_workload_report)
        period_layout.addWidget(QLabel("Time Period:"))
        period_layout.addWidget(self.workload_period)
        layout.addLayout(period_layout)
        
        # Workload statistics table
        self.workload_table = QTableWidget()
        self.workload_table.setColumnCount(4)
        self.workload_table.setHorizontalHeaderLabels([
            "Category", "Tasks Completed", "Hours Worked", "Efficiency Rate"
        ])
        layout.addWidget(self.workload_table)
        
        # Workload distribution chart placeholder
        chart_label = QLabel("Workload Distribution")
        chart_label.setAlignment(Qt.AlignCenter)
        chart_label.setStyleSheet("background-color: #f0f0f0; padding: 20px;")
        layout.addWidget(chart_label)
        
        self.reports_tab_widget.addTab(workload_widget, "Workload Analysis")

    def load_craftsmen_for_reports(self):
        craftsmen = self.db_manager.get_all_craftsmen()
        self.report_craftsman.clear()
        for craftsman in craftsmen:
            self.report_craftsman.addItem(
                f"{craftsman['first_name']} {craftsman['last_name']}",
                craftsman['craftsman_id']
            )

    def load_craftsman_reports(self):
        craftsman_id = self.report_craftsman.currentData()
        if not craftsman_id:
            return
        
        self.load_performance_report(craftsman_id)
        self.load_skills_report(craftsman_id)
        self.load_training_report(craftsman_id)
        self.update_workload_report()

    def load_performance_report(self, craftsman_id):
        # Get performance data from database
        performance_data = self.db_manager.get_craftsman_performance(craftsman_id)
        self.performance_table.setRowCount(4)
        
        metrics = [
            ("Tasks Completed", "count"),
            ("Average Performance Rating", "rating"),
            ("On-Time Completion Rate", "percentage"),
            ("Quality Score", "rating")
        ]
        
        for row, (metric, type_) in enumerate(metrics):
            self.performance_table.setItem(row, 0, QTableWidgetItem(metric))
            for col, period in enumerate(['month', 'quarter', 'year']):
                value = performance_data.get(f"{period}_{type_}", "N/A")
                if type_ == "rating":
                    value = f"{value:.1f}" if isinstance(value, (int, float)) else value
                elif type_ == "percentage":
                    value = f"{value}%" if isinstance(value, (int, float)) else value
                self.performance_table.setItem(row, col + 1, QTableWidgetItem(str(value)))

    def load_skills_report(self, craftsman_id):
        # Get skills data from database
        skills_data = self.db_manager.get_craftsman_skills_summary(craftsman_id)
        self.skills_summary_table.setRowCount(len(skills_data))
        
        for row, skill in enumerate(skills_data):
            self.skills_summary_table.setItem(row, 0, QTableWidgetItem(skill['category']))
            self.skills_summary_table.setItem(row, 1, QTableWidgetItem(skill['level']))
            self.skills_summary_table.setItem(row, 2, QTableWidgetItem(str(skill['cert_count'])))
            self.skills_summary_table.setItem(row, 3, QTableWidgetItem(str(skill['expiring'])))

    def load_training_report(self, craftsman_id):
        # Get training data from database
        training_data = self.db_manager.get_craftsman_training_summary(craftsman_id)
        self.training_summary_table.setRowCount(len(training_data))
        
        for row, training in enumerate(training_data):
            self.training_summary_table.setItem(row, 0, QTableWidgetItem(training['type']))
            self.training_summary_table.setItem(row, 1, QTableWidgetItem(str(training['completed'])))
            self.training_summary_table.setItem(row, 2, QTableWidgetItem(str(training['in_progress'])))
            self.training_summary_table.setItem(row, 3, QTableWidgetItem(str(training['required'])))

    def update_workload_report(self):
        craftsman_id = self.report_craftsman.currentData()
        if not craftsman_id:
            return
        
        period = self.workload_period.currentText()
        workload_data = self.db_manager.get_craftsman_workload(craftsman_id, period)
        self.workload_table.setRowCount(len(workload_data))
        
        for row, category in enumerate(workload_data):
            self.workload_table.setItem(row, 0, QTableWidgetItem(category['name']))
            self.workload_table.setItem(row, 1, QTableWidgetItem(str(category['tasks'])))
            self.workload_table.setItem(row, 2, QTableWidgetItem(f"{category['hours']:.1f}"))
            self.workload_table.setItem(row, 3, QTableWidgetItem(f"{category['efficiency']:.1f}%"))

    def export_reports(self):
        craftsman_id = self.report_craftsman.currentData()
        if not craftsman_id:
            return
        
        try:
            # Export reports to CSV files
            self.db_manager.export_craftsman_reports(craftsman_id)
            QMessageBox.information(self, "Success", "Reports exported successfully!")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to export reports: {str(e)}")

    def export_all_data(self):
        """Export all craftsmen data to JSON files"""
        try:
            # Create export directory
            export_dir = os.path.join(os.path.expanduser("~"), "Craftsmen_Exports")
            os.makedirs(export_dir, exist_ok=True)
            
            # Get all craftsmen
            craftsmen = self.db_manager.get_all_craftsmen()
            
            # Create timestamp for filename
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            
            # Export data for each craftsman
            exported_files = []
            for craftsman in craftsmen:
                # Gather all data for the craftsman
                data = {
                    'basic_info': craftsman,
                    'skills': self.db_manager.get_craftsman_skills(craftsman['craftsman_id']),
                    'training': self.db_manager.get_craftsman_training(craftsman['craftsman_id']),
                    'work_history': self.db_manager.get_craftsman_work_history(craftsman['craftsman_id']),
                    'schedule': self.db_manager.get_craftsman_schedule(craftsman['craftsman_id']),
                    'performance': self.db_manager.get_craftsman_performance(craftsman['craftsman_id'])
                }
                
                # Generate filename
                filename = f"craftsman_{craftsman['employee_id']}_{timestamp}.json"
                file_path = os.path.join(export_dir, filename)
                
                # Save to file
                with open(file_path, 'w') as f:
                    json.dump(data, f, indent=4, default=str)
                
                exported_files.append(file_path)
            
            # Export teams data
            teams_data = {
                'teams': self.db_manager.get_all_teams(),
                'members': {}
            }
            
            for team in teams_data['teams']:
                teams_data['members'][team['team_name']] = self.db_manager.get_team_members(team['team_id'])
            
            teams_file = os.path.join(export_dir, f"teams_data_{timestamp}.json")
            with open(teams_file, 'w') as f:
                json.dump(teams_data, f, indent=4, default=str)
            
            exported_files.append(teams_file)
            
            # Show success message with option to open folder
            msg = QMessageBox(self)
            msg.setIcon(QMessageBox.Information)
            msg.setWindowTitle("Export Complete")
            msg.setText("All data exported successfully!")
            msg.setInformativeText(f"Files have been saved to:\n{export_dir}")
            
            open_folder_button = msg.addButton("Open Folder", QMessageBox.ActionRole)
            msg.addButton(QMessageBox.Ok)
            
            msg.exec()
            
            if msg.clickedButton() == open_folder_button:
                self.open_containing_folder(export_dir)

        except Exception as e:
            QMessageBox.critical(
                self,
                "Export Error",
                f"Failed to export data: {str(e)}"
            )

    def export_specific_data(self, data_type):
        """Export specific type of data (skills, training, schedule)"""
        try:
            # Create export directory
            export_dir = os.path.join(os.path.expanduser("~"), "Craftsmen_Exports")
            os.makedirs(export_dir, exist_ok=True)
            
            # Get all craftsmen
            craftsmen = self.db_manager.get_all_craftsmen()
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            
            # Prepare data based on type
            export_data = {}
            for craftsman in craftsmen:
                craftsman_name = f"{craftsman['first_name']} {craftsman['last_name']}"
                
                if data_type == "skills":
                    export_data[craftsman_name] = self.db_manager.get_craftsman_skills(craftsman['craftsman_id'])
                elif data_type == "training":
                    export_data[craftsman_name] = self.db_manager.get_craftsman_training(craftsman['craftsman_id'])
                elif data_type == "schedule":
                    export_data[craftsman_name] = self.db_manager.get_craftsman_schedule(craftsman['craftsman_id'])
            
            # Generate filename
            filename = f"{data_type}_export_{timestamp}.json"
            file_path = os.path.join(export_dir, filename)
            
            # Save to file
            with open(file_path, 'w') as f:
                json.dump(export_data, f, indent=4, default=str)
            
            # Show success message
            msg = QMessageBox(self)
            msg.setIcon(QMessageBox.Information)
            msg.setWindowTitle("Export Complete")
            msg.setText(f"{data_type.capitalize()} data exported successfully!")
            msg.setInformativeText(f"File has been saved to:\n{file_path}")
            
            open_folder_button = msg.addButton("Open Folder", QMessageBox.ActionRole)
            msg.addButton(QMessageBox.Ok)
            
            msg.exec()
            
            if msg.clickedButton() == open_folder_button:
                self.open_containing_folder(file_path)

        except Exception as e:
            QMessageBox.critical(
                self,
                "Export Error",
                f"Failed to export {data_type} data: {str(e)}"
            )

    def edit_team_dialog(self, row):
        """Open dialog to edit an existing team"""
        if row < 0:
            QMessageBox.warning(self, "Warning", "Please select a team to edit!")
            return
        
        # Get the team data from the selected row
        team_name = self.teams_table.item(row, 0).text()
        team_leader = self.teams_table.item(row, 1).text()
        description = self.teams_table.item(row, 2).text()
        
        # Create dialog
        dialog = QDialog(self)
        dialog.setWindowTitle("Edit Team")
        layout = QFormLayout(dialog)
        
        # Create input fields
        name_field = QLineEdit(team_name)
        
        # Create leader selection
        leader_combo = QComboBox()
        craftsmen = self.db_manager.get_all_craftsmen()
        selected_index = 0
        for i, craftsman in enumerate(craftsmen):
            full_name = f"{craftsman['first_name']} {craftsman['last_name']}"
            leader_combo.addItem(full_name, craftsman['craftsman_id'])
            if full_name == team_leader:
                selected_index = i
        
        leader_combo.setCurrentIndex(selected_index)
        
        description_field = QTextEdit()
        description_field.setText(description)
        description_field.setMinimumHeight(100)
        
        # Add fields to layout
        layout.addRow("Team Name:", name_field)
        layout.addRow("Team Leader:", leader_combo)
        layout.addRow("Description:", description_field)
        
        # Add buttons
        buttons = QHBoxLayout()
        save_btn = QPushButton("Save Changes")
        cancel_btn = QPushButton("Cancel")
        buttons.addWidget(save_btn)
        buttons.addWidget(cancel_btn)
        layout.addRow("", buttons)
        
        # Connect buttons
        save_btn.clicked.connect(lambda: self.update_team(
            team_name,  # Original team name for identification
            name_field.text(),
            leader_combo.currentData(),
            description_field.toPlainText(),
            dialog
        ))
        cancel_btn.clicked.connect(dialog.reject)
        
        dialog.exec()

    def update_team(self, original_name, new_name, leader_id, description, dialog):
        """Update an existing team"""
        # Create data dictionary
        data = {
            'original_name': original_name,
            'team_name': new_name,
            'team_leader_id': leader_id,
            'description': description
        }
        
        # Add method to db_manager to update team
        if self.db_manager.update_team(data):
            QMessageBox.information(self, "Success", "Team updated successfully!")
            self.load_teams()  # Refresh the teams list
            dialog.accept()
        else:
            QMessageBox.warning(self, "Error", "Failed to update team!")

    def handle_craftsman_click(self, data):
        """Handle single click on craftsman card - just select the card"""
        # The selection is handled internally by the CardTableWidget
        pass


class DemoDataGenerator:
    first_names = [
        "John", "James", "Michael", "William", "David", "Robert", "Thomas", "Richard",
        "Charles", "Joseph", "Christopher", "Daniel", "Matthew", "Anthony", "Donald",
        "Mark", "Paul", "Steven", "Andrew", "Kenneth"
    ]
    
    last_names = [
        "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis",
        "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson",
        "Thomas", "Taylor", "Moore", "Jackson", "Martin"
    ]
    
    domains = ["gmail.com", "yahoo.com", "hotmail.com", "outlook.com"]
    
    specializations = ["Mechanical", "Electrical", "HVAC", "Plumbing"]
    
    experience_levels = ["Entry Level", "Intermediate", "Expert", "Master"]
    
    @classmethod
    def generate_phone(cls):
        return f"+1-{random.randint(200, 999)}-{random.randint(100, 999)}-{random.randint(1000, 9999)}"
    
    @classmethod
    def generate_employee_id(cls):
        return f"EMP{random.randint(1000, 9999)}"
    
    @classmethod
    def generate_hire_date(cls):
        # Generate a date between 5 years ago and today
        days_ago = random.randint(0, 5 * 365)
        return datetime.now().date() - timedelta(days=days_ago)
    
    @classmethod
    def generate_craftsman_data(cls):
        first_name = random.choice(cls.first_names)
        last_name = random.choice(cls.last_names)
        email = f"{first_name.lower()}.{last_name.lower()}@{random.choice(cls.domains)}"
        
        return {
            'employee_id': cls.generate_employee_id(),
            'first_name': first_name,
            'last_name': last_name,
            'phone': cls.generate_phone(),
            'email': email,
            'specialization': random.choice(cls.specializations),
            'experience_level': random.choice(cls.experience_levels),
            'hire_date': cls.generate_hire_date(),
            'status': 'Active'
        }

