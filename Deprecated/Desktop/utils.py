import logging
import random
import sys

import colorlog


def createLogger(log_level = None, name = None, mode = 'a', log_format = None, is_consoleLogger = False, filename = None):
    """
    Creates a logger object with the specified parameters.
    Parameters:
        log_level: The level of logging to be used. Defaults to logging.INFO
        name: The name of the logger. Defaults to a random number between 1 and 100
        mode: The mode of the file handler. Defaults to 'a'
        log_format: The format of the log message. Defaults to "%(asctime)s -%(levelname)s - %(filename)s:%(lineno)d - %(message)s"
        is_consoleLogger: Whether to log to the console. Defaults to False
        filename: The filename to be used for the file handler. Defaults to None
    """
    if log_level is None:
        log_level = logging.INFO
    if log_format is None:
        log_format = "%(asctime)s -%(levelname)s - %(filename)s:%(lineno)d - %(message)s"
    if name is None:
        name = "logger"+str(random.randint(1,100)) if not is_consoleLogger else __name__
    
    logger = logging.getLogger(name)

    if is_consoleLogger:
        # Color format for console
        color_format = "%(log_color)s" + log_format
        handler = colorlog.StreamHandler()
        handler.setFormatter(colorlog.ColoredFormatter(
            color_format,
            log_colors={
                'DEBUG':    'cyan',
                'INFO':     'green',
                'WARNING': 'yellow',
                'ERROR':   'red',
                'CRITICAL': 'red,bg_white',
            }
        ))
    else:
        if filename is None:
            filename = sys.executable.rstrip(".py")+".log"
        handler = logging.FileHandler(filename=filename, mode=mode)
        handler.setFormatter(logging.Formatter(log_format))
    
    handler.setLevel(log_level)
    logger.addHandler(handler)
    logger.setLevel(log_level)
    
    return logger