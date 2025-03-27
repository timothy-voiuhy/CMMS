from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                              QLabel, QTableWidget, QTableWidgetItem, QDialog,
                              QTextEdit, QComboBox, QHeaderView, QSplitter,
                              QFrame, QTabWidget, QMessageBox, QMenu, QSizePolicy)
from PySide6.QtCore import Qt, Signal, QSize
from PySide6.QtGui import QIcon, QAction, QColor
from datetime import datetime
import webbrowser
import tempfile
import os

class NotificationCenter(QMainWindow):
    notification_count_changed = Signal(int)
    
    def __init__(self, notification_service, parent=None):
        super().__init__(parent)
        self.notification_service = notification_service
        self.setWindowTitle("Notification Center")
        self.resize(800, 600)  # Set a default size for the window
        
        # Create central widget
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        # Set up the UI
        self.setup_ui()
        
        # Load initial data
        self.refresh_notifications()
    
    def setup_ui(self):
        main_layout = QVBoxLayout(self.central_widget)
        
        # Header
        header_layout = QHBoxLayout()
        
        title_label = QLabel("Notification Center")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        
        self.status_filter = QComboBox()
        self.status_filter.addItems(["All", "Sent", "Failed", "Pending"])
        self.status_filter.currentTextChanged.connect(self.refresh_notifications)
        
        refresh_btn = QPushButton("Refresh")
        refresh_btn.clicked.connect(self.refresh_notifications)
        
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        header_layout.addWidget(QLabel("Filter:"))
        header_layout.addWidget(self.status_filter)
        header_layout.addWidget(refresh_btn)
        
        main_layout.addLayout(header_layout)
        
        # Notification table
        self.notification_table = QTableWidget()
        self.notification_table.setColumnCount(6)
        self.notification_table.setHorizontalHeaderLabels([
            "ID", "Type", "Recipient", "Subject", "Status", "Date"
        ])
        self.notification_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.notification_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.notification_table.doubleClicked.connect(self.view_notification)
        self.notification_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch)
        self.notification_table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.notification_table.customContextMenuRequested.connect(self.show_context_menu)
        
        main_layout.addWidget(self.notification_table, 1)
        
        # Button row
        button_layout = QHBoxLayout()
        
        view_btn = QPushButton("View Details")
        view_btn.clicked.connect(self.view_notification)
        
        retry_btn = QPushButton("Retry Failed")
        retry_btn.clicked.connect(self.retry_failed)
        
        export_btn = QPushButton("Export as HTML")
        export_btn.clicked.connect(self.export_as_html)
        
        button_layout.addWidget(view_btn)
        button_layout.addWidget(retry_btn)
        button_layout.addWidget(export_btn)
        button_layout.addStretch()
        
        main_layout.addLayout(button_layout)
        
        # Create menu bar
        self.create_menu_bar()
        
        # Create status bar
        self.statusBar().showMessage("Ready")
    
    def create_menu_bar(self):
        """Create menu bar with actions"""
        menu_bar = self.menuBar()
        
        # File menu
        file_menu = menu_bar.addMenu("File")
        
        refresh_action = QAction("Refresh", self)
        refresh_action.setShortcut("F5")
        refresh_action.triggered.connect(self.refresh_notifications)
        file_menu.addAction(refresh_action)
        
        file_menu.addSeparator()
        
        close_action = QAction("Close", self)
        close_action.setShortcut("Ctrl+W")
        close_action.triggered.connect(self.close)
        file_menu.addAction(close_action)
        
        # Actions menu
        actions_menu = menu_bar.addMenu("Actions")
        
        view_action = QAction("View Details", self)
        view_action.triggered.connect(self.view_notification)
        actions_menu.addAction(view_action)
        
        retry_action = QAction("Retry Failed", self)
        retry_action.triggered.connect(self.retry_failed)
        actions_menu.addAction(retry_action)
        
        export_action = QAction("Export as HTML", self)
        export_action.triggered.connect(self.export_as_html)
        actions_menu.addAction(export_action)
    
    def refresh_notifications(self):
        try:
            # Clear the table
            self.notification_table.setRowCount(0)
            
            # Get status filter
            status_filter = self.status_filter.currentText()
            status = None if status_filter == "All" else status_filter.lower()
            
            # Get notifications
            notifications = self.notification_service.get_notifications(status=status)
            
            # Count unread/failed notifications
            failed_count = sum(1 for n in notifications if n['status'] == 'failed')
            self.notification_count_changed.emit(failed_count)
            
            # Update status bar
            self.statusBar().showMessage(f"Displaying {len(notifications)} notifications | {failed_count} failed")
            
            # Populate table
            for notification in notifications:
                row_position = self.notification_table.rowCount()
                self.notification_table.insertRow(row_position)
                
                # ID
                id_item = QTableWidgetItem(str(notification['notification_id']))
                id_item.setData(Qt.UserRole, notification['notification_id'])
                self.notification_table.setItem(row_position, 0, id_item)
                
                # Type
                type_text = notification['notification_type'] or "General"
                self.notification_table.setItem(row_position, 1, QTableWidgetItem(type_text))
                
                # Recipient
                self.notification_table.setItem(row_position, 2, QTableWidgetItem(notification['recipient']))
                
                # Subject
                self.notification_table.setItem(row_position, 3, QTableWidgetItem(notification['subject']))
                
                # Status
                status_item = QTableWidgetItem(notification['status'].capitalize())
                if notification['status'] == 'sent':
                    status_item.setForeground(QColor("#4CAF50"))  # Green
                elif notification['status'] == 'failed':
                    status_item.setForeground(QColor("#F44336"))  # Red
                elif notification['status'] == 'pending':
                    status_item.setForeground(QColor("#FFC107"))  # Amber
                self.notification_table.setItem(row_position, 4, status_item)
                
                # Date
                date_str = notification['sent_at'] or notification['created_at']
                if isinstance(date_str, datetime):
                    date_str = date_str.strftime('%Y-%m-%d %H:%M')
                self.notification_table.setItem(row_position, 5, QTableWidgetItem(date_str))
            
            # Resize columns
            self.notification_table.resizeColumnsToContents()
            
        except Exception as e:
            print(f"Error refreshing notifications: {e}")
            self.statusBar().showMessage(f"Error: {e}")
    
    def view_notification(self):
        selected_rows = self.notification_table.selectedItems()
        if not selected_rows:
            return
            
        notification_id = self.notification_table.item(selected_rows[0].row(), 0).data(Qt.UserRole)
        notification = self.notification_service.get_notification_by_id(notification_id)
        
        if notification:
            dialog = NotificationDetailDialog(notification, self)
            dialog.exec()
    
    def retry_failed(self):
        selected_rows = self.notification_table.selectedItems()
        if not selected_rows:
            return
            
        notification_id = self.notification_table.item(selected_rows[0].row(), 0).data(Qt.UserRole)
        status = self.notification_table.item(selected_rows[0].row(), 4).text().lower()
        
        if status != 'failed':
            QMessageBox.information(self, "Retry Failed", "Only failed notifications can be retried.")
            return
            
        if self.notification_service.retry_failed_notification(notification_id):
            QMessageBox.information(self, "Success", "Notification was successfully resent.")
            self.refresh_notifications()
        else:
            QMessageBox.critical(self, "Error", "Failed to resend notification.")
    
    def export_as_html(self):
        selected_rows = self.notification_table.selectedItems()
        if not selected_rows:
            return
            
        notification_id = self.notification_table.item(selected_rows[0].row(), 0).data(Qt.UserRole)
        notification = self.notification_service.get_notification_by_id(notification_id)
        
        if notification:
            # Create a temporary HTML file
            with tempfile.NamedTemporaryFile(delete=False, suffix='.html') as f:
                f.write(notification['content'].encode('utf-8'))
                temp_path = f.name
            
            # Open in default browser
            webbrowser.open('file://' + temp_path)
    
    def show_context_menu(self, position):
        menu = QMenu()
        
        view_action = QAction("View Details", self)
        view_action.triggered.connect(self.view_notification)
        menu.addAction(view_action)
        
        selected_rows = self.notification_table.selectedItems()
        if selected_rows:
            status = self.notification_table.item(selected_rows[0].row(), 4).text().lower()
            
            if status == 'failed':
                retry_action = QAction("Retry Sending", self)
                retry_action.triggered.connect(self.retry_failed)
                menu.addAction(retry_action)
        
        export_action = QAction("Export as HTML", self)
        export_action.triggered.connect(self.export_as_html)
        menu.addAction(export_action)
        
        menu.exec(self.notification_table.mapToGlobal(position))


