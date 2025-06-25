import logging
import sys

def setup_logger(name="hdt", level=logging.INFO):
    """
    Sets up a logger with console output and consistent formatting.

    Args:
        name (str): Name of the logger
        level (int): Logging level (e.g., logging.DEBUG, logging.INFO)

    Returns:
        logging.Logger
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Avoid duplicate handlers if re-initializing
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(
            "[%(asctime)s] [%(levelname)s] %(name)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger
