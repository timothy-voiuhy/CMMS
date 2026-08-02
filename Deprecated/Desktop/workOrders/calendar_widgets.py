from PySide6.QtWidgets import QWidget, QDialog, QVBoxLayout, QLabel, QScrollArea, QFrame, QToolTip, QGraphicsDropShadowEffect
from PySide6.QtCore import Signal, QDate, QRect, QPoint, QTimer, Qt
from PySide6.QtGui import QPainter, QColor, QFont, QCursor

class BaseCalendarView(QWidget):
    """Base class for all calendar views"""
    date_clicked = Signal(QDate)
    work_order_clicked = Signal(int)  # work_order_id
    
    def __init__(self, db_manager, parent=None):
        super().__init__(parent)
        self.db_manager = db_manager
        self.current_date = QDate.currentDate()
        self.work_orders = []
        
    def refresh_view(self):
        """Refresh the calendar view with latest data"""
        self.load_work_orders()
        self.update()
        
    def load_work_orders(self):
        """Load work orders for the current view period"""
        # To be implemented by subclasses
        pass
        
    def get_work_order_color(self, work_order):
        """Get color for work order based on status"""
        # Check if overdue first (higher priority than status)
        due_date = QDate.fromString(str(work_order['due_date']), "yyyy-MM-dd")
        if due_date < QDate.currentDate() and work_order['status'] not in ["Completed", "Cancelled"]:
            return QColor("#F44336")  # Bright red for overdue
        
        # If not overdue, color by status
        status = work_order['status']
        if status == "Open":
            return QColor("#2196F3")
        elif status == "In Progress":
            return QColor("#FF9800")
        elif status == "On Hold":
            return QColor("#9C27B0")
        elif status == "Completed":
            return QColor("#4CAF50")
        elif status == "Cancelled":
            return QColor("#9E9E9E")
        
        return QColor("#607D8B")  # Default
        
    def set_date(self, date):
        """Set the current date and refresh view"""
        self.current_date = date
        self.refresh_view()
        
    def go_to_today(self):
        """Go to today's date"""
        self.current_date = QDate.currentDate()
        self.refresh_view()


