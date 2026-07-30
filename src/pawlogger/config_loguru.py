import functools
import sys
from pathlib import Path
from typing import Callable, Literal

import loguru
from loguru import logger

"""
functions for configuring loguru
"""

CATEGORY_COLORS = {}


def configure_loguru(
    level: str = 'INFO',
    log_file: Path | None = None,
    profile: Literal['local'] = 'local',
    color_dict: dict | None = None,
):
    """
    Configure loguru logger

    :param log_file: path to log file
    :param profile: log profile to use
    :param color_dict: dictionary of log-category to colour mappings
    :return: logger
    """
    if color_dict:
        color_dict = {k.lower(): v for k, v in color_dict.items()}
        global CATEGORY_COLORS
        CATEGORY_COLORS = color_dict

    if profile == 'local':
        logger.info('Using local log profile')
        terminal_format = log_fmt_local_terminal
    else:
        raise ValueError(f'Invalid profile: {profile}')

    logger.remove()

    lvl = level.upper()
    if log_file:
        logger.add(log_file, rotation='1 day', delay=True, encoding='utf8', level=lvl)
    logger.add(sys.stderr, level=lvl, format=terminal_format)


def logger_wraps(*, entries=True, exits=True, level='DEBUG') -> Callable:
    """
    Decorator to log function entry and exit

    :param entries: log entry
    :param exits: log exit
    :param level: log level
    :return: decorator
    """

    def wrapper(func):
        name = func.__name__

        @functools.wraps(func)
        def wrapped(*args, **kwargs):
            logger_ = logger.opt(depth=1)
            if entries:
                logger_.log(level, f"Entering '{name}' (args={args}, kwargs={kwargs})")
            result = func(*args, **kwargs)
            if exits:
                logger_.log(level, "Exiting '{}' (result={})", name, result)
            return result

        return wrapped

    return wrapper


def log_fmt_local_terminal(record: loguru.Record) -> str:
    lvltext = wrapped_fmt_str(f'{record["level"]: <7}', 'lvl')
    category = record['extra'].get('category', '')
    category = f'{category.title():<9}'
    color = CATEGORY_COLORS.get(category.lower(), None)
    if category:
        category = f' | {category}'
        if isinstance(color, str):
            category = f' | {wrapped_fmt_str(category, color)}'
    msg = wrapped_fmt_str(record['message'], 'lvl')
    msg = msg.replace('{', '{{').replace('}', '}}')
    link_path = f'{record["file"].path}:{record["line"]}'
    return f'{lvltext}{category} | {msg} | {link_path}\n'


def wrapped_fmt_str(msg: str, tag: str) -> str:
    """
    Wrap a message with a tag

    :param msg: message to wrap
    :param tag: tag to use
    :return: wrapped message
    """
    return f'<{tag}>{msg}</{tag}>'
