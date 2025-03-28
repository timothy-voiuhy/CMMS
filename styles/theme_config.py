import json
import os
from typing import Dict, Optional
from config import DATA_DIR, THEME_CONFIG_FILE

class ThemeConfig:
    """Manages theme configuration saving and loading"""
    
    def __init__(self):
        self.config_file = THEME_CONFIG_FILE
        self._ensure_config_dir()
    
    def _ensure_config_dir(self):
        """Ensure the theme config directory exists"""
        os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
    
    def save_theme(self, name: str, colors: Dict[str, str], border_radius: int, font_size: int = None):
        """Save a theme configuration"""
        config = self.load_all_themes()
        
        # Add or update theme
        config['themes'][name] = {
            'colors': colors,
            'border_radius': border_radius,
            'font_size': font_size if font_size is not None else 10  # Default font size
        }
        
        # Update current theme
        config['current_theme'] = name
        
        with open(self.config_file, 'w') as f:
            json.dump(config, f, indent=4)
    
    def load_all_themes(self) -> Dict:
        """Load all saved themes"""
        if not os.path.exists(self.config_file):
            return {
                'themes': {},
                'current_theme': None,
                'global_font_size': 10  # Default global font size
            }
        
        try:
            with open(self.config_file, 'r') as f:
                config = json.load(f)
                # Ensure backward compatibility
                if 'global_font_size' not in config:
                    config['global_font_size'] = 10
                return config
        except Exception:
            return {
                'themes': {},
                'current_theme': None,
                'global_font_size': 10
            }
    
    def get_current_theme(self) -> Optional[Dict]:
        """Get the currently selected theme"""
        config = self.load_all_themes()
        current = config.get('current_theme')
        if current:
            theme_data = config['themes'].get(current)
            if theme_data and 'font_size' not in theme_data:
                theme_data['font_size'] = config.get('global_font_size', 10)
            return theme_data
        return None
    
    def delete_theme(self, name: str):
        """Delete a saved theme"""
        config = self.load_all_themes()
        if name in config['themes']:
            del config['themes'][name]
            if config['current_theme'] == name:
                config['current_theme'] = None
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=4)
    
    def save_global_font_size(self, size: int):
        """Save the global font size setting"""
        config = self.load_all_themes()
        config['global_font_size'] = size
        with open(self.config_file, 'w') as f:
            json.dump(config, f, indent=4)
    
    def get_global_font_size(self) -> int:
        """Get the global font size setting"""
        config = self.load_all_themes()
        return config.get('global_font_size', 10)