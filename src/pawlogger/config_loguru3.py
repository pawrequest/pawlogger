from __future__ import annotations

import functools
import json
import sys
from datetime import timedelta
from pathlib import Path
from typing import Callable
from loguru import logger


def loguru_ndjson_and_terminal(
        level: str = 'INFO',
        log_file: Path | None = None,
        rotation: timedelta = timedelta(weeks=1),
        retention: timedelta = timedelta(weeks=8),
):
    logger.remove()
    lvl = level.upper()

    config = dict(
        level=lvl.upper(),
        rotation=rotation,
        retention=retention,
        delay=True,
        encoding='utf8',
    )

    if log_file:
        log_file_ndjson = log_file.with_suffix('.ndjson')
        log_file_ndjson.parent.mkdir(parents=True, exist_ok=True)
        log_file_ndjson.touch(exist_ok=True)
        logger.add(log_file_ndjson, format=serializing_formatter, **config)
    logger.add(sys.stdout, level=lvl, format=log_fmt_local_terminal)
    # logger.add(sys.stderr, level=lvl, format=log_fmt_local_terminal)
    logger.info(f'Configured loguru with level {lvl} and log_file {log_file}')


def log_fmt_local_terminal(record) -> str:
    name_txt = f'<lvl>{record["name"].split(".")[0]}</lvl>'
    lvltext = f'<lvl>{record["level"]}</lvl>'
    msg_txt = f'<lvl>{record["message"]}</lvl>'
    file_txt = f'"{record["file"].path}:{record["line"]}"'
    msg_txt = msg_txt.replace('{', '{{').replace('}', '}}')
    return f'{name_txt}({lvltext}) | {msg_txt} | {file_txt}\n'


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
                logger_.log(level, f"Exiting '{name}' (result={result})")
            return result

        return wrapped

    return wrapper


def serialize(record):
    timestamp = record['time'].strftime('%Y-%m-%dT%H:%M:%S.%fZ')
    exported = {
        'timestamp': timestamp,
        'level': record['level'].name,
        'name': record['name'],
        'message': record['message'],
        **record['extra'],
    }
    return json.dumps(exported)


def serializing_formatter(record):
    # Note this function returns the string to be formatted, not the actual message to be logged
    record['extra']['serialized'] = serialize(record)
    return '{extra[serialized]}\n'


if __name__ == '__main__':
    loguru_ndjson_and_terminal(level='DEBUG', log_file=Path('test_logger.log'))
    logger.info('Test loguru configuration')
    logger.warning('This is a warning message', extra={'a': 'b'})
