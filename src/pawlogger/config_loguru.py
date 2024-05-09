from __future__ import annotations

import functools
import sys
from typing import Literal

import loguru
from loguru import logger

"""
functions for configuring loguru
"""
CAT_COLOR_DICT = {
    'episode': 'cyan',
    'reddit': 'green',
    'backup': 'magenta',
}


def get_loguru(
        log_file, profile: Literal['local', 'remote', 'default'] = 'local',
        color_dict: dict | None = None
) -> logger:
    """
    Configure loguru logger

    :param log_file: path to log file
    :param profile: log profile to use
    :param color_dict: dictionary of log-category to colour mappings
    :return: logger
    """
    if color_dict:
        global CAT_COLOR_DICT
        CAT_COLOR_DICT = color_dict

    if profile == 'local':
        logger.info('Using local log profile')
        terminal_format = log_fmt_local_terminal
    elif profile == 'remote':
        logger.info('Using remote log profile')
        terminal_format = log_fmt_server_terminal
    else:
        raise ValueError(f'Invalid profile: {profile}')

    logger.remove()

    logger.add(log_file, rotation='1 day', delay=True, encoding='utf8')
    logger.add(sys.stderr, level='DEBUG', format=terminal_format)

    return logger


# def log_fmt_local_terminal(record) -> str:
#     """
#     Format for local logging
# 
#     :param record: log record
#     :return: formatted log record
#     """
#     category = record['extra'].get('category', 'General')
#     bot_colour = BOT_COLOR.get(category, 'white')
#     category = f'{category:<9}'
#     max_length = 100
#     file_txt = f"{record['file'].path}:{record['line']}"
# 
#     if len(file_txt) > max_length:
#         file_txt = file_txt[:max_length]
# 
#     # clickable link only works at start of line
#     return f"{file_txt:<{max_length}} | <lvl>{record['level']: <7} | {coloured(category, bot_colour)} | {record['message']}</lvl>\n"


def log_fmt_local_terminal(record: loguru.Record) -> str:
    file_txt = f"{record['file'].path}:{record['line']}"

    category = record['extra'].get('category', 'General')
    category_txt = f'{category.title():<9}'

    color = CAT_COLOR_DICT.get(category.lower(), 'white')
    category_txt = f'| {coloured(category_txt, color)}' if category_txt != 'General' else ''
    lvltext = f'<lvl>{record['level']: <7}</lvl>'
    msg_txt = f'<lvl>{record['message']}</lvl>'
    # msg_txt = f'{record['message']}'
    return f'{lvltext} {category_txt} | {msg_txt} | {file_txt}\n'


def coloured(msg: str, colour: str) -> str:
    """
    Colour a message

    :param msg: message to colour
    :param colour: colour to use
    :return: coloured message
    """
    return f'<{colour}>{msg}</{colour}>'


def log_fmt_server_terminal(record) -> str:
    """
    Format for server-side logging

    :param record: log record
    :return: formatted log record
    """
    category = record['extra'].get('category', 'General')
    category = f'{category:<9}'
    colour = CAT_COLOR_DICT.get(category, 'white')

    file_line = f"{record['file']}:{record['line']}- {record['function']}()"
    bot_says = f"<bold>{coloured(category, colour):<9} </bold> | {coloured(record['message'], colour)}"

    return f"<lvl>{record['level']: <7} </lvl>| {bot_says} | {file_line}\n"


def logger_wraps(*, entries=True, exits=True, level='DEBUG') -> callable:
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
