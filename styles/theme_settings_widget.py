from qtpy.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QSlider, 
    QPushButton, QColorDialog, QGroupBox, QScrollArea,
    QFormLayout, QSpinBox, QComboBox, QCheckBox, QInputDialog,
    QMessageBox
)
from qtpy.QtCore import Qt, Signal
from qtpy.QtGui import QColor
import colorsys
from .theme_config import ThemeConfig

class ColorPicker(QWidget):
    """Custom color picker widget with preview"""
    color_changed = Signal(str, str)  # (color_key, hex_color)
    
    def __init__(self, color_key: str, initial_color: str, label: str, parent=None):
        super().__init__(parent)
        self.color_key = color_key
        self.current_color = QColor(initial_color)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        self.label = QLabel(label)
        self.preview = QLabel()
        self.preview.setFixedSize(25, 25)
        self.update_preview()
        
        self.pick_button = QPushButton("Change")
        self.pick_button.clicked.connect(self.pick_color)
        
        layout.addWidget(self.label)
        layout.addWidget(self.preview)
        layout.addWidget(self.pick_button)
        layout.addStretch()
    
    def update_preview(self):
        self.preview.setStyleSheet(
            f"background-color: {self.current_color.name()}; "
            f"border: 1px solid #666666; border-radius: 3px;"
        )
    
    def pick_color(self):
        color = QColorDialog.getColor(self.current_color, self)
        if color.isValid():
            self.current_color = color
            self.update_preview()
            self.color_changed.emit(self.color_key, color.name())