class WorkOrdersPopup(QDialog):
    """Popup dialog to display all work orders for a specific date"""
    work_order_clicked = Signal(int)  # work_order_id
    
    def __init__(self, date, work_orders, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Work Orders - {date.toString('MMMM d, yyyy')}")
        self.setMinimumSize(400, 300)
        
        # Remove window frame and set styling for dark theme
        self.setWindowFlags(Qt.WindowType.Popup | Qt.WindowType.FramelessWindowHint)
        self.setStyleSheet("""
            QDialog {
                background-color: #2D2D30;
                border: 1px solid #3F3F46;
                border-radius: 10px;
            }
            QLabel {
                color: #E0E0E0;
            }
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            QScrollBar:vertical {
                background-color: #2D2D30;
                width: 12px;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background-color: #3F3F46;
                min-height: 20px;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #525257;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """)
        
        # Create layout with margins for rounded corners
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        
        # Add date header with styling
        date_label = QLabel(f"<h2>Work Orders for {date.toString('MMMM d, yyyy')}</h2>")
        date_label.setStyleSheet("color: #4FC3F7; margin-bottom: 10px;")
        layout.addWidget(date_label)
        
        # Add close button hint
        hint_label = QLabel("Click on a work order to open it, or click outside to close")
        hint_label.setStyleSheet("color: #9E9E9E; font-size: 11px; margin-bottom: 10px;")
        layout.addWidget(hint_label)
        
        # Create scroll area for work orders
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        
        # Create container widget for work orders
        container = QWidget()
        container.setStyleSheet("background-color: transparent;")
        container_layout = QVBoxLayout(container)
        container_layout.setSpacing(10)  # Add space between work orders
        
        # Add work order widgets
        for wo in work_orders:
            wo_widget = self.create_work_order_widget(wo)
            container_layout.addWidget(wo_widget)
            
        # Add stretch to push work orders to the top
        container_layout.addStretch()
        
        # Set container as scroll area widget
        scroll_area.setWidget(container)
        layout.addWidget(scroll_area)
        
    def create_work_order_widget(self, work_order):
        """Create a widget to display a work order"""
        frame = QFrame()
        frame.setFrameShape(QFrame.Shape.StyledPanel)
        frame.setFrameShadow(QFrame.Shadow.Raised)
        
        # Set rounded corners and shadow effect
        frame.setStyleSheet(f"""
            QFrame {{
                background-color: {self.get_color_string(work_order)};
                color: white;
                border-radius: 8px;
                padding: 8px;
            }}
            QLabel {{
                color: white;
            }}
        """)
        
        # Store work order ID
        frame.work_order_id = work_order['work_order_id']
        
        # Create layout
        layout = QVBoxLayout(frame)
        layout.setSpacing(5)  # Tighter spacing
        
        # Add work order details
        title_label = QLabel(f"<b>{work_order['title']}</b>")
        title_label.setStyleSheet("font-size: 14px;")
        layout.addWidget(title_label)
        
        # Create a grid for the details
        details_widget = QWidget()
        details_layout = QVBoxLayout(details_widget)
        details_layout.setContentsMargins(0, 0, 0, 0)
        details_layout.setSpacing(3)
        
        equipment_label = QLabel(f"<b>Equipment:</b> {work_order['equipment_name']}")
        details_layout.addWidget(equipment_label)
        
        assigned_label = QLabel(f"<b>Assigned to:</b> {work_order['assigned_to']}")
        details_layout.addWidget(assigned_label)
        
        status_label = QLabel(f"<b>Status:</b> {work_order['status']}")
        details_layout.addWidget(status_label)
        
        layout.addWidget(details_widget)
        
        # Connect mouse press event
        frame.mousePressEvent = lambda event, wo_id=work_order['work_order_id']: self.on_work_order_clicked(wo_id)
        
        return frame
    
    def get_color_string(self, work_order):
        """Get color for work order based on status"""
        # Check if overdue
        due_date = QDate.fromString(str(work_order['due_date']), "yyyy-MM-dd")
        if due_date < QDate.currentDate() and work_order['status'] not in ["Completed", "Cancelled"]:
            return "#F44336"  # Bright red for overdue
        
        # If not overdue, color by status
        status = work_order['status']
        if status == "Open":
            return "#2196F3"
        elif status == "In Progress":
            return "#FF9800"
        elif status == "On Hold":
            return "#9C27B0"
        elif status == "Completed":
            return "#4CAF50"
        elif status == "Cancelled":
            return "#9E9E9E"
        
        return "#607D8B"  # Default
    
    def on_work_order_clicked(self, work_order_id):
        """Handle work order click"""
        self.work_order_clicked.emit(work_order_id)
        self.close()


class MonthCalendarView(BaseCalendarView):
    """Custom month calendar view"""
    def __init__(self, db_manager, parent=None):
        super().__init__(db_manager, parent)
        self.setMinimumHeight(500)
        self.day_rects = {}  # Maps dates to their rectangles
        self.corner_radius = 8  # Radius for rounded corners
        self.popup = None  # Current popup dialog
        
        # We don't need mouse tracking anymore since we're not using hover
        self.setMouseTracking(False)
        
    def load_work_orders(self):
        """Load work orders for the current month"""
        first_day = QDate(self.current_date.year(), self.current_date.month(), 1)
        last_day = QDate(self.current_date.year(), self.current_date.month(), first_day.daysInMonth())
        
        self.work_orders = self.db_manager.get_work_orders_by_date_range(
            first_day.toPython(), last_day.toPython()
        )
        
    def paintEvent(self, event):
        """Draw the month calendar"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Clear the day_rects dictionary
        self.day_rects = {}
        
        # Get first day of month and number of days
        first_day = QDate(self.current_date.year(), self.current_date.month(), 1)
        days_in_month = first_day.daysInMonth()
        
        # Calculate first day of week (0=Monday, 6=Sunday)
        first_day_of_week = first_day.dayOfWeek() - 1  # Convert to 0-based
        if first_day_of_week < 0:  # Handle Sunday
            first_day_of_week = 6
        
        # Calculate grid dimensions
        width = self.width()
        height = self.height()
        header_height = 40  # Increased from 30 to add more space
        cell_width = width / 7
        cell_height = (height - header_height) / 6  # Reserve space for day names
        
        # Draw day names
        day_names = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        for i, day_name in enumerate(day_names):
            painter.drawText(
                i * cell_width + 5, 20,
                cell_width - 10, 20,
                Qt.AlignmentFlag.AlignCenter,
                day_name
            )
        
        # Draw days
        for day in range(1, days_in_month + 1):
            date = QDate(self.current_date.year(), self.current_date.month(), day)
            day_of_week = date.dayOfWeek() - 1  # Convert to 0-based
            if day_of_week < 0:  # Handle Sunday
                day_of_week = 6
            
            week = (day + first_day_of_week - 1) // 7
            
            # Calculate cell rectangle
            rect = QRect(
                day_of_week * cell_width + 2,  # Add small margin
                week * cell_height + header_height + 2,  # Add offset for day names and margin
                cell_width - 4,  # Subtract margin
                cell_height - 4  # Subtract margin
            )
            
            # Store the rectangle for this date
            self.day_rects[date] = rect
            
            # Draw cell background
            if date == QDate.currentDate():
                # Highlight today
                painter.save()
                painter.setPen(Qt.PenStyle.NoPen)
                painter.setBrush(QColor(240, 240, 255))
                painter.drawRoundedRect(rect, self.corner_radius, self.corner_radius)
                painter.restore()
            
            # Draw border with rounded corners
            painter.save()
            painter.setPen(QColor(200, 200, 200))
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawRoundedRect(rect, self.corner_radius, self.corner_radius)
            painter.restore()
            
            # Draw day number
            painter.drawText(
                rect.x() + 5, rect.y() + 5,
                rect.width() - 10, 20,
                Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop,
                str(day)
            )
            
            # Draw work orders for this day
            day_work_orders = [wo for wo in self.work_orders 
                             if QDate.fromString(str(wo['due_date']), "yyyy-MM-dd") == date]
            
            if day_work_orders:
                # Create a smaller rectangle for work orders
                work_orders_rect = QRect(
                    rect.x() + 5,
                    rect.y() + 25,
                    rect.width() - 10,
                    rect.height() - 30
                )
                
                # Only show the first work order
                if day_work_orders:
                    wo = day_work_orders[0]
                    wo_rect = QRect(
                        work_orders_rect.x(),
                        work_orders_rect.y(),
                        work_orders_rect.width(),
                        20
                    )
                    
                    # Draw work order background with rounded corners
                    painter.save()
                    painter.setPen(Qt.PenStyle.NoPen)
                    painter.setBrush(self.get_work_order_color(wo))
                    painter.drawRoundedRect(wo_rect, 4, 4)  # Smaller radius for work orders
                    painter.restore()
                    
                    # Draw work order text
                    painter.setPen(Qt.GlobalColor.white)
                    painter.drawText(
                        wo_rect.adjusted(5, 0, -5, 0),
                        Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
                        wo['title'][:15] + ('...' if len(wo['title']) > 15 else '')
                    )
                    painter.setPen(Qt.GlobalColor.black)
                
                # Show count if there are more work orders
                if len(day_work_orders) > 1:
                    count_rect = QRect(
                        work_orders_rect.x(),
                        work_orders_rect.y() + 25,  # Position below the first work order
                        work_orders_rect.width(),
                        20
                    )
                    
                    # Draw background for count
                    painter.save()
                    painter.setPen(Qt.PenStyle.NoPen)
                    painter.setBrush(QColor(100, 100, 100, 150))
                    painter.drawRoundedRect(count_rect, 4, 4)
                    painter.restore()
                    
                    # Draw count text
                    painter.setPen(Qt.GlobalColor.white)
                    painter.drawText(
                        count_rect,
                        Qt.AlignmentFlag.AlignCenter,
                        f"+{len(day_work_orders) - 1} more"
                    )
                    painter.setPen(Qt.GlobalColor.black)
    
    def mousePressEvent(self, event):
        """Handle mouse press events"""
        for date, rect in self.day_rects.items():
            if rect.contains(event.pos()):
                # Get work orders for this date
                day_work_orders = [wo for wo in self.work_orders 
                                 if QDate.fromString(str(wo['due_date']), "yyyy-MM-dd") == date]
                
                # If there are work orders, show popup
                if day_work_orders:
                    self.show_work_orders_dialog(date, day_work_orders)
                    return
                
                # If no work orders, emit date clicked
                self.date_clicked.emit(date)
                return
    
    def previous_month(self):
        """Go to previous month"""
        self.current_date = self.current_date.addMonths(-1)
        self.refresh_view()
    
    def next_month(self):
        """Go to next month"""
        self.current_date = self.current_date.addMonths(1)
        self.refresh_view()

    def show_work_orders_dialog(self, date, work_orders):
        """Show dialog with all work orders for a date"""
        # Close existing popup if any
        if self.popup:
            self.popup.close()
        
        # Create new popup
        self.popup = WorkOrdersPopup(date, work_orders, self)
        
        # Connect work order clicked signal
        self.popup.work_order_clicked.connect(self.work_order_clicked)
        
        # Position popup near the cursor but ensure it's visible on screen
        cursor_pos = QCursor.pos()
        screen_rect = self.screen().availableGeometry()
        
        # Calculate popup position to ensure it stays on screen
        popup_width = 400  # Estimated width
        popup_height = min(500, 100 + len(work_orders) * 100)  # Estimated height
        
        x = min(cursor_pos.x(), screen_rect.right() - popup_width)
        y = min(cursor_pos.y(), screen_rect.bottom() - popup_height)
        
        self.popup.setGeometry(x, y, popup_width, popup_height)
        
        # Add drop shadow effect
        shadow = QGraphicsDropShadowEffect(self.popup)
        shadow.setBlurRadius(15)
        shadow.setColor(QColor(0, 0, 0, 80))
        shadow.setOffset(0, 0)
        self.popup.setGraphicsEffect(shadow)
        
        # Show popup
        self.popup.show()


class WeekCalendarView(BaseCalendarView):
    """Custom week calendar view"""
    def __init__(self, db_manager, parent=None):
        super().__init__(db_manager, parent)
        self.setMinimumHeight(500)
        self.day_rects = {}  # Maps dates to their rectangles
        self.work_order_rects = {}  # Maps work order IDs to their rectangles
        self.week_start_date = self.get_week_start_date(self.current_date)
        
    def get_week_start_date(self, date):
        """Get the start date of the week (Monday)"""
        days_to_subtract = date.dayOfWeek() - 1
        if days_to_subtract < 0:  # Handle Sunday
            days_to_subtract = 6
        return date.addDays(-days_to_subtract)
    
    def load_work_orders(self):
        """Load work orders for the current week"""
        self.week_start_date = self.get_week_start_date(self.current_date)
        week_end_date = self.week_start_date.addDays(6)
        
        self.work_orders = self.db_manager.get_work_orders_by_date_range(
            self.week_start_date.toPython(), week_end_date.toPython()
        )
        
    def paintEvent(self, event):
        """Draw the week calendar"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Clear the dictionaries
        self.day_rects = {}
        self.work_order_rects = {}
        
        # Calculate dimensions
        width = self.width()
        height = self.height()
        day_width = width / 7
        header_height = 30
        
        # Draw day headers
        day_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        for i, day_name in enumerate(day_names):
            date = self.week_start_date.addDays(i)
            
            # Create header rectangle
            header_rect = QRect(
                i * day_width,
                0,
                day_width,
                header_height
            )
            
            # Draw header background
            if date == QDate.currentDate():
                painter.fillRect(header_rect, QColor(240, 240, 255))
            
            # Draw header text
            painter.drawText(
                header_rect,
                Qt.AlignmentFlag.AlignCenter,
                f"{day_name}\n{date.toString('MMM d')}"
            )
            
            # Draw header border
            painter.drawRect(header_rect)
            
            # Create day rectangle
            day_rect = QRect(
                i * day_width,
                header_height,
                day_width,
                height - header_height
            )
            
            # Store the rectangle for this date
            self.day_rects[date] = day_rect
            
            # Draw day border
            painter.drawRect(day_rect)
            
            # Draw work orders for this day
            day_work_orders = [wo for wo in self.work_orders 
                             if QDate.fromString(str(wo['due_date']), "yyyy-MM-dd") == date]
            
            if day_work_orders:
                y_offset = 5
                for wo in day_work_orders:
                    # Create work order rectangle
                    wo_rect = QRect(
                        day_rect.x() + 5,
                        day_rect.y() + y_offset,
                        day_rect.width() - 10,
                        60
                    )
                    
                    # Store the rectangle for this work order
                    self.work_order_rects[wo['work_order_id']] = wo_rect
                    
                    # Draw work order background
                    painter.fillRect(wo_rect, self.get_work_order_color(wo))
                    
                    # Draw work order text
                    painter.setPen(Qt.GlobalColor.white)
                    
                    # Draw title
                    title_rect = QRect(
                        wo_rect.x() + 5,
                        wo_rect.y() + 5,
                        wo_rect.width() - 10,
                        20
                    )
                    painter.drawText(
                        title_rect,
                        Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
                        wo['title']
                    )
                    
                    # Draw equipment name
                    equip_rect = QRect(
                        wo_rect.x() + 5,
                        wo_rect.y() + 25,
                        wo_rect.width() - 10,
                        15
                    )
                    painter.drawText(
                        equip_rect,
                        Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
                        f"Equipment: {wo['equipment_name']}"
                    )
                    
                    # Draw assigned to
                    assigned_rect = QRect(
                        wo_rect.x() + 5,
                        wo_rect.y() + 40,
                        wo_rect.width() - 10,
                        15
                    )
                    painter.drawText(
                        assigned_rect,
                        Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
                        f"Assigned: {wo['assigned_to']}"
                    )
                    
                    painter.setPen(Qt.GlobalColor.black)
                    
                    y_offset += 65
    
    def mousePressEvent(self, event):
        """Handle mouse press events"""
        # Check if clicked on a work order
        for wo_id, rect in self.work_order_rects.items():
            if rect.contains(event.pos()):
                self.work_order_clicked.emit(wo_id)
                return
        
        # Check if clicked on a day
        for date, rect in self.day_rects.items():
            if rect.contains(event.pos()):
                self.date_clicked.emit(date)
                return
    
    def previous_week(self):
        """Go to previous week"""
        self.current_date = self.current_date.addDays(-7)
        self.refresh_view()
    
    def next_week(self):
        """Go to next week"""
        self.current_date = self.current_date.addDays(7)
        self.refresh_view()


class DayCalendarView(BaseCalendarView):
    """Custom day calendar view"""
    def __init__(self, db_manager, parent=None):
        super().__init__(db_manager, parent)
        self.setMinimumHeight(500)
        self.work_order_rects = {}  # Maps work order IDs to their rectangles
        
    def load_work_orders(self):
        """Load work orders for the current day"""
        self.work_orders = self.db_manager.get_work_orders_by_date(
            self.current_date.toPython()
        )
        
    def paintEvent(self, event):
        """Draw the day calendar"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Clear the dictionary
        self.work_order_rects = {}
        
        # Calculate dimensions
        width = self.width()
        height = self.height()
        
        # Draw header
        header_rect = QRect(0, 0, width, 40)
        painter.fillRect(header_rect, QColor(240, 240, 255))
        painter.drawRect(header_rect)
        
        # Draw header text
        painter.drawText(
            header_rect,
            Qt.AlignmentFlag.AlignCenter,
            f"{self.current_date.toString('dddd, MMMM d, yyyy')}"
        )
        
        # Draw work orders
        if self.work_orders:
            y_offset = 50  # Start below header
            for wo in self.work_orders:
                # Create work order rectangle
                wo_rect = QRect(
                    10,
                    y_offset,
                    width - 20,
                    100
                )
                
                # Store the rectangle for this work order
                self.work_order_rects[wo['work_order_id']] = wo_rect
                
                # Draw work order background
                painter.fillRect(wo_rect, self.get_work_order_color(wo))
                
                # Draw work order border
                painter.drawRect(wo_rect)
                
                # Draw work order text
                painter.setPen(Qt.GlobalColor.white)
                
                # Draw title
                title_rect = QRect(
                    wo_rect.x() + 10,
                    wo_rect.y() + 10,
                    wo_rect.width() - 20,
                    30
                )
                font = painter.font()
                font.setPointSize(12)
                font.setBold(True)
                painter.setFont(font)
                painter.drawText(
                    title_rect,
                    Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
                    wo['title']
                )
                
                # Reset font
                font.setPointSize(10)
                font.setBold(False)
                painter.setFont(font)
                
                # Draw equipment name
                equip_rect = QRect(
                    wo_rect.x() + 10,
                    wo_rect.y() + 40,
                    wo_rect.width() - 20,
                    20
                )
                painter.drawText(
                    equip_rect,
                    Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
                    f"Equipment: {wo['equipment_name']}"
                )
                
                # Draw assigned to
                assigned_rect = QRect(
                    wo_rect.x() + 10,
                    wo_rect.y() + 60,
                    wo_rect.width() - 20,
                    20
                )
                painter.drawText(
                    assigned_rect,
                    Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
                    f"Assigned to: {wo['assigned_to']}"
                )
                
                # Draw status
                status_rect = QRect(
                    wo_rect.x() + 10,
                    wo_rect.y() + 80,
                    wo_rect.width() - 20,
                    20
                )
                painter.drawText(
                    status_rect,
                    Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
                    f"Status: {wo['status']}"
                )
                
                painter.setPen(Qt.GlobalColor.black)
                
                y_offset += 110
        else:
            # Draw "No work orders" message
            painter.drawText(
                QRect(0, 50, width, 50),
                Qt.AlignmentFlag.AlignCenter,
                "No work orders scheduled for this day"
            )
    
    def mousePressEvent(self, event):
        """Handle mouse press events"""
        # Check if clicked on a work order
        for wo_id, rect in self.work_order_rects.items():
            if rect.contains(event.pos()):
                self.work_order_clicked.emit(wo_id)
                return
    
    def previous_day(self):
        """Go to previous day"""
        self.current_date = self.current_date.addDays(-1)
        self.refresh_view()
    
    def next_day(self):
        """Go to next day"""
        self.current_date = self.current_date.addDays(1)
        self.refresh_view()

