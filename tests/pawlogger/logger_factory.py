import logging

from pawlogger import configure_logging


def get_logger(log_file, level=logging.DEBUG):
    return configure_logging(log_file=log_file, level=level)
