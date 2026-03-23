from __future__ import annotations

import functools
import sys
from pathlib import Path
from typing import Callable

import loguru


def configure_loguru(
    logger_: loguru.Logger = None,
    level: str = 'INFO',
    log_file: Path | None = None,
) -> loguru.Logger:
    if logger is None:
        from loguru import logger as logger_
    logger_.remove()
    lvl = level.upper()
    if log_file:
        logger_.add(log_file, rotation='1 day', delay=True, encoding='utf8', level=lvl)
    logger_.add(sys.stderr, level=lvl, format=log_fmt_local_terminal)

    return logger_


def log_fmt_local_terminal(record: loguru.Record) -> str:
    file_txt = f'{record["file"].path}:{record["line"]}'
    lvltext = f'<lvl>{record["level"]: <7}</lvl>'
    msg_txt = f'<lvl>{record["message"]}</lvl>'
    msg_txt = msg_txt.replace('{', '{{').replace('}', '}}')
    # msg_txt = f'{record['message']}'
    return f'{file_txt} | {lvltext} | {msg_txt} \n'


def logger_wraps(*, entries=True, exits=True, level='DEBUG') -> Callable:
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


if __name__ == '__main__':
    from loguru import logger

    configure_loguru(logger, level='DEBUG')
    logger.debug('Configured loguru')
