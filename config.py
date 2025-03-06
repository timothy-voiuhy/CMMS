"""
Configuration settings for the CMMS application.
"""

import os
import platform
import json

if platform.system() == "Windows":
    BASE_DIR = os.path.join(os.getenv('APPDATA'), "CMMS")
else:
    BASE_DIR = os.path.join(os.path.expanduser("~"), ".cmms")

PROJECT_DIR = BASE_DIR
DATA_DIR = os.path.join(PROJECT_DIR, "data")
DB_DIR = os.path.join(DATA_DIR, "db")
DB_CREDENTIALS_FILE = os.path.join(DB_DIR, "credentials.json")
DB_FILE = os.path.join(DB_DIR, "cmms.db")
TMP_DIR = os.path.join(PROJECT_DIR, "tmp")
TMP_DB_FILE = os.path.join(TMP_DIR, "cmms.db")
LOGS_DIR = os.path.join(PROJECT_DIR, "logs")
LOGS_FILE = os.path.join(LOGS_DIR, "cmms.log")
CREDENTIALS_DIR = os.path.join(PROJECT_DIR, "credentials")
CREDENTIALS_FILE = os.path.join(CREDENTIALS_DIR, "credentials.json")
MODELS_DIR = os.path.join(PROJECT_DIR, "Models")

APP_STYLE_SHEET_FILE = os.path.join(DATA_DIR, "app_stylesheet.css")
CLOSED_POSITIONS_FILE = os.path.join(TMP_DIR, "closed_positions.json")

GOOGLEDRIVE_CREDENTIALS_FILE = os.path.join(CREDENTIALS_DIR, "client_secrets.json")
GOOGLEDRIVE_TOKENPICKLE_FLIE = os.path.join(CREDENTIALS_DIR, "token.pickle")
SETTINGS_FILE = os.path.join(DATA_DIR, "settings.json")
WORK_ORDER_SETTINGS_FILE = os.path.join(DATA_DIR, "work_order_settings.json")
# Add to existing paths
THEME_CONFIG_FILE = os.path.join(DATA_DIR, "theme_config.json")

# Application directories
APP_DIR = os.path.dirname(os.path.abspath(__file__))
SETTINGS_DIR = os.path.join(os.path.expanduser("~"), ".cmms")
REPORTS_DIR = os.path.join(os.path.expanduser("~"), "CMMS_Reports")

# Ensure directories exist
os.makedirs(SETTINGS_DIR, exist_ok=True)
os.makedirs(REPORTS_DIR, exist_ok=True)

# Default settings
DEFAULT_WORK_ORDER_SETTINGS = {
    'notifications': {
        'new_work_orders': True,
        'work_order_updates': True,
        'approaching_due_dates': True,
        'due_date_days': 2
    },
    'assignment': {
        'auto_assign': False,
        'assignment_method': 'Based on workload'
    },
    'defaults': {
        'priority': 'Medium'
    },
    'email': {
        'enabled': False,
        'server': '',
        'port': '587',
        'username': '',
        'password': '',
        'from_address': ''
    }
}

def load_work_order_settings():
    """Load work order settings from file or create with defaults if not exists"""
    try:
        if os.path.exists(WORK_ORDER_SETTINGS_FILE):
            with open(WORK_ORDER_SETTINGS_FILE, 'r') as f:
                settings = json.load(f)
                
            # Ensure all required settings exist by merging with defaults
            merged_settings = DEFAULT_WORK_ORDER_SETTINGS.copy()
            
            # Update top-level sections
            for section in merged_settings:
                if section in settings:
                    merged_settings[section].update(settings[section])
            
            return merged_settings
        else:
            # Create default settings file
            with open(WORK_ORDER_SETTINGS_FILE, 'w') as f:
                json.dump(DEFAULT_WORK_ORDER_SETTINGS, f, indent=4)
            
            return DEFAULT_WORK_ORDER_SETTINGS
    except Exception as e:
        print(f"Error loading work order settings: {e}")
        return DEFAULT_WORK_ORDER_SETTINGS

def save_work_order_settings(settings):
    """Save work order settings to file"""
    try:
        with open(WORK_ORDER_SETTINGS_FILE, 'w') as f:
            json.dump(settings, f, indent=4)
        return True
    except Exception as e:
        print(f"Error saving work order settings: {e}")
        return False

