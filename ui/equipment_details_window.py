from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                              QTabWidget, QLabel, QLineEdit, QTextEdit, 
                              QPushButton, QFormLayout, QScrollArea, QFrame,
                              QTableWidget, QTableWidgetItem, QDateEdit,
                              QSpinBox, QComboBox, QMessageBox, QDialog, QMenu,
                              QFileDialog, QMenuBar, QStatusBar, QSizePolicy)
from PySide6.QtCore import Qt, QDate, QPoint
from PySide6.QtPrintSupport import QPrinter, QPrintDialog
from PySide6.QtGui import QAction, QCursor, QPainter
import json
from datetime import datetime, timedelta
import csv
import os

class ItemDetailDialog(QDialog):
    """Reusable dialog for viewing detailed information from any table row"""
    def __init__(self, data: dict, title: str = "Details", parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setMinimumSize(800, 600)
        
        # Create main layout
        main_layout = QVBoxLayout(self)
        
        # Create toolbar
        toolbar = QHBoxLayout()
        
        # Export buttons
        export_pdf_btn = QPushButton("Export PDF")
        export_csv_btn = QPushButton("Export CSV")
        export_pdf_btn.clicked.connect(self.export_to_pdf)
        export_csv_btn.clicked.connect(self.export_to_csv)
        
        toolbar.addWidget(export_pdf_btn)
        toolbar.addWidget(export_csv_btn)
        toolbar.addStretch()
        
        main_layout.addLayout(toolbar)
        
        # Create scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("""
            QScrollArea {
                background-color: #1e1e1e;
                border: none;
            }
        """)
        
        # Content widget
        content_widget = QWidget()
        self.form_layout = QFormLayout(content_widget)
        self.form_layout.setSpacing(10)
        
        # Add all data fields
        self.field_widgets = {}
        for label, value in data.items():
            label_widget = QLabel(label)
            label_widget.setStyleSheet("""
                color: #e0e0e0;
                font-weight: bold;
                font-size: 12px;
            """)
            
            if isinstance(value, str) and len(value) > 100:
                value_widget = QTextEdit()
                value_widget.setPlainText(str(value))
                value_widget.setReadOnly(True)
                value_widget.setMinimumHeight(100)
            else:
                value_widget = QLabel(str(value))
                value_widget.setWordWrap(True)
            
            value_widget.setStyleSheet("""
                QLabel, QTextEdit {
                    color: #e0e0e0;
                    background-color: #2a2a2a;
                    padding: 5px;
                    border: 1px solid #3a3a3a;
                    border-radius: 3px;
                }
            """)
            
            self.field_widgets[label] = value_widget
            self.form_layout.addRow(label_widget, value_widget)
        
        scroll.setWidget(content_widget)
        main_layout.addWidget(scroll)
        
        # Close button
        close_button = QPushButton("Close")
        close_button.clicked.connect(self.accept)
        close_button.setStyleSheet("""
            QPushButton {
                background-color: #2b5b84;
                border: 1px solid #3a7ab7;
                padding: 8px 16px;
                color: #ffffff;
            }
            QPushButton:hover {
                background-color: #3a7ab7;
            }
        """)
        main_layout.addWidget(close_button)

    def export_to_pdf(self):
        file_name, _ = QFileDialog.getSaveFileName(
            self,
            "Export PDF",
            f"{self.windowTitle()}.pdf",
            "PDF Files (*.pdf)"
        )
        
        if file_name:
            printer = QPrinter(QPrinter.PrinterMode.HighResolution)
            printer.setOutputFormat(QPrinter.OutputFormat.PdfFormat)
            printer.setOutputFileName(file_name)
            
            painter = QPainter(printer)
            font = painter.font()
            font.setPointSize(10)
            painter.setFont(font)
            
            # Get page metrics
            page_rect = printer.pageRect(QPrinter.Unit.DevicePixel)
            margin = 100  # Left margin
            content_width = page_rect.width() - (margin * 2)  # Available width for text
            line_height = painter.fontMetrics().height() + 5  # Space between lines
            
            # Draw title
            title_font = painter.font()
            title_font.setPointSize(14)
            title_font.setBold(True)
            painter.setFont(title_font)
            
            y_position = margin
            painter.drawText(
                margin, y_position, 
                f"Details Report - {self.windowTitle()}"
            )
            
            # Reset font for content
            font.setPointSize(10)
            font.setBold(False)
            painter.setFont(font)
            
            # Add some space after title
            y_position += line_height * 2

            # Draw content
            for label, widget in self.field_widgets.items():
                if isinstance(widget, QTextEdit):
                    value = widget.toPlainText()
                else:
                    value = widget.text()
                
                # Draw label
                font.setBold(True)
                painter.setFont(font)
                painter.drawText(margin, y_position, f"{label}:")
                y_position += line_height
                
                # Draw value with word wrap
                font.setBold(False)
                painter.setFont(font)
                
                # Handle multiline text
                if len(value) > 0:
                    remaining_text = value
                    while remaining_text:
                        # Calculate how many characters can fit in one line
                        metrics = painter.fontMetrics()
                        chars_that_fit = 0
                        for i in range(len(remaining_text)):
                            if metrics.horizontalAdvance(remaining_text[:i+1]) > content_width:
                                chars_that_fit = i
                                break
                        
                        if chars_that_fit == 0:  # Entire text fits
                            chars_that_fit = len(remaining_text)
                        
                        # Find last space before cut-off to avoid word breaks
                        if chars_that_fit < len(remaining_text):
                            last_space = remaining_text.rfind(' ', 0, chars_that_fit)
                            if last_space != -1:
                                chars_that_fit = last_space
                        
                        # Draw line
                        line = remaining_text[:chars_that_fit].strip()
                        if line:
                            painter.drawText(margin + 20, y_position, line)
                            y_position += line_height
                        
                        # Update remaining text
                        remaining_text = remaining_text[chars_that_fit:].strip()
                else:
                    # Handle empty values
                    painter.drawText(margin + 20, y_position, "-")
                    y_position += line_height
                
                # Add space between fields
                y_position += line_height
                
                # Check if we need a new page
                if y_position > page_rect.height() - margin:
                    printer.newPage()
                    y_position = margin
            
            painter.end()
            
            QMessageBox.information(
                self,
                "Success",
                f"PDF exported successfully to {file_name}"
            )

    def export_to_csv(self):
        file_name, _ = QFileDialog.getSaveFileName(
            self,
            "Export CSV",
            f"{self.windowTitle()}.csv",
            "CSV Files (*.csv)"
        )
        
        if file_name:
            try:
                with open(file_name, 'w', newline='') as csvfile:
                    writer = csv.writer(csvfile)
                    writer.writerow(['Field', 'Value'])
                    
                    for label, widget in self.field_widgets.items():
                        if isinstance(widget, QTextEdit):
                            value = widget.toPlainText()
                        else:
                            value = widget.text()
                        writer.writerow([label, value])
                
                QMessageBox.information(
                    self,
                    "Success",
                    f"CSV exported successfully to {file_name}"
                )
            
            except Exception as e:
                QMessageBox.critical(
                    self,
                    "Error",
                    f"Failed to export CSV: {str(e)}"
                )

class EquipmentDetailsWindow(QMainWindow):
    def __init__(self, equipment_id, db_manager, parent=None):
        super().__init__(parent)
        self.equipment_id = equipment_id
        self.db_manager = db_manager
        self.equipment_data = self.db_manager.get_equipment_by_id(equipment_id)
        
        self.setWindowTitle(f"Equipment Details - {self.equipment_data['equipment_name']}")
        
        # Create central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)
        
        # Create tab widget
        self.tab_widget = QTabWidget()
        self.tab_widget.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #3a3a3a;
                background-color: #1e1e1e;
            }
            QTabBar::tab {
                background-color: #2a2a2a;
                color: #e0e0e0;
                padding: 8px 20px;
                border: 1px solid #3a3a3a;
                border-bottom: none;
            }
            QTabBar::tab:selected {
                background-color: #1e1e1e;
                border-bottom: none;
            }
            QTabBar::tab:hover {
                background-color: #3a3a3a;
            }
        """)
        
        # Add tabs
        self.setup_registry_tab()
        self.setup_technical_info_tab()
        self.setup_history_tab()
        self.setup_maintenance_tab()
        self.setup_tools_tab()
        self.setup_safety_tab()
        self.setup_additional_info_tab()
        
        # Give the tab widget a stretch factor to take available space
        main_layout.addWidget(self.tab_widget, 1)
        
        # Create menu bar
        self.setup_menu_bar()
        
        # Add status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        
        # Set size policy for central widget to ensure it expands properly
        central_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

    def create_scroll_area(self):
        """Create a standardized scroll area with a widget and layout"""
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
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
        
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(15)
        
        # Set size policy to ensure the widget expands properly
        widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        scroll.setWidget(widget)
        return scroll, widget, layout

    def setup_registry_tab(self):
        """Basic equipment registration information"""
        scroll, widget, layout = self.create_scroll_area()
        
        # Create form layout for registry info
        form_layout = QFormLayout()
        form_layout.setSpacing(10)
        
        # Add all basic equipment fields
        fields = [
            ("Equipment ID", str(self.equipment_data['equipment_id'])),
            ("Part Number", self.equipment_data['part_number']),
            ("Equipment Name", self.equipment_data['equipment_name']),
            ("Manufacturer", self.equipment_data.get('manufacturer', '')),
            ("Model", self.equipment_data.get('model', '')),
            ("Serial Number", self.equipment_data.get('serial_number', '')),
            ("Location", self.equipment_data.get('location', '')),
            ("Installation Date", str(self.equipment_data.get('installation_date', ''))),
            ("Status", self.equipment_data.get('status', '')),
        ]
        
        for label, value in fields:
            label_widget = QLabel(label)
            value_widget = QLabel(value)
            label_widget.setStyleSheet("color: #e0e0e0; font-weight: bold;")
            value_widget.setStyleSheet("color: #e0e0e0;")
            form_layout.addRow(label_widget, value_widget)
        
        layout.addLayout(form_layout)
        layout.addStretch()
        
        self.tab_widget.addTab(scroll, "Registry Info")

    def setup_technical_info_tab(self):
        """Technical specifications and parameters"""
        scroll, widget, layout = self.create_scroll_area()
        
        # Add form for technical specifications
        form_layout = QFormLayout()
        
        # Load existing technical info
        tech_info = self.db_manager.get_technical_info(self.equipment_id)
        
        # Technical specification fields
        self.tech_fields = {}
        specs = [
            ("Power Requirements", "power_requirements"),
            ("Operating Temperature", "operating_temperature"),
            ("Weight", "weight"),
            ("Dimensions", "dimensions"),
            ("Operating Pressure", "operating_pressure"),
            ("Capacity", "capacity"),
            ("Precision/Accuracy", "precision_accuracy"),
        ]
        
        for label, field_name in specs:
            field = QLineEdit()
            if tech_info:
                field.setText(tech_info.get(field_name, ''))
            field.setStyleSheet("""
                QLineEdit {
                    background-color: #2a2a2a;
                    border: 1px solid #3a3a3a;
                    padding: 5px;
                    color: #e0e0e0;
                }
            """)
            self.tech_fields[field_name] = field
            form_layout.addRow(QLabel(label), field)
        
        # Add specifications text area
        specs_label = QLabel("Detailed Specifications")
        specs_label.setStyleSheet("color: #e0e0e0; font-weight: bold; margin-top: 15px;")
        layout.addWidget(specs_label)
        
        self.specs_text = QTextEdit()
        if tech_info:
            self.specs_text.setText(tech_info.get('detailed_specifications', ''))
        self.specs_text.setStyleSheet("""
            QTextEdit {
                background-color: #2a2a2a;
                border: 1px solid #3a3a3a;
                color: #e0e0e0;
            }
        """)
        layout.addWidget(self.specs_text)
        
        # Add save button
        save_button = QPushButton("Save Technical Info")
        save_button.clicked.connect(self.save_technical_info)
        save_button.setStyleSheet("""
            QPushButton {
                background-color: #2b5b84;
                border: 1px solid #3a7ab7;
                padding: 8px 16px;
                color: #ffffff;
            }
            QPushButton:hover {
                background-color: #3a7ab7;
            }
        """)
        layout.addWidget(save_button)
        
        layout.addLayout(form_layout)
        self.tab_widget.addTab(scroll, "Technical Info")

    def save_technical_info(self):
        """Save technical information to database"""
        data = {
            field_name: field.text()
            for field_name, field in self.tech_fields.items()
        }
        data['detailed_specifications'] = self.specs_text.toPlainText()
        
        try:
            self.db_manager.save_technical_info(self.equipment_id, data)
            QMessageBox.information(
                self,
                "Success",
                "Technical information saved successfully!"
            )
        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                f"Failed to save technical information: {str(e)}"
            )

    def setup_table_context_menu(self, table: QTableWidget):
        """Set up context menu for any table"""
        table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        table.customContextMenuRequested.connect(
            lambda pos, t=table: self.show_table_context_menu(pos, t)
        )

    def show_table_context_menu(self, position: QPoint, table: QTableWidget):
        """Show context menu for table rows"""
        row = table.rowAt(position.y())
        
        if row >= 0:  # If a valid row was clicked
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
            """)

            # View details action
            view_action = menu.addAction("View Details")
            view_action.triggered.connect(
                lambda: self.show_row_details(table, row)
            )
            
            menu.exec(table.viewport().mapToGlobal(position))

    def show_row_details(self, table: QTableWidget, row: int):
        """Show details for the selected row"""
        data = {}
        
        # Get column headers and standardize them
        headers = []
        header_mapping = {
            # History table mappings
            "Date": "date",
            "Type": "event_type",
            "Description": "description",
            "Performed By": "performed_by",
            "Notes": "notes",
            
            # Maintenance table mappings
            "Task": "task_name",
            "Frequency": "frequency",
            "Last Done": "last_done",
            "Next Due": "next_due",
            "Procedure": "maintenance_procedure",
            "Required Parts": "required_parts",
            
            # Tools table mappings
            "Tool Name": "tool_name",
            "Specification": "specification",
            "Purpose": "purpose",
            "Location": "location"
        }
        
        # Get standardized headers
        for col in range(table.columnCount()):
            header = table.horizontalHeaderItem(col).text()
            standardized_header = header_mapping.get(header, header)
            headers.append(standardized_header)
        
        # Get row data with standardized field names
        for col in range(table.columnCount()):
            item = table.item(row, col)
            if item:
                data[headers[col]] = item.text()
        
        # Add any additional data based on table type
        if table == self.history_table:
            # Get the date and description to uniquely identify the entry
            entry_date = data.get('date')
            description = data.get('description')
            full_entry = self.db_manager.get_history_entry_by_date_desc(
                self.equipment_id, entry_date, description
            )
            if full_entry:
                # Remove duplicate fields before updating
                for key in data.keys():
                    if key in full_entry:
                        del full_entry[key]
                data.update(full_entry)
        
        elif table == self.maintenance_table:
            task_name = data.get('task_name')
            full_task = self.db_manager.get_maintenance_task_by_name(
                self.equipment_id, task_name
            )
            if full_task:
                # Remove duplicate fields before updating
                for key in data.keys():
                    if key in full_task:
                        del full_task[key]
                data.update(full_task)
        
        elif table == self.tools_table:
            tool_name = data.get('tool_name')
            full_tool = self.db_manager.get_special_tool_by_name(
                self.equipment_id, tool_name
            )
            if full_tool:
                # Remove duplicate fields before updating
                for key in data.keys():
                    if key in full_tool:
                        del full_tool[key]
                data.update(full_tool)
        
        # Clean up the data by removing any None values and standardizing field names
        cleaned_data = {}
        for key, value in data.items():
            if value is not None:
                # Convert any technical field names to user-friendly display names
                display_name = next(
                    (k for k, v in header_mapping.items() if v == key),
                    key.replace('_', ' ').title()
                )
                cleaned_data[display_name] = value
        
        # Show detail dialog
        dialog = ItemDetailDialog(cleaned_data, f"Details - {table.objectName()}", self)
        dialog.exec()

    def setup_history_tab(self):
        """Equipment usage and maintenance history"""
        scroll, widget, layout = self.create_scroll_area()
        
        # Add history table
        self.history_table = QTableWidget()
        self.history_table.setColumnCount(5)
        self.history_table.setHorizontalHeaderLabels([
            "Date", "Type", "Description", "Performed By", "Notes"
        ])
        
        # Set table to expand to fill available space
        self.history_table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.history_table.horizontalHeader().setStretchLastSection(True)

        # Set column widths - distribute space proportionally
        header = self.history_table.horizontalHeader()
        header.setSectionResizeMode(0, header.ResizeMode.ResizeToContents)  # Date
        header.setSectionResizeMode(1, header.ResizeMode.ResizeToContents)  # Type
        header.setSectionResizeMode(2, header.ResizeMode.Stretch)           # Description
        header.setSectionResizeMode(3, header.ResizeMode.ResizeToContents)  # Performed By
        header.setSectionResizeMode(4, header.ResizeMode.Stretch)           # Notes

        # Set alternating row colors and selection behavior
        self.history_table.setAlternatingRowColors(True)
        self.history_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.history_table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)

        self.history_table.setStyleSheet("""
            QTableWidget {
                background-color: #1e1e1e;
                alternate-background-color: #262626;
                color: #e0e0e0;
                gridline-color: #2a2a2a;
            }
            QHeaderView::section {
                background-color: #2a2a2a;
                color: #e0e0e0;
                padding: 5px;
                border: 1px solid #3a3a3a;
            }
        """)
        
        # Add new history entry section
        entry_form = QFormLayout()
        
        self.history_date = QDateEdit()
        self.history_date.setDate(QDate.currentDate())
        self.history_type = QComboBox()
        self.history_type.addItems(["Usage", "Maintenance", "Repair", "Calibration", "Other"])
        self.history_description = QLineEdit()
        self.history_performed_by = QLineEdit()
        self.history_notes = QTextEdit()
        self.history_notes.setMaximumHeight(100)
        
        entry_form.addRow("Date:", self.history_date)
        entry_form.addRow("Type:", self.history_type)
        entry_form.addRow("Description:", self.history_description)
        entry_form.addRow("Performed By:", self.history_performed_by)
        entry_form.addRow("Notes:", self.history_notes)
        
        add_history_button = QPushButton("Add History Entry")
        add_history_button.setStyleSheet("""
            QPushButton {
                background-color: #2b5b84;
                border: 1px solid #3a7ab7;
                padding: 8px 16px;
                color: #ffffff;
            }
            QPushButton:hover {
                background-color: #3a7ab7;
            }
        """)
        
        layout.addWidget(self.history_table)
        layout.addLayout(entry_form)
        layout.addWidget(add_history_button)
        
        # Style the input fields
        for widget in [self.history_date, self.history_type, self.history_description, 
                      self.history_performed_by, self.history_notes]:
            if isinstance(widget, (QLineEdit, QTextEdit)):
                widget.setStyleSheet("""
                    QLineEdit, QTextEdit {
                        background-color: #2a2a2a;
                        border: 1px solid #3a3a3a;
                        color: #e0e0e0;
                        padding: 5px;
                    }
                """)
            elif isinstance(widget, (QComboBox, QDateEdit)):
                widget.setStyleSheet("""
                    QComboBox, QDateEdit {
                        background-color: #2a2a2a;
                        border: 1px solid #3a3a3a;
                        color: #e0e0e0;
                        padding: 5px;
                    }
                    QComboBox::drop-down, QDateEdit::drop-down {
                        border: none;
                    }
                    QComboBox::down-arrow, QDateEdit::down-arrow {
                        background-color: #3a3a3a;
                    }
                """)

        # Connect the add history button
        add_history_button.clicked.connect(self.add_history_entry)
        
        # Load existing history
        self.load_history()
        
        # Set table name
        self.history_table.setObjectName("History")
        
        # Add context menu
        self.setup_table_context_menu(self.history_table)
        
        self.tab_widget.addTab(scroll, "History")

    def add_history_entry(self):
        """Add a new history entry"""
        data = {
            'date': self.history_date.date().toPython(),
            'event_type': self.history_type.currentText(),
            'description': self.history_description.text(),
            'performed_by': self.history_performed_by.text(),
            'notes': self.history_notes.toPlainText()
        }
        
        if not data['description']:
            QMessageBox.warning(self, "Validation Error", "Description is required!")
            return
            
        if self.db_manager.add_history_entry(self.equipment_id, data):
            self.load_history()
            # Clear the form
            self.history_description.clear()
            self.history_performed_by.clear()
            self.history_notes.clear()
            self.history_date.setDate(QDate.currentDate())
            QMessageBox.information(self, "Success", "History entry added successfully!")
        else:
            QMessageBox.critical(self, "Error", "Failed to add history entry!")

    def load_history(self):
        """Load history entries into the table"""
        # Get regular history entries
        history = self.db_manager.get_equipment_history(self.equipment_id)
        
        # Get maintenance schedule entries
        maintenance_history = self.db_manager.get_maintenance_schedule(self.equipment_id)
        
        # Convert maintenance tasks to history entries
        for task in maintenance_history:
            if task.get('last_done'):  # Only include tasks that have been done
                history.append({
                    'date': task['last_done'],
                    'event_type': 'Maintenance',
                    'description': f"Completed maintenance task: {task['task_name']}",
                    'performed_by': '',  # This information isn't stored in maintenance_schedule
                    'notes': f"Next due: {task['next_due']}. {task.get('maintenance_procedure', '')}",
                    'source_type': 'maintenance_task',
                    'source_id': task.get('task_id')
                })
        
        # Get completed work orders for this equipment
        completed_work_orders = self.db_manager.get_completed_work_orders_by_equipment(self.equipment_id)
        
        # Convert completed work orders to history entries
        for work_order in completed_work_orders:
            # Get craftsman name if available
            craftsman_name = 'Unknown'
            if work_order.get('craftsman_id'):
                craftsman = self.db_manager.get_craftsman_by_id(work_order['craftsman_id'])
                if craftsman:
                    craftsman_name = f"{craftsman.get('first_name', '')} {craftsman.get('last_name', '')}"
            
            # Get team name if available
            team_name = ''
            if work_order.get('team_id'):
                team = self.db_manager.get_team_by_id(work_order['team_id'])
                if team:
                    team_name = team.get('team_name', '')
            
            # Use team name if no craftsman assigned
            if craftsman_name == 'Unknown' and team_name:
                craftsman_name = f"Team: {team_name}"
            
            # Create history entry from work order
            history.append({
                'date': work_order.get('completed_date', work_order.get('last_modified')),
                'event_type': 'Work Order',
                'description': f"Completed work order: {work_order['title']} (ID: {work_order['work_order_id']})",
                'performed_by': craftsman_name,
                'notes': work_order.get('description', '') + '\n' + work_order.get('notes', ''),
                'source_type': 'work_order',
                'source_id': work_order['work_order_id']
            })
        
        # Sort combined history by date (newest first)
        history.sort(key=lambda x: x['date'] if isinstance(x['date'], datetime) else datetime.strptime(str(x['date']), '%Y-%m-%d'), reverse=True)
        
        # Store the history data for use in double-click handler
        self.history_data = history
        
        self.history_table.setRowCount(len(history))
        
        for row, entry in enumerate(history):
            self.history_table.setItem(row, 0, QTableWidgetItem(str(entry['date'])))
            self.history_table.setItem(row, 1, QTableWidgetItem(entry['event_type']))
            self.history_table.setItem(row, 2, QTableWidgetItem(entry['description']))
            self.history_table.setItem(row, 3, QTableWidgetItem(entry['performed_by']))
            self.history_table.setItem(row, 4, QTableWidgetItem(entry['notes']))
        
        # Connect double-click signal if not already connected
        try:
            self.history_table.cellDoubleClicked.disconnect()
        except:
            pass
        self.history_table.cellDoubleClicked.connect(self.show_history_details)

    def show_history_details(self, row, column):
        """Show details for the selected history entry"""
        if row < 0 or row >= len(self.history_data):
            return
        
        entry = self.history_data[row]
        source_type = entry.get('source_type', '')
        source_id = entry.get('source_id', None)
        
        if source_type == 'work_order' and source_id:
            # Get the full work order data
            work_order = self.db_manager.get_work_order_by_id(source_id)
            if work_order:
                # Format the data for display
                display_data = {
                    'Work Order ID': work_order['work_order_id'],
                    'Title': work_order['title'],
                    'Description': work_order['description'],
                    'Status': work_order['status'],
                    'Priority': work_order['priority'],
                    'Created Date': work_order['created_date'],
                    'Due Date': work_order['due_date'],
                    'Completed Date': work_order.get('completed_date', 'N/A'),
                    'Notes': work_order.get('notes', ''),
                }
                
                # Get craftsman name if available
                if work_order.get('craftsman_id'):
                    craftsman = self.db_manager.get_craftsman_by_id(work_order['craftsman_id'])
                    if craftsman:
                        display_data['Assigned To'] = f"{craftsman.get('first_name', '')} {craftsman.get('last_name', '')}"
                
                # Get team name if available
                if work_order.get('team_id'):
                    team = self.db_manager.get_team_by_id(work_order['team_id'])
                    if team:
                        display_data['Assigned Team'] = team.get('team_name', '')
                
                # Show the details dialog
                dialog = ItemDetailDialog(display_data, f"Work Order Details - {work_order['work_order_id']}", self)
                dialog.exec()
                
        elif source_type == 'maintenance_task' and source_id:
            # Get the full maintenance task data
            task = self.db_manager.get_maintenance_task_by_id(source_id)
            if task:
                # Format the data for display
                display_data = {
                    'Task ID': task['task_id'],
                    'Task Name': task['task_name'],
                    'Frequency': f"{task['frequency']} {task['frequency_unit']}",
                    'Last Done': task['last_done'],
                    'Next Due': task['next_due'],
                    'Maintenance Procedure': task['maintenance_procedure'],
                    'Required Parts': task['required_parts']
                }
                
                # Show the details dialog
                dialog = ItemDetailDialog(display_data, f"Maintenance Task Details - {task['task_name']}", self)
                dialog.exec()
                
        else:
            # Regular history entry
            display_data = {
                'Date': entry['date'],
                'Event Type': entry['event_type'],
                'Description': entry['description'],
                'Performed By': entry['performed_by'],
                'Notes': entry['notes']
            }
            
            # Show the details dialog
            dialog = ItemDetailDialog(display_data, "History Entry Details", self)
            dialog.exec()

    def setup_maintenance_tab(self):
        """Preventive maintenance schedule"""
        scroll, widget, layout = self.create_scroll_area()
        
        # Maintenance schedule table
        self.maintenance_table = QTableWidget()
        self.maintenance_table.setColumnCount(6)
        self.maintenance_table.setHorizontalHeaderLabels([
            "Task", "Frequency", "Last Done", "Next Due", "Procedure", "Required Parts"
        ])
        
        # Add new maintenance task section
        task_form = QFormLayout()
        
        self.maintenance_task = QLineEdit()
        self.maintenance_frequency = QSpinBox()
        self.maintenance_frequency_unit = QComboBox()
        self.maintenance_frequency_unit.addItems(["Days", "Weeks", "Months", "Years"])
        self.maintenance_procedure = QTextEdit()
        self.maintenance_parts = QLineEdit()
        
        freq_layout = QHBoxLayout()
        freq_layout.addWidget(self.maintenance_frequency)
        freq_layout.addWidget(self.maintenance_frequency_unit)
        
        task_form.addRow("Task:", self.maintenance_task)
        task_form.addRow("Frequency:", freq_layout)
        task_form.addRow("Procedure:", self.maintenance_procedure)
        task_form.addRow("Required Parts:", self.maintenance_parts)
        
        add_task_button = QPushButton("Add Maintenance Task")
        
        layout.addWidget(self.maintenance_table)
        layout.addLayout(task_form)
        layout.addWidget(add_task_button)
        
        # Style the input fields
        for widget in [self.maintenance_task, self.maintenance_frequency, 
                      self.maintenance_procedure, self.maintenance_parts]:
            if isinstance(widget, (QLineEdit, QTextEdit)):
                widget.setStyleSheet("""
                    QLineEdit, QTextEdit {
                        background-color: #2a2a2a;
                        border: 1px solid #3a3a3a;
                        color: #e0e0e0;
                        padding: 5px;
                    }
                """)

        # Connect the add task button
        add_task_button.clicked.connect(self.add_maintenance_task)
        
        # Load existing tasks
        self.load_maintenance_tasks()
        
        # Set table name
        self.maintenance_table.setObjectName("Maintenance")
        
        # Add context menu
        self.setup_table_context_menu(self.maintenance_table)
        
        self.tab_widget.addTab(scroll, "Maintenance Schedule")

    def add_maintenance_task(self):
        """Add a new maintenance task"""
        frequency = self.maintenance_frequency.value()
        unit = self.maintenance_frequency_unit.currentText()
        
        # Calculate next due date based on frequency
        last_done = datetime.now()
        if unit == "Days":
            next_due = last_done + timedelta(days=frequency)
        elif unit == "Weeks":
            next_due = last_done + timedelta(weeks=frequency)
        elif unit == "Months":
            next_due = last_done + timedelta(days=frequency * 30)
        else:  # Years
            next_due = last_done + timedelta(days=frequency * 365)
        
        data = {
            'task_name': self.maintenance_task.text(),
            'frequency': frequency,
            'frequency_unit': unit,
            'last_done': last_done.date(),
            'next_due': next_due.date(),
            'maintenance_procedure': self.maintenance_procedure.toPlainText(),
            'required_parts': self.maintenance_parts.text()
        }
        
        if not data['task_name']:
            QMessageBox.warning(self, "Validation Error", "Task name is required!")
            return
            
        if self.db_manager.add_maintenance_task(self.equipment_id, data):
            self.load_maintenance_tasks()
            # Clear the form
            self.maintenance_task.clear()
            self.maintenance_frequency.setValue(0)
            self.maintenance_procedure.clear()
            self.maintenance_parts.clear()
            QMessageBox.information(self, "Success", "Maintenance task added successfully!")
        else:
            QMessageBox.critical(self, "Error", "Failed to add maintenance task!")

    def load_maintenance_tasks(self):
        """Load maintenance tasks into the table"""
        tasks = self.db_manager.get_maintenance_schedule(self.equipment_id)
        self.maintenance_table.setRowCount(len(tasks))
        
        for row, task in enumerate(tasks):
            self.maintenance_table.setItem(row, 0, QTableWidgetItem(task['task_name']))
            self.maintenance_table.setItem(row, 1, QTableWidgetItem(
                f"{task['frequency']} {task['frequency_unit']}"
            ))
            self.maintenance_table.setItem(row, 2, QTableWidgetItem(str(task['last_done'])))
            self.maintenance_table.setItem(row, 3, QTableWidgetItem(str(task['next_due'])))
            self.maintenance_table.setItem(row, 4, QTableWidgetItem(task['maintenance_procedure']))
            self.maintenance_table.setItem(row, 5, QTableWidgetItem(task['required_parts']))

    def setup_tools_tab(self):
        """Special tools and equipment"""
        scroll, widget, layout = self.create_scroll_area()
        
        # Tools table
        self.tools_table = QTableWidget()
        self.tools_table.setColumnCount(4)
        self.tools_table.setHorizontalHeaderLabels([
            "Tool Name", "Specification", "Purpose", "Location"
        ])
        
        # Add new tool section
        tool_form = QFormLayout()
        
        self.tool_name = QLineEdit()
        self.tool_spec = QLineEdit()
        self.tool_purpose = QLineEdit()
        self.tool_location = QLineEdit()
        
        tool_form.addRow("Tool Name:", self.tool_name)
        tool_form.addRow("Specification:", self.tool_spec)
        tool_form.addRow("Purpose:", self.tool_purpose)
        tool_form.addRow("Location:", self.tool_location)
        
        add_tool_button = QPushButton("Add Tool")
        
        layout.addWidget(self.tools_table)
        layout.addLayout(tool_form)
        layout.addWidget(add_tool_button)
        
        # Style the input fields
        for widget in [self.tool_name, self.tool_spec, self.tool_purpose, self.tool_location]:
            widget.setStyleSheet("""
                QLineEdit {
                    background-color: #2a2a2a;
                    border: 1px solid #3a3a3a;
                    color: #e0e0e0;
                    padding: 5px;
                }
            """)

        # Connect the add tool button
        add_tool_button.clicked.connect(self.add_special_tool)
        
        # Load existing tools
        self.load_special_tools()
        
        # Set table name
        self.tools_table.setObjectName("Tools")
        
        # Add context menu
        self.setup_table_context_menu(self.tools_table)
        
        self.tab_widget.addTab(scroll, "Special Tools")

    def add_special_tool(self):
        """Add a new special tool"""
        data = {
            'tool_name': self.tool_name.text(),
            'specification': self.tool_spec.text(),
            'purpose': self.tool_purpose.text(),
            'location': self.tool_location.text()
        }
        
        if not data['tool_name']:
            QMessageBox.warning(self, "Validation Error", "Tool name is required!")
            return
            
        if self.db_manager.add_special_tool(self.equipment_id, data):
            self.load_special_tools()
            # Clear the form
            self.tool_name.clear()
            self.tool_spec.clear()
            self.tool_purpose.clear()
            self.tool_location.clear()
            QMessageBox.information(self, "Success", "Special tool added successfully!")
        else:
            QMessageBox.critical(self, "Error", "Failed to add special tool!")

    def load_special_tools(self):
        """Load special tools into the table"""
        tools = self.db_manager.get_special_tools(self.equipment_id)
        self.tools_table.setRowCount(len(tools))
        
        for row, tool in enumerate(tools):
            self.tools_table.setItem(row, 0, QTableWidgetItem(tool['tool_name']))
            self.tools_table.setItem(row, 1, QTableWidgetItem(tool['specification']))
            self.tools_table.setItem(row, 2, QTableWidgetItem(tool['purpose']))
            self.tools_table.setItem(row, 3, QTableWidgetItem(tool['location']))

    def setup_safety_tab(self):
        """Safety precautions and procedures"""
        scroll, widget, layout = self.create_scroll_area()
        
        # Safety categories
        categories = [
            ("Personal Protective Equipment (PPE)", QTextEdit()),
            ("Operating Precautions", QTextEdit()),
            ("Emergency Procedures", QTextEdit()),
            ("Hazardous Materials", QTextEdit()),
            ("Lock-out/Tag-out Procedures", QTextEdit()),
        ]
        
        for title, text_edit in categories:
            label = QLabel(title)
            label.setStyleSheet("color: #e0e0e0; font-weight: bold; margin-top: 10px;")
            layout.addWidget(label)
            layout.addWidget(text_edit)
        
        save_button = QPushButton("Save Safety Information")
        layout.addWidget(save_button)
        
        # Store references to text edits
        self.safety_fields = {
            'ppe_requirements': categories[0][1],
            'operating_precautions': categories[1][1],
            'emergency_procedures': categories[2][1],
            'hazardous_materials': categories[3][1],
            'lockout_procedures': categories[4][1]
        }
        
        # Style the text edits
        for text_edit in self.safety_fields.values():
            text_edit.setStyleSheet("""
                QTextEdit {
                    background-color: #2a2a2a;
                    border: 1px solid #3a3a3a;
                    color: #e0e0e0;
                    padding: 5px;
                }
            """)
        
        # Connect the save button
        save_button.clicked.connect(self.save_safety_info)
        
        # Load existing safety info
        self.load_safety_info()
        
        self.tab_widget.addTab(scroll, "Safety")

    def save_safety_info(self):
        """Save safety information"""
        data = {
            field: text_edit.toPlainText()
            for field, text_edit in self.safety_fields.items()
        }

        if self.db_manager.save_safety_info(self.equipment_id, data):
            QMessageBox.information(self, "Success", "Safety information saved successfully!")
        else:
            QMessageBox.critical(self, "Error", "Failed to save safety information!")

    def load_safety_info(self):
        """Load safety information"""
        safety_info = self.db_manager.get_safety_info(self.equipment_id)
        if safety_info:
            for field, text_edit in self.safety_fields.items():
                text_edit.setText(safety_info.get(field, ''))

    def setup_additional_info_tab(self):
        """Additional custom fields"""
        scroll, widget, layout = self.create_scroll_area()
        
        # Add custom fields section
        custom_fields_label = QLabel("Custom Fields")
        custom_fields_label.setStyleSheet("color: #e0e0e0; font-weight: bold;")
        layout.addWidget(custom_fields_label)
        
        # Custom fields container
        self.custom_fields_layout = QVBoxLayout()
        layout.addLayout(self.custom_fields_layout)
        
        # Add field button
        add_field_button = QPushButton("Add Custom Field")
        layout.addWidget(add_field_button)
        
        # Add stretch to push everything to the top
        layout.addStretch()
        
        self.tab_widget.addTab(scroll, "Additional Info")

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
        
        # General reports
        general_report = reports_menu.addAction("Complete Equipment Report")
        general_report.triggered.connect(self.generate_complete_report)
        
        reports_menu.addSeparator()
        
        # Technical reports submenu
        technical_menu = reports_menu.addMenu("Technical Reports")
        tech_specs = technical_menu.addAction("Technical Specifications")
        tech_specs.triggered.connect(lambda: self.generate_technical_report())
        performance = technical_menu.addAction("Performance History")
        performance.triggered.connect(lambda: self.generate_technical_report("performance"))
        calibration = technical_menu.addAction("Calibration History")
        calibration.triggered.connect(lambda: self.generate_technical_report("calibration"))
        
        # Maintenance reports submenu
        maintenance_menu = reports_menu.addMenu("Maintenance Reports")
        maint_schedule = maintenance_menu.addAction("Maintenance Schedule")
        maint_schedule.triggered.connect(lambda: self.generate_maintenance_report("schedule"))
        maint_history = maintenance_menu.addAction("Maintenance History")
        maint_history.triggered.connect(lambda: self.generate_maintenance_report("history"))
        upcoming_maint = maintenance_menu.addAction("Upcoming Maintenance")
        upcoming_maint.triggered.connect(lambda: self.generate_maintenance_report("upcoming"))
        overdue_maint = maintenance_menu.addAction("Overdue Maintenance")
        overdue_maint.triggered.connect(lambda: self.generate_maintenance_report("overdue"))
        
        # Safety reports submenu
        safety_menu = reports_menu.addMenu("Safety Reports")
        safety_procedures = safety_menu.addAction("Safety Procedures")
        safety_procedures.triggered.connect(lambda: self.generate_safety_report("procedures"))
        incident_history = safety_menu.addAction("Incident History")
        incident_history.triggered.connect(lambda: self.generate_safety_report("incidents"))
        
        reports_menu.addSeparator()
        
        # Custom reports
        custom_report = reports_menu.addAction("Custom Report...")
        custom_report.triggered.connect(self.generate_custom_report)
        
        # Export menu
        export_menu = menu_bar.addMenu("Export")
        
        export_all = export_menu.addAction("Export All Data")
        export_all.triggered.connect(self.export_all_data)
        
        export_menu.addSeparator()
        
        export_history = export_menu.addAction("Export History")
        export_history.triggered.connect(lambda: self.export_specific_data("history"))
        export_maintenance = export_menu.addAction("Export Maintenance Schedule")
        export_maintenance.triggered.connect(lambda: self.export_specific_data("maintenance"))
        export_tools = export_menu.addAction("Export Tools List")
        export_tools.triggered.connect(lambda: self.export_specific_data("tools"))
        
        # Tools menu
        tools_menu = menu_bar.addMenu("Tools")
        
        analyze_data = tools_menu.addAction("Analyze Maintenance Patterns")
        analyze_data.triggered.connect(self.analyze_maintenance_patterns)
        
        calculate_metrics = tools_menu.addAction("Calculate Performance Metrics")
        calculate_metrics.triggered.connect(self.calculate_performance_metrics)
        
        tools_menu.addSeparator()
        
        generate_qr = tools_menu.addAction("Generate Equipment QR Code")
        generate_qr.triggered.connect(self.generate_equipment_qr)

    def generate_complete_report(self):
        """Generate a comprehensive report of all equipment information"""
        try:
            # Use the new reporting module to generate the report
            from reporting import create_equipment_report, open_containing_folder, open_report_file
            
            # Generate the report
            report_path = create_equipment_report(self.db_manager, self.equipment_id, "complete")
            
            if report_path:
                # Show success message
                msg = QMessageBox(self)
                msg.setIcon(QMessageBox.Information)
                msg.setWindowTitle("Report Generated")
                msg.setText("Complete report generated successfully!")
                msg.setInformativeText(f"The report has been saved to:\n{report_path}")
                
                open_folder_button = msg.addButton("Open Folder", QMessageBox.ActionRole)
                open_report_button = msg.addButton("Open Report", QMessageBox.ActionRole)
                msg.addButton(QMessageBox.Ok)
                
                result = msg.exec()
                
                if msg.clickedButton() == open_folder_button:
                    open_containing_folder(report_path)
                elif msg.clickedButton() == open_report_button:
                    open_report_file(report_path)
                    
                self.status_bar.showMessage("Complete report generated successfully!", 5000)
            else:
                QMessageBox.critical(self, "Error", "Failed to generate report!")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to generate complete report: {str(e)}")

    def generate_technical_report(self, report_type="specs"):
        """Generate technical reports based on type"""
        try:
            # Use the new reporting module to generate the report
            from reporting import create_equipment_report, open_containing_folder, open_report_file
            
            # Generate the report
            report_path = create_equipment_report(self.db_manager, self.equipment_id, "technical")
            
            if report_path:
                # Show success message
                msg = QMessageBox(self)
                msg.setIcon(QMessageBox.Information)
                msg.setWindowTitle("Report Generated")
                msg.setText(f"Technical report ({report_type}) generated successfully!")
                msg.setInformativeText(f"The report has been saved to:\n{report_path}")
                
                open_folder_button = msg.addButton("Open Folder", QMessageBox.ActionRole)
                open_report_button = msg.addButton("Open Report", QMessageBox.ActionRole)
                msg.addButton(QMessageBox.Ok)
                
                result = msg.exec()
                
                if msg.clickedButton() == open_folder_button:
                    open_containing_folder(report_path)
                elif msg.clickedButton() == open_report_button:
                    open_report_file(report_path)
                    
                self.status_bar.showMessage(f"Technical report ({report_type}) generated successfully!", 5000)
            else:
                QMessageBox.critical(self, "Error", "Failed to generate report!")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to generate technical report: {str(e)}")

    def generate_maintenance_report(self, report_type):
        """Generate maintenance reports based on type"""
        try:
            # Use the new reporting module to generate the report
            from reporting import create_equipment_report, open_containing_folder, open_report_file
            
            # Generate the report
            report_path = create_equipment_report(self.db_manager, self.equipment_id, "maintenance")
            
            if report_path:
                # Show success message
                msg = QMessageBox(self)
                msg.setIcon(QMessageBox.Information)
                msg.setWindowTitle("Report Generated")
                msg.setText(f"Maintenance report ({report_type}) generated successfully!")
                msg.setInformativeText(f"The report has been saved to:\n{report_path}")
                
                open_folder_button = msg.addButton("Open Folder", QMessageBox.ActionRole)
                open_report_button = msg.addButton("Open Report", QMessageBox.ActionRole)
                msg.addButton(QMessageBox.Ok)
                
                result = msg.exec()
                
                if msg.clickedButton() == open_folder_button:
                    open_containing_folder(report_path)
                elif msg.clickedButton() == open_report_button:
                    open_report_file(report_path)
                    
                self.status_bar.showMessage(f"Maintenance report ({report_type}) generated successfully!", 5000)
            else:
                QMessageBox.critical(self, "Error", "Failed to generate report!")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to generate maintenance report: {str(e)}")

    def generate_safety_report(self, report_type):
        """Generate safety reports based on type"""
        try:
            # Use the new reporting module to generate the report
            from reporting import create_equipment_report, open_containing_folder, open_report_file
            
            # Generate the report
            report_path = create_equipment_report(self.db_manager, self.equipment_id, "safety")
            
            if report_path:
                # Show success message
                msg = QMessageBox(self)
                msg.setIcon(QMessageBox.Information)
                msg.setWindowTitle("Report Generated")
                msg.setText(f"Safety report ({report_type}) generated successfully!")
                msg.setInformativeText(f"The report has been saved to:\n{report_path}")
                
                open_folder_button = msg.addButton("Open Folder", QMessageBox.ActionRole)
                open_report_button = msg.addButton("Open Report", QMessageBox.ActionRole)
                msg.addButton(QMessageBox.Ok)
                
                result = msg.exec()
                
                if msg.clickedButton() == open_folder_button:
                    open_containing_folder(report_path)
                elif msg.clickedButton() == open_report_button:
                    open_report_file(report_path)
                    
                self.status_bar.showMessage(f"Safety report ({report_type}) generated successfully!", 5000)
            else:
                QMessageBox.critical(self, "Error", "Failed to generate report!")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to generate safety report: {str(e)}")

    def generate_custom_report(self):
        """Open dialog to create custom report"""
        try:
            # Use the new reporting module to generate the report
            from reporting import create_equipment_report, open_containing_folder, open_report_file
            
            # For now, just generate a complete report
            report_path = create_equipment_report(self.db_manager, self.equipment_id, "complete")
            
            if report_path:
                # Show success message
                msg = QMessageBox(self)
                msg.setIcon(QMessageBox.Information)
                msg.setWindowTitle("Report Generated")
                msg.setText("Custom report generated successfully!")
                msg.setInformativeText(f"The report has been saved to:\n{report_path}")
                
                open_folder_button = msg.addButton("Open Folder", QMessageBox.ActionRole)
                open_report_button = msg.addButton("Open Report", QMessageBox.ActionRole)
                msg.addButton(QMessageBox.Ok)
                
                result = msg.exec()
                
                if msg.clickedButton() == open_folder_button:
                    open_containing_folder(report_path)
                elif msg.clickedButton() == open_report_button:
                    open_report_file(report_path)
                    
                self.status_bar.showMessage("Custom report generated successfully!", 5000)
            else:
                QMessageBox.critical(self, "Error", "Failed to generate report!")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to generate custom report: {str(e)}")

    def export_all_data(self):
        """Export all equipment data to various formats"""
        try:
            # Create exports directory if it doesn't exist
            exports_dir = os.path.join(os.path.expanduser("~"), "Equipment_Exports")
            os.makedirs(exports_dir, exist_ok=True)
            
            # Create equipment-specific directory
            equipment_dir = os.path.join(
                exports_dir,
                f"{self.equipment_data['equipment_name']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            )
            os.makedirs(equipment_dir, exist_ok=True)
            
            # Export each type of data
            export_files = []
            for data_type in ["history", "maintenance", "tools"]:
                file_path = os.path.join(equipment_dir, f"{data_type}.csv")
                self.export_specific_data(data_type)
                export_files.append(file_path)
            
            # Export technical and safety info
            tech_info = self.db_manager.get_technical_info(self.equipment_id)
            safety_info = self.db_manager.get_safety_info(self.equipment_id)
            
            # Save as JSON for structured data
            with open(os.path.join(equipment_dir, "technical_info.json"), 'w') as f:
                json.dump(tech_info, f, indent=4)
            with open(os.path.join(equipment_dir, "safety_info.json"), 'w') as f:
                json.dump(safety_info, f, indent=4)
            
            # Show success message with directory path
            msg = QMessageBox(self)
            msg.setIcon(QMessageBox.Information)
            msg.setWindowTitle("Export Complete")
            msg.setText("All data exported successfully!")
            msg.setInformativeText(f"The files have been saved to:\n{equipment_dir}")
            
            # Add button to open containing folder
            open_folder_button = msg.addButton("Open Folder", QMessageBox.ActionRole)
            msg.addButton(QMessageBox.Ok)
            
            msg.exec()
            
            # Handle button click
            if msg.clickedButton() == open_folder_button:
                self.open_containing_folder(equipment_dir)
            
            # Update status bar
            self.status_bar.showMessage(f"All data exported to: {equipment_dir}", 5000)
            
        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                f"Failed to export all data: {str(e)}"
            )

    def export_specific_data(self, data_type):
        """Export specific type of data"""
        try:
            # Create exports directory if it doesn't exist
            exports_dir = os.path.join(os.path.expanduser("~"), "Equipment_Exports")
            os.makedirs(exports_dir, exist_ok=True)
            
            # Generate filename
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"{self.equipment_data['equipment_name']}_{data_type}_{timestamp}.csv"
            file_path = os.path.join(exports_dir, filename)
            
            # Get data based on type
            if data_type == "history":
                data = self.db_manager.get_equipment_history(self.equipment_id)
            elif data_type == "maintenance":
                data = self.db_manager.get_maintenance_schedule(self.equipment_id)
            elif data_type == "tools":
                data = self.db_manager.get_special_tools(self.equipment_id)
            else:
                raise ValueError(f"Unknown data type: {data_type}")
            
            # Export to CSV
            with open(file_path, 'w', newline='') as csvfile:
                if data and len(data) > 0:
                    writer = csv.DictWriter(csvfile, fieldnames=data[0].keys())
                    writer.writeheader()
                    writer.writerows(data)
            
            # Show success message with file path
            msg = QMessageBox(self)
            msg.setIcon(QMessageBox.Information)
            msg.setWindowTitle("Export Complete")
            msg.setText("Data exported successfully!")
            msg.setInformativeText(f"The file has been saved to:\n{file_path}")
            
            # Add button to open containing folder
            open_folder_button = msg.addButton("Open Folder", QMessageBox.ActionRole)
            msg.addButton(QMessageBox.Ok)
            
            msg.exec()
            
            # Handle button click
            if msg.clickedButton() == open_folder_button:
                self.open_containing_folder(file_path)
            
            # Update status bar
            self.status_bar.showMessage(f"Data exported to: {file_path}", 5000)
            
        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                f"Failed to export data: {str(e)}"
            )

    def analyze_maintenance_patterns(self):
        """Analyze maintenance patterns and generate insights"""
        # Implementation for maintenance pattern analysis
        pass

    def calculate_performance_metrics(self):
        """Calculate and display performance metrics"""
        # Implementation for performance metrics calculation
        pass

    def generate_equipment_qr(self):
        """Generate QR code for quick equipment identification"""
        # Implementation for QR code generation
        pass