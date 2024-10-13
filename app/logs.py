import logging
from logging.handlers import RotatingFileHandler
import sys

def setup_logger():
    logger = logging.getLogger(__name__)

    # Check if the logger already has handlers to avoid duplicate logs
    if not logger.hasHandlers():
        logger.setLevel(logging.DEBUG)

        # Create console handler and set level to INFO
        ch = logging.StreamHandler(sys.stdout)
        ch.setLevel(logging.INFO)

        # Create file handler and set level to DEBUG
        fh = RotatingFileHandler('app.log', maxBytes=1000000, backupCount=5)
        fh.setLevel(logging.DEBUG)

        # Create formatter
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

        # Add formatter to ch and fh
        ch.setFormatter(formatter)
        fh.setFormatter(formatter)

        # Add handlers to logger
        logger.addHandler(ch)
        logger.addHandler(fh)

    return logger
