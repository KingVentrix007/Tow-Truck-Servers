import logging
def setup_logging(log_file):
    """Setup logging configuration."""
    logging.basicConfig(filename=log_file, level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
def log(*args):
    """Log a message."""
    message = ' '.join(map(str, args))
    logging.info(message)

setup_logging("./logs/debug.log")