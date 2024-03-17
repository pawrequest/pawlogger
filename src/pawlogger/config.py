"""
logging configuration for builtin logger
"""
import inspect
import logging

from . import consts


def get_logger(logger_name=None, log_file=None, level=logging.DEBUG):
    """
    Configure logging

    :param logger_name: name of logger
    :param log_file: path to log file
    :param level: logging level
    :return: logger
    """
    if logger_name is None:
        frame = inspect.stack()[1]
        module = inspect.getmodule(frame[0])
        logger_name = module.__name__ if module else '__main__'

    if log_file is None:
        log_file = f'{logger_name}.log'

    logger = logging.getLogger(logger_name)
    logger.setLevel(level)

    file_handler = logging.FileHandler(log_file)
    console_handler = logging.StreamHandler()

    file_formatter = logging.Formatter(consts.FILE_FORMAT_STR, style='{')
    console_formatter = logging.Formatter(consts.CONSOLE_FORMAT_STR, style='{')

    file_handler.setFormatter(file_formatter)
    console_handler.setFormatter(console_formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    logger.debug(f'Logger created: {logger.name}')

    return logger
