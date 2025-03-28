import sys
from PySide6.QtWidgets import QApplication, QDialog, QVBoxLayout, QLabel, QSlider, QDialogButtonBox
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

class GlobalFontSizeDialog(QDialog):
    def __init__(self, parent=None):
        """
        Dialog to change the font size for the entire application
        """
        super().__init__(parent)
        self.setWindowTitle("Application Font Size")
        self.setMinimumWidth(350)
        
        # Create layout
        layout = QVBoxLayout(self)
        
        # Current font size preview label
        self.preview_label = QLabel("Preview: How the text will look")
        layout.addWidget(self.preview_label)
        
        # Font size slider
        self.font_slider = QSlider(Qt.Horizontal)
        self.font_slider.setRange(8, 24)  # Reasonable font size range
        self.font_slider.setValue(QApplication.font().pointSize())
        self.font_slider.valueChanged.connect(self.update_font_preview)
        layout.addWidget(self.font_slider)
        
        # Label to show current font size
        self.size_label = QLabel(f"Font Size: {self.font_slider.value()} pt")
        layout.addWidget(self.size_label)
        
        # Dialog buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
        # Initial setup of preview
        self.update_font_preview(self.font_slider.value())
    
    def update_font_preview(self, value):
        """
        Update the preview label and size label
        """
        # Update size label
        self.size_label.setText(f"Font Size: {value} pt")
        
        # Create preview font
        preview_font = QFont()
        preview_font.setPointSize(value)
        self.preview_label.setFont(preview_font)
    
    @classmethod
    def change_application_font_size(cls, font_size=None):
        """
        Change the font size for the entire application
        
        :param font_size: Optional specific font size to set
        """
        # Get the current application instance
        app = QApplication.instance()
        
        # If no size provided, show dialog
        if font_size is None:
            dialog = cls()
            if dialog.exec():
                font_size = dialog.font_slider.value()
            else:
                return  # User cancelled
        
        # Create a new font with the selected size
        font = app.font()
        font.setPointSize(font_size)
        
        # Set the font for the entire application
        app.setFont(font)
