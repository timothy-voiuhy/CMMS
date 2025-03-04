from PySide6.QtWidgets import QApplication
import sys

from main_window import CMMSMainWindow
from utils import createLogger
import logging

def initialize_loggers():
    console_logger = createLogger(is_consoleLogger=True, log_level=logging.DEBUG)
    file_logger = createLogger(filename="cmms.log", log_level=logging.DEBUG)

def main():
    app = QApplication(sys.argv)
    main_window = CMMSMainWindow()
    main_window.showMaximized()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()