class NotificationDetailDialog(QDialog):
    def __init__(self, notification, parent=None):
        super().__init__(parent)
        self.notification = notification
        self.setWindowTitle("Notification Details")
        self.setMinimumSize(700, 500)
        
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Create tabs
        tab_widget = QTabWidget()
        
        # Details tab
        details_widget = QWidget()
        details_layout = QVBoxLayout(details_widget)
        
        # Header info
        header_layout = QVBoxLayout()
        
        subject_label = QLabel(f"<b>Subject:</b> {self.notification['subject']}")
        recipient_label = QLabel(f"<b>Recipient:</b> {self.notification['recipient']}")
        
        status_text = self.notification['status'].capitalize()
        status_color = "#4CAF50" if self.notification['status'] == 'sent' else "#F44336"
        status_label = QLabel(f"<b>Status:</b> <span style='color:{status_color}'>{status_text}</span>")
        
        type_text = self.notification['notification_type'] or "General"
        type_label = QLabel(f"<b>Type:</b> {type_text}")
        
        reference_text = self.notification['reference_id'] or "N/A"
        reference_label = QLabel(f"<b>Reference ID:</b> {reference_text}")
        
        created_date = self.notification['created_at']
        if isinstance(created_date, datetime):
            created_date = created_date.strftime('%Y-%m-%d %H:%M:%S')
        created_label = QLabel(f"<b>Created:</b> {created_date}")
        
        sent_date = self.notification['sent_at'] or "Not sent"
        if isinstance(sent_date, datetime):
            sent_date = sent_date.strftime('%Y-%m-%d %H:%M:%S')
        sent_label = QLabel(f"<b>Sent:</b> {sent_date}")
        
        header_layout.addWidget(subject_label)
        header_layout.addWidget(recipient_label)
        header_layout.addWidget(status_label)
        header_layout.addWidget(type_label)
        header_layout.addWidget(reference_label)
        header_layout.addWidget(created_label)
        header_layout.addWidget(sent_label)
        
        details_layout.addLayout(header_layout)
        
        # Error message if any
        if self.notification['error_message']:
            error_frame = QFrame()
            error_frame.setFrameShape(QFrame.StyledPanel)
            error_frame.setStyleSheet("background-color: #FFEBEE; padding: 10px; border-radius: 5px;")
            
            error_layout = QVBoxLayout(error_frame)
            error_title = QLabel("<b>Error Message:</b>")
            error_text = QLabel(self.notification['error_message'])
            error_text.setWordWrap(True)
            
            error_layout.addWidget(error_title)
            error_layout.addWidget(error_text)
            
            details_layout.addWidget(error_frame)
        
        details_layout.addStretch()
        
        # Content tab
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        
        content_browser = QTextEdit()
        content_browser.setReadOnly(True)
        content_browser.setHtml(self.notification['content'])
        
        content_layout.addWidget(content_browser)
        
        # Add tabs
        tab_widget.addTab(details_widget, "Details")
        tab_widget.addTab(content_widget, "Content")
        
        layout.addWidget(tab_widget)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        
        export_btn = QPushButton("Export as HTML")
        export_btn.clicked.connect(self.export_as_html)
        
        button_layout.addWidget(export_btn)
        button_layout.addStretch()
        button_layout.addWidget(close_btn)
        
        layout.addLayout(button_layout)
    
    def export_as_html(self):
        # Create a temporary HTML file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.html') as f:
            f.write(self.notification['content'].encode('utf-8'))
            temp_path = f.name
        
        # Open in default browser
        webbrowser.open('file://' + temp_path) 