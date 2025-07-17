import logging
import os
from datetime import datetime

_logger = None

def setup_logger(config=None):
    global _logger
    if _logger is not None:
        return _logger

    _logger = logging.getLogger('S1-Space')
    _logger.setLevel(config.get('level', 'INFO') if config else 'INFO')
    _logger.propagate = False

    # Console handler
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    _logger.addHandler(handler)

    # File handler
    log_dir = 'results/logs'
    os.makedirs(log_dir, exist_ok=True)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    log_file = os.path.join(log_dir, f'run_{timestamp}.log')
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    _logger.addHandler(file_handler)

    _logger.info("Logger setup completed")
    return _logger

def get_logger():
    global _logger
    if _logger is None:
        setup_logger()
    return _logger 