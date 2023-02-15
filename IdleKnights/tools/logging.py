__author__ = 'github.com/wardsimon'
__version__ = '0.0.1'

import logging
import sys
from logging.handlers import TimedRotatingFileHandler
from IdleKnights.constants import LOG_LEVEL
LOG_FILE = "my_app.log"


class CustomFormatter(logging.Formatter):
    """Logging colored formatter, adapted from https://stackoverflow.com/a/56944256/3638629"""

    grey = '\x1b[38;21m'
    blue = '\x1b[38;5;39m'
    yellow = '\x1b[38;5;226m'
    red = '\x1b[38;5;196m'
    bold_red = '\x1b[31;1m'
    reset = '\x1b[0m'

    def __init__(self, fmt):
        super().__init__()
        self.fmt = fmt
        self.FORMATS = {
            logging.DEBUG:    self.grey + self.fmt + self.reset,
            logging.INFO:     self.blue + self.fmt + self.reset,
            logging.WARNING:  self.yellow + self.fmt + self.reset,
            logging.ERROR:    self.red + self.fmt + self.reset,
            logging.CRITICAL: self.bold_red + self.fmt + self.reset
        }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)


FORMATTER = CustomFormatter("%(asctime)s — %(name)s — %(levelname)s — %(message)s")


def get_console_handler():
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(FORMATTER)
    return console_handler


def get_file_handler():
    file_handler = TimedRotatingFileHandler(LOG_FILE, when='midnight')
    file_handler.setFormatter(FORMATTER)
    return file_handler


def get_logger(logger_name, to_file=False):
    logger = logging.getLogger(logger_name)
    logger.setLevel(LOG_LEVEL)  # better to have too much log than not enough
    logger.addHandler(get_console_handler())
    if to_file:
        logger.addHandler(get_file_handler())
    # with this pattern, it's rarely necessary to propagate the error up to parent
    logger.propagate = False
    return logger


def set_level(level: int = logging.INFO):
    logging.getLogger().setLevel(level)
