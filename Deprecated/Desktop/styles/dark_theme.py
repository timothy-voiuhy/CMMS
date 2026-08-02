class DarkTheme:
    """
    Comprehensive dark theme stylesheet for the entire application.
    Handles styling for all common Qt widgets with a consistent color scheme.
    """
    
    # Color Palette
    COLORS = {
        # Base colors
        'bg_primary': '#282c34',
        'bg_secondary': '#21252b',
        'bg_tertiary': '#31363f',
        'bg_hover': '#434956',
        'bg_pressed': '#1b1d23',
        'bg_disabled': '#2c313a',
        
        # Borders
        'border': '#181a1f',
        
        # Text colors
        'text_primary': '#9da5b4',
        'text_secondary': '#6b727d',
        'text_disabled': '#4a4d52',
        
        # Accent colors
        'accent_blue': '#61afef',
        'accent_select': '#4d78cc',
        'accent_green': '#98c379',
        'accent_red': '#e06c75',
        'accent_yellow': '#e5c07b',
        'accent_orange': '#d19a66',
        'accent_purple': '#c678dd',
    }

    @classmethod
    def get_stylesheet(cls):
        """Returns the complete stylesheet for the application"""
        return f"""
            /* Global Application Style */
            QWidget {{
                background-color: {cls.COLORS['bg_primary']};
                color: {cls.COLORS['text_primary']};
            }}

            /* Main Window */
            QMainWindow {{
                background-color: {cls.COLORS['bg_primary']};
                color: {cls.COLORS['text_primary']};
            }}

            /* Tabs */
            QTabWidget::pane {{
                border: 1px solid {cls.COLORS['border']};
                background-color: {cls.COLORS['bg_primary']};
                top: -1px;
            }}
            
            QTabBar::tab {{
                background-color: {cls.COLORS['bg_secondary']};
                color: {cls.COLORS['text_primary']};
                padding: 8px 16px;
                border: 1px solid {cls.COLORS['border']};
                border-bottom: none;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
            }}
            
            QTabBar::tab:selected {{
                background-color: {cls.COLORS['bg_primary']};
                border-bottom: 2px solid {cls.COLORS['accent_blue']};
            }}
            
            QTabBar::tab:hover:!selected {{
                background-color: {cls.COLORS['bg_hover']};
            }}

            /* Group Boxes */
            QGroupBox {{
                border: 1px solid {cls.COLORS['border']};
                border-radius: 4px;
                margin-top: 1em;
                padding-top: 0.7em;
                color: {cls.COLORS['text_primary']};
            }}
            
            QGroupBox::title {{
                color: {cls.COLORS['accent_blue']};
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 3px;
            }}

            /* Buttons */
            QPushButton {{
                background-color: {cls.COLORS['bg_tertiary']};
                color: {cls.COLORS['text_primary']};
                border: none;
                border-radius: 3px;
                padding: 5px 15px;
                min-width: 80px;
            }}
            
            QPushButton:hover {{
                background-color: {cls.COLORS['bg_hover']};
            }}
            
            QPushButton:pressed {{
                background-color: {cls.COLORS['bg_pressed']};
            }}
            
            QPushButton:disabled {{
                background-color: {cls.COLORS['bg_disabled']};
                color: {cls.COLORS['text_disabled']};
            }}
            
            QPushButton:checked {{
                background-color: {cls.COLORS['accent_select']};
                color: white;
            }}

            /* Input Fields */
            QLineEdit, QSpinBox, QDoubleSpinBox, QComboBox, QDateEdit {{
                background-color: {cls.COLORS['bg_tertiary']};
                color: {cls.COLORS['text_primary']};
                border: 1px solid {cls.COLORS['border']};
                border-radius: 3px;
                padding: 4px;
                min-height: 20px;
            }}
            
            QLineEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus, 
            QComboBox:focus, QDateEdit:focus {{
                border-color: {cls.COLORS['accent_select']};
            }}
            
            QLineEdit:disabled, QSpinBox:disabled, QDoubleSpinBox:disabled,
            QComboBox:disabled, QDateEdit:disabled {{
                background-color: {cls.COLORS['bg_disabled']};
                color: {cls.COLORS['text_disabled']};
            }}

            /* Combo Box Specifics */
            QComboBox::drop-down {{
                border: none;
                width: 20px;
            }}
            
            QComboBox::down-arrow {{
                width: 12px;
                height: 12px;
                margin-right: 5px;
                image: none;
                border: 2px solid {cls.COLORS['text_primary']};
                border-width: 0 2px 2px 0;
                transform: rotate(45deg);
            }}
            
            QComboBox QAbstractItemView {{
                background-color: {cls.COLORS['bg_tertiary']};
                color: {cls.COLORS['text_primary']};
                selection-background-color: {cls.COLORS['accent_select']};
                selection-color: white;
                border: 1px solid {cls.COLORS['border']};
            }}

            /* Spin Boxes */
            QSpinBox::up-button, QDoubleSpinBox::up-button,
            QSpinBox::down-button, QDoubleSpinBox::down-button {{
                background-color: {cls.COLORS['bg_tertiary']};
                width: 16px;
                border: none;
            }}
            
            QSpinBox::up-arrow, QDoubleSpinBox::up-arrow {{
                width: 6px;
                height: 6px;
                border: 2px solid {cls.COLORS['text_primary']};
                border-width: 2px 2px 0 0;
                transform: rotate(-45deg);
            }}
            
            QSpinBox::down-arrow, QDoubleSpinBox::down-arrow {{
                width: 6px;
                height: 6px;
                border: 2px solid {cls.COLORS['text_primary']};
                border-width: 0 0 2px 2px;
                transform: rotate(-45deg);
            }}

            /* Tables */
            QTableWidget {{
                background-color: {cls.COLORS['bg_secondary']};
                alternate-background-color: {cls.COLORS['bg_primary']};
                border: 1px solid {cls.COLORS['border']};
                gridline-color: {cls.COLORS['border']};
            }}
            
            QTableWidget::item {{
                padding: 5px;
                color: {cls.COLORS['text_primary']};
            }}
            
            QTableWidget::item:selected {{
                background-color: {cls.COLORS['accent_select']};
                color: white;
            }}
            
            QHeaderView::section {{
                background-color: {cls.COLORS['bg_tertiary']};
                color: {cls.COLORS['text_primary']};
                padding: 5px;
                border: none;
                border-right: 1px solid {cls.COLORS['border']};
                border-bottom: 1px solid {cls.COLORS['border']};
            }}

            /* Scroll Bars */
            QScrollBar:vertical, QScrollBar:horizontal {{
                background-color: {cls.COLORS['bg_primary']};
                width: 14px;
                height: 14px;
                margin: 0px;
            }}
            
            QScrollBar::handle:vertical, QScrollBar::handle:horizontal {{
                background-color: {cls.COLORS['bg_tertiary']};
                min-height: 20px;
                min-width: 20px;
                border-radius: 7px;
                margin: 2px;
            }}
            
            QScrollBar::handle:hover {{
                background-color: {cls.COLORS['bg_hover']};
            }}
            
            QScrollBar::add-line, QScrollBar::sub-line {{
                height: 0px;
                width: 0px;
            }}
            
            QScrollBar::add-page, QScrollBar::sub-page {{
                background: none;
            }}

            /* Check Boxes */
            QCheckBox {{
                color: {cls.COLORS['text_primary']};
                spacing: 5px;
            }}
            
            QCheckBox::indicator {{
                width: 16px;
                height: 16px;
                border: 1px solid {cls.COLORS['border']};
                border-radius: 3px;
                background-color: {cls.COLORS['bg_tertiary']};
            }}
            
            QCheckBox::indicator:checked {{
                background-color: {cls.COLORS['accent_select']};
                border-color: {cls.COLORS['accent_select']};
            }}
            
            QCheckBox::indicator:hover {{
                border-color: {cls.COLORS['accent_blue']};
            }}

            /* Radio Buttons */
            QRadioButton {{
                color: {cls.COLORS['text_primary']};
                spacing: 5px;
            }}
            
            QRadioButton::indicator {{
                width: 16px;
                height: 16px;
                border: 1px solid {cls.COLORS['border']};
                border-radius: 8px;
                background-color: {cls.COLORS['bg_tertiary']};
            }}
            
            QRadioButton::indicator:checked {{
                background-color: {cls.COLORS['accent_select']};
                border-color: {cls.COLORS['accent_select']};
            }}

            /* Menu and Menu Items */
            QMenuBar {{
                background-color: {cls.COLORS['bg_primary']};
                color: {cls.COLORS['text_primary']};
            }}
            
            QMenuBar::item:selected {{
                background-color: {cls.COLORS['bg_hover']};
            }}
            
            QMenu {{
                background-color: {cls.COLORS['bg_secondary']};
                border: 1px solid {cls.COLORS['border']};
            }}
            
            QMenu::item {{
                padding: 5px 20px;
                color: {cls.COLORS['text_primary']};
            }}
            
            QMenu::item:selected {{
                background-color: {cls.COLORS['accent_select']};
                color: white;
            }}

            /* Status Bar */
            QStatusBar {{
                background-color: {cls.COLORS['bg_secondary']};
                color: {cls.COLORS['text_primary']};
            }}

            /* Tool Tips */
            QToolTip {{
                background-color: {cls.COLORS['bg_secondary']};
                color: {cls.COLORS['text_primary']};
                border: 1px solid {cls.COLORS['border']};
                padding: 4px;
            }}

            /* Progress Bar */
            QProgressBar {{
                border: 1px solid {cls.COLORS['border']};
                border-radius: 3px;
                background-color: {cls.COLORS['bg_secondary']};
                text-align: center;
                color: {cls.COLORS['text_primary']};
            }}
            
            QProgressBar::chunk {{
                background-color: {cls.COLORS['accent_blue']};
                width: 10px;
            }}

            /* Sliders */
            QSlider::groove:horizontal {{
                border: 1px solid {cls.COLORS['border']};
                height: 4px;
                background: {cls.COLORS['bg_secondary']};
                margin: 2px 0;
            }}
            
            QSlider::handle:horizontal {{
                background: {cls.COLORS['accent_blue']};
                border: 1px solid {cls.COLORS['border']};
                width: 18px;
                margin: -8px 0;
                border-radius: 9px;
            }}

            /* Status Indicators */
            .status-success {{
                color: {cls.COLORS['accent_green']};
            }}
            
            .status-error {{
                color: {cls.COLORS['accent_red']};
            }}
            
            .status-warning {{
                color: {cls.COLORS['accent_yellow']};
            }}
            
            .status-info {{
                color: {cls.COLORS['accent_blue']};
            }}
        """ 