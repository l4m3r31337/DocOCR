import logging
import sys

def setup_logging(log_level='INFO', log_file=None):
    logger = logging.getLogger("DocProcessor")
    logger.setLevel(getattr(logging, log_level.upper()))
    logger.handlers.clear()
    
    # Только консоль
    handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter('%(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    
    return logger