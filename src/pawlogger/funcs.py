import copy
import json
import sys
from typing import Any

from loguru import logger


def remove_keys_from_dict(data: Any, keys_to_remove: set[str]) -> Any:
    """
    Recursively removes specified keys from a nested dictionaries.
    """

    data = copy.deepcopy(data)

    if isinstance(data, dict):
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


def serialize(record):
    timestamp = record['time'].strftime('%Y-%m-%dT%H:%M:%S.%fZ')
    exported = {'timestamp': timestamp, 'message': record['message'], **record['extra'], 'level': record['level'].name}
    return json.dumps(exported)


def serializing_formatter(record):
    # Note this function returns the string to be formatted, not the actual message to be logged
    record['extra']['serialized'] = serialize(record)
    return '{extra[serialized]}\n'


def configure_logging(ndjson_file):
    logger.remove()

    logger.add(ndjson_file, format=serializing_formatter)
    logger.add(sys.stderr, level='DEBUG', format=serializing_formatter)


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


if __name__ == '__main__':
    configure_logging('test.ndjson')
    extra = {
        'TEST': 'siomsoimnafhb',
    }
    logger.info('TESTIG', extra=extra)
