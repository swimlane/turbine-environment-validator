import os
import logging

def setup_logger():
    logger = logging.getLogger(__name__)

    # Remove any default log handlers
    # since we only want to log to stdout
    for handler in logger.handlers:
        logger.removeHandler(handler)

    # Set the log stream handlers for stdout
    handler = logging.StreamHandler()

    # Grab the logging level from environment var
    # if not found, et log level to warning
    
    # if config.arguments.debug:
    #     log_level = "DEBUG"
    # else:
    #     log_level = os.environ.get('LOG_LEVEL', 'INFO').upper()
    log_level = os.environ.get('LOG_LEVEL', 'INFO').upper()
    logger.setLevel(log_level)

    # Configure the format of the logs
    formatter = logging.Formatter('{%(pathname)s:%(lineno)d} %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)


    return logger