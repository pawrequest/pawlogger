import copy
import sys
from typing import Any

from loguru import logger


def remove_keys_from_dict(data: Any, keys_to_remove: set[str] | None = None) -> Any:
    """
    Recursively removes specified keys from a nested dictionaries.
    """

    data = copy.deepcopy(data)

    if isinstance(data, dict) and keys_to_remove:
        for key in list(data.keys()):
            if key in keys_to_remove:
                logger.warning(f'Removing key: {key}')
                del data[key]
            else:
                data[key] = remove_keys_from_dict(data[key], keys_to_remove)
    elif isinstance(data, list):
        data = [remove_keys_from_dict(item, keys_to_remove) for item in data]
    elif isinstance(data, tuple):
        data = tuple(remove_keys_from_dict(item, keys_to_remove) for item in data)
    elif isinstance(data, set):
        data = {remove_keys_from_dict(item, keys_to_remove) for item in data}

    return data


def configure_logging(ndjson_file):
    logger.remove()

    logger.add(
        sys.stderr,
        level='DEBUG',
        format='{time:YYYY-MM-DD HH:mm:ss} | {level} | {message} | {extra}',
    )

    logger.add(
        ndjson_file,
        level='DEBUG',
        serialize=True,
        rotation='10 MB',
        retention=10,
    )


def normalize_log_value(value: Any) -> Any:
    if isinstance(value, dict):
        return remove_keys_from_dict(value)
    if isinstance(value, (list, tuple, set)):
        return [normalize_log_value(v) for v in value]
    return value


def log_event(message: str, *, level: str = 'INFO', event: str | None = None, **fields: Any):
    fields = {k: normalize_log_value(v) for k, v in fields.items()}
    if event is not None:
        fields['event'] = event
    logger.bind(**fields).log(level.upper(), message)
