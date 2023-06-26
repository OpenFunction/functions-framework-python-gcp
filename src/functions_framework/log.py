import logging


def initialize_logger(name=None, level=logging.DEBUG):
    if not name:
        name = __name__
    _logger = logging.getLogger(name)

    # set logger level
    _logger.setLevel(level)

    # create file handler
    file_handler = logging.FileHandler("function.log")
    file_handler.setLevel(level)

    # create console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)

    # create formatter
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

    # add formatter to handlers
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    # add handlers to logger
    _logger.addHandler(file_handler)
    _logger.addHandler(console_handler)

    return _logger


# initialize logger
logger = initialize_logger(__name__, logging.INFO)

# test logger
logger.debug("This is a debug message")
logger.info("This is an info message")
logger.warning("This is a warning message")
logger.error("This is an error message")
