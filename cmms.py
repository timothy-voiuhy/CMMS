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
    """Create log files with timestamps"""
    gui_log_file = os.path.join(LOGS_DIR, f"gui_{time.strftime('%Y-%m-%d-%H-%M-%S')}.log") 
    console_log_file = os.path.join(LOGS_DIR, f"console_{time.strftime('%Y-%m-%d-%H-%M-%S')}.log")
    db_log_file = os.path.join(LOGS_DIR, f"db_{time.strftime('%Y-%m-%d-%H-%M-%S')}.log")
    credentials_log_file = os.path.join(LOGS_DIR, f"credentials_{time.strftime('%Y-%m-%d-%H-%M-%S')}.log")
    scheduler_log_file = os.path.join(LOGS_DIR, f"scheduler_{time.strftime('%Y-%m-%d-%H-%M-%S')}.log")
    
    open(gui_log_file, "w").close()
    open(console_log_file, "w").close()
    open(db_log_file, "w").close()
    open(credentials_log_file, "w").close()
    open(scheduler_log_file, "w").close()

    return gui_log_file, console_log_file, db_log_file, credentials_log_file, scheduler_log_file

def initializeApplication():
    """Initialize application directories and components"""
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
    """Main application entry point"""
    initializeApplication()
    
    # create necessary loggers 
    GUI_LOG_FILE, CONSOLE_LOG_FILE, DB_LOG_FILE, CREDENTIALS_LOG_FILE, SCHEDULER_LOG_FILE = create_log_files()
    console_logger = createLogger(is_consoleLogger=True, log_level=logging.INFO, name="console")
    gui_logger = createLogger(log_level=logging.INFO, filename=GUI_LOG_FILE, name="gui")
    console_logger = createLogger(log_level=logging.INFO, filename=CONSOLE_LOG_FILE, name="console")
    db_logger = createLogger(log_level=logging.INFO, filename=DB_LOG_FILE, name="db")
    credentials_logger = createLogger(log_level=logging.INFO, filename=CREDENTIALS_LOG_FILE, name="credentials")
    scheduler_logger = createLogger(log_level=logging.INFO, filename=SCHEDULER_LOG_FILE, name="maintenance_scheduler")

    try:
        app = QApplication(sys.argv)
        
        # Create and show main window
        main_window = CMMSMainWindow()
        main_window.setWindowState(Qt.WindowState.WindowMaximized)
        main_window.show()
        
        # Run the application
        result = app.exec()
        
        # Clean up before exit
        scheduler_logger.info("Stopping maintenance scheduler...")
        main_window.scheduler.stop()
        
        sys.exit(result)
        
    except Exception as e:
        console_logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()