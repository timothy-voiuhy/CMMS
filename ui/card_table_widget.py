from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                              QScrollArea, QFrame, QPushButton, QDialog,
                              QFormLayout, QTextEdit, QSizePolicy, QSpacerItem)
from PySide6.QtCore import Qt, Signal, QSize, QPoint, QPropertyAnimation, QEasingCurve
from PySide6.QtGui import QColor, QPalette, QFont, QIcon, QPainter, QPainterPath, QPen, QPixmap
import typing


class CardItemWidget(QFrame):
    """A card-style widget for displaying a single row of data"""
    clicked = Signal(object)  # Signal emitted when card is clicked
    doubleClicked = Signal(object)  # Signal emitted when card is double-clicked
    editClicked = Signal(object)  # Signal emitted when edit button is clicked
    contextMenuRequested = Signal(object, QPoint)  # Signal emitted when right-click menu is requested
    
    def __init__(self, data: dict, display_fields: list, parent=None):
        super().__init__(parent)
        self.data = data
        self.display_fields = display_fields
        self.hovered = False
        self.selected = False
        
        # Set up styling
        self.setObjectName("CardItem")
        self.setStyleSheet("""
            #CardItem {
                background-color: #2a2a2a;
                border-radius: 8px;
                padding: 10px;
                margin: 5px;
            }
            #CardItem:hover {
                background-color: #3a3a3a;
                border: 1px solid #4a90e2;
            }
            QPushButton#editButton {
                background-color: transparent;
                border: none;
                padding: 4px;
                border-radius: 12px;
            }
            QPushButton#editButton:hover {
                background-color: rgba(74, 144, 226, 0.2);
            }
            QLabel {
                color: #e0e0e0;
            }
            .field-name {
                color: #9e9e9e;
                font-size: 11px;
            }
            .field-value {
                color: #ffffff;
                font-size: 13px;
                font-weight: bold;
            }
            .status-label {
                border-radius: 10px;
                padding: 3px 8px;
                font-weight: bold;
                font-size: 11px;
            }
        """)
        
        # Enable mouse tracking for hover effects
        self.setMouseTracking(True)
        
        # Set up layout
        self.main_layout = QHBoxLayout(self)  # Changed to horizontal layout
        self.main_layout.setContentsMargins(10, 10, 10, 10)
        self.main_layout.setSpacing(8)
        
        # Create edit button
        self.edit_button = QPushButton()
        self.edit_button.setObjectName("editButton")
        self.edit_button.setFixedSize(24, 24)
        self.edit_button.setToolTip("Edit")
        
        # Load and set the edit icon
        edit_icon = QIcon.fromTheme("edit")  # Use system theme icon if available
        if edit_icon.isNull():
            # If no system theme icon, create a simple edit icon
            pixmap = QPixmap(24, 24)
            pixmap.fill(Qt.transparent)
            painter = QPainter(pixmap)
            painter.setPen(QPen(QColor("#4a90e2"), 2))
            painter.drawRect(6, 6, 12, 12)
            painter.drawLine(6, 6, 18, 18)
            painter.end()
            edit_icon = QIcon(pixmap)
        
        self.edit_button.setIcon(edit_icon)
        self.edit_button.clicked.connect(lambda: self.editClicked.emit(self.data))
        
        # Add edit button to layout
        self.main_layout.addWidget(self.edit_button)
        
        # Create content widget for the rest of the card
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(8)
        
        # Add header and content to content layout
        self.setup_header(content_layout)
        self.setup_content(content_layout)
        
        # Add content widget to main layout
        self.main_layout.addWidget(content_widget, 1)  # Give it stretch factor
        
        # Add animation properties
        self.setGraphicsEffect(None)
        self.animation = QPropertyAnimation(self, b"geometry")
        self.animation.setDuration(150)
        self.animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        
        # Enable context menu
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)

    def enterEvent(self, event):
        """Handle mouse enter event for hover effect"""
        self.hovered = True
        self.update()
        
        # Slightly enlarge the card
        current_geo = self.geometry()
        target_geo = current_geo.adjusted(-2, -2, 2, 2)
        
        self.animation.setStartValue(current_geo)
        self.animation.setEndValue(target_geo)
        self.animation.start()
        
        super().enterEvent(event)

    def leaveEvent(self, event):
        """Handle mouse leave event to remove hover effect"""
        self.hovered = False
        self.update()
        
        # Return to original size
        current_geo = self.geometry()
        target_geo = current_geo.adjusted(2, 2, -2, -2)
        
        self.animation.setStartValue(current_geo)
        self.animation.setEndValue(target_geo)
        self.animation.start()
        
        super().leaveEvent(event)

    def mousePressEvent(self, event):
        """Handle mouse press event"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit(self.data)
        super().mousePressEvent(event)

    def mouseDoubleClickEvent(self, event):
        """Handle mouse double click event"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.doubleClicked.emit(self.data)
        super().mouseDoubleClickEvent(event)

    def setSelected(self, selected):
        """Set the selected state of the card"""
        self.selected = selected
        self.update()

    def paintEvent(self, event):
        """Custom paint event to draw rounded corners and border"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Create rounded rectangle path
        path = QPainterPath()
        path.addRoundedRect(self.rect(), 8, 8)
        
        # Set clip path to ensure content stays within rounded corners
        painter.setClipPath(path)
        
        # Draw background
        if self.selected:
            painter.fillPath(path, QColor("#2b5b84"))  # Blue background for selected
        elif self.hovered:
            painter.fillPath(path, QColor("#3a3a3a"))
        else:
            painter.fillPath(path, QColor("#2a2a2a"))
        
        # Draw border
        if self.selected:
            pen = QPen(QColor("#4a90e2"), 2)
        elif self.hovered:
            pen = QPen(QColor("#4a90e2"), 1.5)
        else:
            pen = QPen(QColor("#3a3a3a"), 1)
        
        painter.setPen(pen)
        painter.drawPath(path)
        
        super().paintEvent(event)

    def setup_header(self, layout):
        """Setup the header section of the card"""
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(10)
        
        # Add primary field (usually ID or name) to header
        if len(self.display_fields) > 0:
            primary_field = self.display_fields[0]
            primary_value = self.data.get(primary_field['field'], '')
            
            primary_label = QLabel(str(primary_value))
            primary_label.setObjectName("PrimaryField")
            primary_label.setStyleSheet("""
                #PrimaryField {
                    color: #ffffff;
                    font-size: 16px;
                    font-weight: bold;
                }
            """)
            header_layout.addWidget(primary_label)
        
        # Add status field if it exists
        status_field = next((f for f in self.display_fields if f.get('type') == 'status'), None)
        if status_field:
            status_value = self.data.get(status_field['field'], '')
            status_label = QLabel(str(status_value))
            status_label.setObjectName("StatusLabel")
            status_label.setProperty("class", "status-label")
            
            # Set background color based on status
            status_colors = status_field.get('colors', {})
            bg_color = status_colors.get(status_value, "#808080")  # Default gray
            status_label.setStyleSheet(f"""
                #StatusLabel {{
                    background-color: {bg_color};
                    color: white;
                    border-radius: 10px;
                    padding: 3px 8px;
                }}
            """)
            
            header_layout.addWidget(status_label)
        
        # Add spacer to push status to the right
        header_layout.addStretch()
        
        # Add header to main layout
        layout.addLayout(header_layout)

    def setup_content(self, layout):
        """Setup the content section of the card"""
        content_layout = QHBoxLayout()
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(15)
        
        # Add other fields (skip the first one and status field)
        for field_info in self.display_fields[1:]:
            # Skip status field as it's already in the header
            if field_info.get('type') == 'status':
                continue
            
            field_name = field_info['field']
            display_name = field_info.get('display', field_name.replace('_', ' ').title())
            field_value = self.data.get(field_name, '')
            
            # Create field container
            field_container = QVBoxLayout()
            field_container.setSpacing(2)
            
            # Add field name
            name_label = QLabel(display_name)
            name_label.setProperty("class", "field-name")
            field_container.addWidget(name_label)
            
            # Add field value
            value_label = QLabel(str(field_value))
            value_label.setProperty("class", "field-value")
            
            # Handle special field types
            if field_info.get('type') == 'date':
                # Format date if needed
                pass
            elif field_info.get('type') == 'priority':
                # Set text color based on priority
                priority_colors = field_info.get('colors', {})
                text_color = priority_colors.get(field_value, "#e0e0e0")  # Default light gray
                value_label.setStyleSheet(f"color: {text_color}; font-weight: bold;")
            
            field_container.addWidget(value_label)
            content_layout.addLayout(field_container)
        
        # Add content to main layout
        layout.addLayout(content_layout)

    def show_context_menu(self, position):
        """Handle right-click context menu request"""
        # Convert position to global coordinates and emit signal with data
        global_pos = self.mapToGlobal(position)
        self.contextMenuRequested.emit(self.data, global_pos)


class CardDetailDialog(QDialog):
    """Dialog to display detailed information about a card item"""
    
    def __init__(self, data: dict, title: str = "Details", parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setMinimumSize(600, 400)
        
        # Set dialog styling
        self.setStyleSheet("""
            QDialog {
                background-color: #1e1e1e;
            }
            QLabel {
                color: #e0e0e0;
            }
            QTextEdit {
                background-color: #2a2a2a;
                color: #e0e0e0;
                border: 1px solid #3a3a3a;
                border-radius: 4px;
                padding: 5px;
            }
            QPushButton {
                background-color: #2b5b84;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
            }
            QPushButton:hover {
                background-color: #3a7ab7;
            }
            .field-name {
                font-weight: bold;
                color: #9e9e9e;
            }
            .field-value {
                color: #ffffff;
            }
        """)
        
        # Create main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
        
        # Create scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        
        # Create content widget
        content_widget = QWidget()
        form_layout = QFormLayout(content_widget)
        form_layout.setSpacing(10)
        form_layout.setContentsMargins(0, 0, 0, 0)
        
        # Add all data fields
        for key, value in data.items():
            # Create field name label
            field_name = QLabel(key.replace('_', ' ').title())
            field_name.setProperty("class", "field-name")
            
            # Create field value widget
            if isinstance(value, str) and len(value) > 100:
                # Use text edit for long text
                field_value = QTextEdit()
                field_value.setPlainText(str(value))
                field_value.setReadOnly(True)
                field_value.setMaximumHeight(100)
            else:
                # Use label for short text
                field_value = QLabel(str(value))
                field_value.setWordWrap(True)
                field_value.setProperty("class", "field-value")
            
            form_layout.addRow(field_name, field_value)
        
        scroll.setWidget(content_widget)
        main_layout.addWidget(scroll)
        
        # Add close button
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        close_button = QPushButton("Close")
        close_button.clicked.connect(self.accept)
        button_layout.addWidget(close_button)
        
        main_layout.addLayout(button_layout)


class CardTableWidget(QWidget):
    """A widget that displays data in card format instead of a traditional table"""
    
    itemClicked = Signal(object)  # Signal emitted when an item is clicked
    itemDoubleClicked = Signal(object)  # Signal emitted when an item is double-clicked
    itemEditClicked = Signal(object)  # New signal for edit button clicks
    itemContextMenuRequested = Signal(object, QPoint)  # New signal
    selectionChanged = Signal()  # Signal emitted when selection changes
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Set up main layout
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(10, 10, 10, 10)
        self.main_layout.setSpacing(10)
        
        # Create scroll area
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        
        # Create container for cards
        self.cards_container = QWidget()
        self.cards_layout = QVBoxLayout(self.cards_container)
        self.cards_layout.setContentsMargins(5, 5, 5, 5)
        self.cards_layout.setSpacing(10)
        self.cards_layout.addStretch()  # Add stretch to push cards to the top
        
        # Set the container as the scroll area's widget
        self.scroll_area.setWidget(self.cards_container)
        
        # Add scroll area to main layout
        self.main_layout.addWidget(self.scroll_area)
        
        # Initialize variables
        self.cards = []
        self.display_fields = []
        self.data = []
        self.selected_card = None
        self.selected_index = -1

    def set_display_fields(self, fields):
        """
        Set the fields to display in each card
        
        Args:
            fields: List of dictionaries with field configuration
                   Each dict should have:
                   - 'field': The data field name
                   - 'display': (optional) Display name
                   - 'type': (optional) Field type ('text', 'date', 'status', 'priority')
                   - 'colors': (optional) Dict mapping values to colors for status/priority
        """
        self.display_fields = fields
        
        # If we already have data, refresh the display
        if self.data:
            self.set_data(self.data)

    def set_data(self, data):
        """
        Set the data to display in the cards
        
        Args:
            data: List of dictionaries with data for each card
        """
        self.data = data
        self.refresh_cards()

    def refresh_cards(self):
        """Refresh the card display with current data and display fields"""
        self.clear_cards()
        
        for item_data in self.data:
            card = CardItemWidget(item_data, self.display_fields)
            card.clicked.connect(lambda d, c=card: self._handle_card_clicked(d, c))
            card.doubleClicked.connect(self._handle_card_double_clicked)
            card.editClicked.connect(self._handle_card_edit_clicked)
            card.contextMenuRequested.connect(self._handle_context_menu_requested)  # Connect context menu signal
            self.cards.append(card)
            self.cards_layout.insertWidget(self.cards_layout.count() - 1, card)

    def clear_cards(self):
        """Clear all cards from the layout"""
        # Remove all cards from layout
        for card in self.cards:
            self.cards_layout.removeWidget(card)
            card.deleteLater()
        
        self.cards = []
        self.selected_card = None
        self.selected_index = -1

    def _handle_card_clicked(self, data, card):
        """Handle when a card is clicked"""
        # Update selection
        if self.selected_card:
            self.selected_card.setSelected(False)
        
        self.selected_card = card
        self.selected_index = self.cards.index(card)
        card.setSelected(True)
        
        # Emit signal with the data
        self.itemClicked.emit(data)
        self.selectionChanged.emit()

    def _handle_card_double_clicked(self, data):
        """Handle when a card is double-clicked"""
        # Show detail dialog
        dialog = CardDetailDialog(data, "Item Details", self)
        dialog.exec()
        
        # Emit signal with the data
        self.itemDoubleClicked.emit(data)

    def _handle_card_edit_clicked(self, data):
        """Handle when a card's edit button is clicked"""
        self.itemEditClicked.emit(data)

    def _handle_context_menu_requested(self, data, position):
        """Handle context menu request from a card"""
        self.itemContextMenuRequested.emit(data, position)

    def filter_data(self, filter_func):
        """
        Filter the displayed cards based on a filter function
        
        Args:
            filter_func: Function that takes a data item and returns True if it should be shown
        """
        filtered_data = [item for item in self.data if filter_func(item)]
        
        # Update only the visibility of existing cards for better performance
        for card, item_data in zip(self.cards, self.data):
            card.setVisible(filter_func(item_data))
        
        # If no cards are visible, show a message
        has_visible_cards = any(card.isVisible() for card in self.cards)
        
        # TODO: Add a "no results" message when needed

    def get_selected_data(self):
        """Get the data of the currently selected card (if any)"""
        if self.selected_index >= 0 and self.selected_index < len(self.data):
            return self.data[self.selected_index]
        return None
    
    def selected_items(self):
        """Compatibility method for table-like interface"""
        if self.selected_index >= 0:
            # Return a list with a mock item that has a row() method
            class MockItem:
                def __init__(self, row):
                    self.row_index = row
                
                def row(self):
                    return self.row_index
            
            return [MockItem(self.selected_index)]
        return []
    
    def item(self, row, col):
        """Compatibility method for table-like interface"""
        if row >= 0 and row < len(self.data):
            # Return a mock item that has a text() method
            class MockItem:
                def __init__(self, text):
                    self.item_text = text
                
                def text(self):
                    return self.item_text
            
            # Get the appropriate field based on column index
            if col == 0 and 'employee_id' in self.data[row]:
                return MockItem(self.data[row]['employee_id'])
            elif col == 0 and 'craftsman_id' in self.data[row]:
                return MockItem(self.data[row]['craftsman_id'])
            
            # For other columns, try to map them to data fields
            field_mapping = {
                1: 'full_name',
                2: 'specialization',
                3: 'experience_level',
                4: 'phone',
                5: 'email',
                6: 'status',
                7: 'hire_date'
            }
            
            if col in field_mapping and field_mapping[col] in self.data[row]:
                return MockItem(str(self.data[row][field_mapping[col]]))
            
            return MockItem("")
        return None
    
    def rowCount(self):
        """Compatibility method for table-like interface"""
        return len(self.data)
    
    def setRowHidden(self, row, hidden):
        """Compatibility method for table-like interface"""
        if row >= 0 and row < len(self.cards):
            self.cards[row].setVisible(not hidden) 