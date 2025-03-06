from PySide6.QtWidgets import QApplication
import sys
import os
import time
from PySide6.QtCore import QTimer, Qt

from main_window import CMMSMainWindow
from utils import createLogger
from config import LOGS_DIR, PROJECT_DIR, DB_DIR, DATA_DIR, TMP_DIR, CREDENTIALS_DIR
import logging

def create_log_files():
    gui_log_file = os.path.join(LOGS_DIR, f"gui_{time.strftime('%Y-%m-%d-%H-%M-%S')}.log") 
    console_log_file = os.path.join(LOGS_DIR, f"console_{time.strftime('%Y-%m-%d-%H-%M-%S')}.log")
    db_log_file = os.path.join(LOGS_DIR, f"db_{time.strftime('%Y-%m-%d-%H-%M-%S')}.log")
    credentials_log_file = os.path.join(LOGS_DIR, f"credentials_{time.strftime('%Y-%m-%d-%H-%M-%S')}.log")
    
    open(gui_log_file, "w").close()
    open(console_log_file, "w").close()
    open(db_log_file, "w").close()
    open(credentials_log_file, "w").close()

    return gui_log_file, console_log_file, db_log_file, credentials_log_file

def initializeApplication():
    # Create directories if they don't exist
    os.makedirs(PROJECT_DIR, exist_ok=True)
    os.makedirs(DATA_DIR, exist_ok=True)
    os.makedirs(DB_DIR, exist_ok=True)
    os.makedirs(TMP_DIR, exist_ok=True)
    os.makedirs(LOGS_DIR, exist_ok=True)
    os.makedirs(CREDENTIALS_DIR, exist_ok=True)

    # create log files
    create_log_files()

def main():
    initializeApplication()
    # create necessary loggers 
    GUI_LOG_FILE, CONSOLE_LOG_FILE, DB_LOG_FILE, CREDENTIALS_LOG_FILE = create_log_files()
    console_logger = createLogger(is_consoleLogger=True, log_level=logging.INFO, name="console")
    gui_logger = createLogger(log_level=logging.INFO, filename=GUI_LOG_FILE, name="gui")
    console_logger = createLogger(log_level=logging.INFO, filename=CONSOLE_LOG_FILE, name="console")
    db_logger = createLogger(log_level=logging.INFO, filename=DB_LOG_FILE, name="db")
    credentials_logger = createLogger(log_level=logging.INFO, filename=CREDENTIALS_LOG_FILE, name="credentials")

    app = QApplication(sys.argv)
    main_window = CMMSMainWindow()
    
    # Force maximize using both approaches
    main_window.setWindowState(Qt.WindowState.WindowMaximized)
    main_window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()