class ThemeSettingsWidget(QWidget):
    """Widget for customizing theme settings"""
    
    theme_updated = Signal(dict)  # Emits when theme settings are changed
    
    # Define built-in presets as a class attribute
    built_in_presets = [
        "Custom",
        "Dark",
        "Darker",
        "Ocean",
        "Forest",
        "Purple",
        "Nord"
    ]
    
    def __init__(self, dark_theme, parent=None):
        super().__init__(parent)
        self.dark_theme = dark_theme
        self.colors = dark_theme.COLORS.copy()
        self.theme_config = ThemeConfig()
        self.setup_ui()
        self.load_saved_themes()
        
    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        
        # Create scroll area for settings
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)
        
        # Brightness and Contrast Controls
        appearance_group = QGroupBox("Global Appearance")
        appearance_layout = QFormLayout()
        
        # Brightness control
        self.brightness_slider = QSlider(Qt.Horizontal)
        self.brightness_slider.setRange(-100, 100)
        self.brightness_slider.setValue(0)
        self.brightness_slider.valueChanged.connect(self.adjust_brightness)
        appearance_layout.addRow("Brightness:", self.brightness_slider)
        
        # Contrast control
        self.contrast_slider = QSlider(Qt.Horizontal)
        self.contrast_slider.setRange(-100, 100)
        self.contrast_slider.setValue(0)
        self.contrast_slider.valueChanged.connect(self.adjust_contrast)
        appearance_layout.addRow("Contrast:", self.contrast_slider)
        
        # Saturation control
        self.saturation_slider = QSlider(Qt.Horizontal)
        self.saturation_slider.setRange(-100, 100)
        self.saturation_slider.setValue(0)
        self.saturation_slider.valueChanged.connect(self.adjust_saturation)
        appearance_layout.addRow("Saturation:", self.saturation_slider)
        
        appearance_group.setLayout(appearance_layout)
        scroll_layout.addWidget(appearance_group)
        
        # Color Customization
        colors_group = QGroupBox("Color Customization")
        colors_layout = QVBoxLayout()
        
        # Background colors
        bg_group = QGroupBox("Background Colors")
        bg_layout = QVBoxLayout()
        
        self.bg_pickers = {
            'bg_primary': ColorPicker('bg_primary', self.colors['bg_primary'], "Primary Background"),
            'bg_secondary': ColorPicker('bg_secondary', self.colors['bg_secondary'], "Secondary Background"),
            'bg_tertiary': ColorPicker('bg_tertiary', self.colors['bg_tertiary'], "Tertiary Background"),
            'bg_hover': ColorPicker('bg_hover', self.colors['bg_hover'], "Hover Background"),
        }
        
        for picker in self.bg_pickers.values():
            picker.color_changed.connect(self.color_changed)
            bg_layout.addWidget(picker)
        
        bg_group.setLayout(bg_layout)
        colors_layout.addWidget(bg_group)
        
        # Accent colors
        accent_group = QGroupBox("Accent Colors")
        accent_layout = QVBoxLayout()
        
        self.accent_pickers = {
            'accent_blue': ColorPicker('accent_blue', self.colors['accent_blue'], "Primary Accent"),
            'accent_select': ColorPicker('accent_select', self.colors['accent_select'], "Selection"),
            'accent_green': ColorPicker('accent_green', self.colors['accent_green'], "Success"),
            'accent_red': ColorPicker('accent_red', self.colors['accent_red'], "Error"),
            'accent_yellow': ColorPicker('accent_yellow', self.colors['accent_yellow'], "Warning"),
        }
        
        for picker in self.accent_pickers.values():
            picker.color_changed.connect(self.color_changed)
            accent_layout.addWidget(picker)
        
        accent_group.setLayout(accent_layout)
        colors_layout.addWidget(accent_group)
        
        # Text colors
        text_group = QGroupBox("Text Colors")
        text_layout = QVBoxLayout()
        
        self.text_pickers = {
            'text_primary': ColorPicker('text_primary', self.colors['text_primary'], "Primary Text"),
            'text_secondary': ColorPicker('text_secondary', self.colors['text_secondary'], "Secondary Text"),
            'text_disabled': ColorPicker('text_disabled', self.colors['text_disabled'], "Disabled Text"),
        }
        
        for picker in self.text_pickers.values():
            picker.color_changed.connect(self.color_changed)
            text_layout.addWidget(picker)
        
        text_group.setLayout(text_layout)
        colors_layout.addWidget(text_group)
        
        colors_group.setLayout(colors_layout)
        scroll_layout.addWidget(colors_group)
        
        # Border customization
        border_group = QGroupBox("Border Settings")
        border_layout = QFormLayout()
        
        self.border_picker = ColorPicker('border', self.colors['border'], "Border Color")
        self.border_picker.color_changed.connect(self.color_changed)
        
        self.border_radius = QSpinBox()
        self.border_radius.setRange(0, 20)
        self.border_radius.setValue(3)
        self.border_radius.valueChanged.connect(self.update_theme)
        
        border_layout.addRow(self.border_picker)
        border_layout.addRow("Border Radius:", self.border_radius)
        
        border_group.setLayout(border_layout)
        scroll_layout.addWidget(border_group)
        
        # Preset themes
        presets_group = QGroupBox("Theme Presets")
        presets_layout = QHBoxLayout()
        
        self.preset_combo = QComboBox()
        self.preset_combo.currentTextChanged.connect(self.load_preset)
        
        # Add buttons for save/delete
        self.save_preset_btn = QPushButton("Save As...")
        self.save_preset_btn.clicked.connect(self.save_current_preset)
        
        self.delete_preset_btn = QPushButton("Delete")
        self.delete_preset_btn.clicked.connect(self.delete_current_preset)
        
        presets_layout.addWidget(self.preset_combo)
        presets_layout.addWidget(self.save_preset_btn)
        presets_layout.addWidget(self.delete_preset_btn)
        
        presets_group.setLayout(presets_layout)
        scroll_layout.addWidget(presets_group)
        
        # Action buttons
        button_layout = QHBoxLayout()
        
        self.apply_btn = QPushButton("Apply Changes")
        self.apply_btn.clicked.connect(self.update_theme)
        
        self.reset_btn = QPushButton("Reset to Default")
        self.reset_btn.clicked.connect(self.reset_to_default)
        
        button_layout.addWidget(self.apply_btn)
        button_layout.addWidget(self.reset_btn)
        
        scroll_layout.addLayout(button_layout)
        scroll.setWidget(scroll_widget)
        main_layout.addWidget(scroll)
    
    def adjust_brightness(self, value):
        """Adjust brightness of all colors"""
        factor = value / 100.0
        self.adjust_all_colors('brightness', factor)
        
    def adjust_contrast(self, value):
        """Adjust contrast of all colors"""
        factor = value / 100.0
        self.adjust_all_colors('contrast', factor)
        
    def adjust_saturation(self, value):
        """Adjust saturation of all colors"""
        factor = value / 100.0
        self.adjust_all_colors('saturation', factor)
    
    def adjust_all_colors(self, adjustment_type, factor):
        """Adjust all colors based on the specified adjustment type"""
        for key, color in self.colors.items():
            qcolor = QColor(color)
            h, s, v = qcolor.getHsvF()[:3]
            
            if adjustment_type == 'brightness':
                v = max(0.0, min(1.0, v + factor))
            elif adjustment_type == 'contrast':
                v = max(0.0, min(1.0, ((v - 0.5) * (1 + factor)) + 0.5))
            elif adjustment_type == 'saturation':
                s = max(0.0, min(1.0, s + factor))
            
            qcolor.setHsvF(h, s, v)
            self.colors[key] = qcolor.name()
            
            # Update color pickers
            if key in self.bg_pickers:
                self.bg_pickers[key].current_color = qcolor
                self.bg_pickers[key].update_preview()
            elif key in self.accent_pickers:
                self.accent_pickers[key].current_color = qcolor
                self.accent_pickers[key].update_preview()
            elif key in self.text_pickers:
                self.text_pickers[key].current_color = qcolor
                self.text_pickers[key].update_preview()
            elif key == 'border':
                self.border_picker.current_color = qcolor
                self.border_picker.update_preview()
        
        self.update_theme()
    
    def color_changed(self, color_key: str, new_color: str):
        """Handle color change from any picker"""
        self.colors[color_key] = new_color
        self.update_theme()
    
    def update_theme(self):
        """Emit updated theme settings"""
        theme_settings = {
            'colors': self.colors,
            'border_radius': self.border_radius.value()
        }
        self.theme_updated.emit(theme_settings)
    
    def reset_to_default(self):
        """Reset all settings to default"""
        self.colors = self.dark_theme.COLORS.copy()
        self.brightness_slider.setValue(0)
        self.contrast_slider.setValue(0)
        self.saturation_slider.setValue(0)
        self.border_radius.setValue(3)
        self.update_theme()
        
        # Update all color pickers
        for key, picker in {**self.bg_pickers, **self.accent_pickers, 
                          **self.text_pickers, 'border': self.border_picker}.items():
            picker.current_color = QColor(self.colors[key])
            picker.update_preview()
    
    def load_preset(self, preset_name: str):
        """Load a predefined theme preset"""
        if preset_name == "Custom":
            return
            
        # Define preset colors
        presets = {
            "Dark": self.dark_theme.COLORS,  # Our current dark theme
            
            "Darker": {
                'bg_primary': '#1a1a1a',
                'bg_secondary': '#141414',
                'bg_tertiary': '#252525',
                'bg_hover': '#303030',
                'bg_pressed': '#0a0a0a',
                'bg_disabled': '#1c1c1c',
                'border': '#0a0a0a',
                'text_primary': '#ffffff',
                'text_secondary': '#aaaaaa',
                'text_disabled': '#666666',
                'accent_blue': '#528bff',
                'accent_select': '#3d6099',
                'accent_green': '#98c379',
                'accent_red': '#e06c75',
                'accent_yellow': '#e5c07b',
                'accent_orange': '#d19a66',
                'accent_purple': '#c678dd',
            },
            
            "Ocean": {
                'bg_primary': '#1b2b34',
                'bg_secondary': '#14232a',
                'bg_tertiary': '#263b44',
                'bg_hover': '#2d4048',
                'bg_pressed': '#0f1c22',
                'bg_disabled': '#1c2830',
                'border': '#0f1c22',
                'text_primary': '#d8dee9',
                'text_secondary': '#a7adba',
                'text_disabled': '#65737e',
                'accent_blue': '#6699cc',
                'accent_select': '#5fb3b3',
                'accent_green': '#99c794',
                'accent_red': '#ec5f67',
                'accent_yellow': '#fac863',
                'accent_orange': '#f99157',
                'accent_purple': '#c594c5',
            },
            
            "Forest": {
                'bg_primary': '#2d2f2d',
                'bg_secondary': '#1e211e',
                'bg_tertiary': '#373937',
                'bg_hover': '#424642',
                'bg_pressed': '#1a1d1a',
                'bg_disabled': '#2a2c2a',
                'border': '#1a1d1a',
                'text_primary': '#d3d9d3',
                'text_secondary': '#a5aca5',
                'text_disabled': '#6c736c',
                'accent_blue': '#83b97d',
                'accent_select': '#6a9b64',
                'accent_green': '#a8d193',
                'accent_red': '#e67e80',
                'accent_yellow': '#dbbc7f',
                'accent_orange': '#e69875',
                'accent_purple': '#b279a7',
            },
            
            "Purple": {
                'bg_primary': '#2d2b3b',
                'bg_secondary': '#1e1c2c',
                'bg_tertiary': '#373545',
                'bg_hover': '#423f50',
                'bg_pressed': '#1a1828',
                'bg_disabled': '#2a2838',
                'border': '#1a1828',
                'text_primary': '#d3d1e3',
                'text_secondary': '#a5a3b5',
                'text_disabled': '#6c6a7c',
                'accent_blue': '#a39fe5',
                'accent_select': '#8683c9',
                'accent_green': '#b1e3ad',
                'accent_red': '#e5a3a1',
                'accent_yellow': '#e3d1a3',
                'accent_orange': '#e5b3a1',
                'accent_purple': '#c9a3e5',
            },
            
            "Nord": {
                'bg_primary': '#2e3440',
                'bg_secondary': '#242933',
                'bg_tertiary': '#3b4252',
                'bg_hover': '#434c5e',
                'bg_pressed': '#1c2027',
                'bg_disabled': '#2b303b',
                'border': '#1c2027',
                'text_primary': '#eceff4',
                'text_secondary': '#d8dee9',
                'text_disabled': '#4c566a',
                'accent_blue': '#88c0d0',
                'accent_select': '#5e81ac',
                'accent_green': '#a3be8c',
                'accent_red': '#bf616a',
                'accent_yellow': '#ebcb8b',
                'accent_orange': '#d08770',
                'accent_purple': '#b48ead',
            }
        }
        
        if preset_name in presets:
            self.colors = presets[preset_name].copy()
            self.update_theme()
            
            # Update all color pickers
            for key, picker in {**self.bg_pickers, **self.accent_pickers, 
                              **self.text_pickers, 'border': self.border_picker}.items():
                picker.current_color = QColor(self.colors[key])
                picker.update_preview()
            
            # Reset sliders
            self.brightness_slider.setValue(0)
            self.contrast_slider.setValue(0)
            self.saturation_slider.setValue(0)
    
    def load_saved_themes(self):
        """Load saved themes into combo box"""
        # Add built-in presets
        self.preset_combo.clear()
        self.preset_combo.addItems(self.built_in_presets)
        
        # Add saved themes
        config = self.theme_config.load_all_themes()
        for theme_name in config['themes'].keys():
            if theme_name not in self.built_in_presets:
                self.preset_combo.addItem(theme_name)
        
        # Set current theme
        current = config.get('current_theme')
        if current:
            index = self.preset_combo.findText(current)
            if index >= 0:
                self.preset_combo.setCurrentIndex(index)
    
    def save_current_preset(self):
        """Save current theme as a new preset"""
        name, ok = QInputDialog.getText(
            self, 'Save Theme', 'Enter theme name:',
            text=self.preset_combo.currentText()
        )
        
        if ok and name:
            # Save theme
            self.theme_config.save_theme(
                name=name,
                colors=self.colors,
                border_radius=self.border_radius.value()
            )
            
            # Add to combo if new
            if self.preset_combo.findText(name) < 0:
                self.preset_combo.addItem(name)
            
            # Select the saved theme
            self.preset_combo.setCurrentText(name)
            
            QMessageBox.information(
                self, "Theme Saved",
                f"Theme '{name}' has been saved successfully!"
            )
    
    def delete_current_preset(self):
        """Delete the current preset"""
        current = self.preset_combo.currentText()
        
        # Don't allow deleting built-in presets
        if current in self.built_in_presets:
            QMessageBox.warning(
                self, "Cannot Delete",
                "Built-in presets cannot be deleted."
            )
            return
        
        reply = QMessageBox.question(
            self, "Delete Theme",
            f"Are you sure you want to delete the theme '{current}'?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.theme_config.delete_theme(current)
            self.preset_combo.removeItem(self.preset_combo.currentIndex())
            QMessageBox.information(
                self, "Theme Deleted",
                f"Theme '{current}' has been deleted."
            ) 