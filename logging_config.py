
import logging
import sys

def logging_config(logger_name = __name__, log_file='logger.log'):
    # Create a logger
    logger = logging.getLogger(logger_name)
    logger.propagate = False
    # Set the logging level to DEBUG (this will allow us to capture both INFO and DEBUG messages)
    logger.setLevel(logging.DEBUG)

    # Create a file handler to log DEBUG messages to a file
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.DEBUG)

    # Create a console handler to log INFO messages to the console
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)

    # Create a formatter and add it to the handlers
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    # Add the handlers to the logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger