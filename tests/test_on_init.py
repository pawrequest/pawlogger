# tests_on_init.py
import logging
import uuid

import pytest
from loggingdecorators import on_init  # Adjust the import according to your project structure

DFLT_LOGGER_STR = "logger"  # Default logger string
INIT_CLASS_MSG = "init: DummyClass"  # Message pattern to look for in logs


class DummyClass:
    def __init__(self, arg1, arg2=None):
        self.arg1 = arg1
        self.arg2 = arg2


@pytest.fixture
def test_logger():
    logger_name = "test_logger_" + str(uuid.uuid4())
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.DEBUG)
    yield logger
    logger.handlers.clear()
    logger = None


def apply_decorator(cls, **decorator_kwargs):
    decorated_class = on_init(**decorator_kwargs)(cls)
    return decorated_class


def test_on_init_with_string_logger(caplog):
    decorated_test_class = apply_decorator(DummyClass, logger=DFLT_LOGGER_STR, logargs=True)
    with caplog.at_level(logging.DEBUG, logger=DFLT_LOGGER_STR):
        instance = decorated_test_class('arg1_value', arg2='arg2_value')  # noqa: F841
    msg = caplog.records[0].msg

    assert INIT_CLASS_MSG in msg
    assert 'arg1_value' in msg
    assert 'arg2_value' in msg
    caplog.clear()


def test_on_init_with_logger_instance(caplog, test_logger):
    decorated_test_class = apply_decorator(DummyClass, logger=test_logger, logargs=True)
    with caplog.at_level(logging.DEBUG, logger=test_logger.name):
        instance = decorated_test_class('arg1_value')  # noqa: F841
    msg = caplog.records[0].msg

    assert INIT_CLASS_MSG in msg
    assert 'arg1_value' in msg
    assert 'arg2' not in msg  # arg2 is not provided, should not be logged
    caplog.clear()


def test_on_init_without_logargs(caplog, test_logger):
    decorated_test_class = apply_decorator(DummyClass, logger=test_logger.name, logargs=False)
    with caplog.at_level(logging.DEBUG, logger=test_logger.name):
        instance = decorated_test_class('arg1_value', arg2='arg2_value')  # noqa: F841
    msg = caplog.records[0].msg

    assert INIT_CLASS_MSG in msg
    assert 'arg1_value' not in msg
    assert 'arg2_value' not in msg
    caplog.clear()

# Additional tests can include testing the depth parameter, handling of exceptions, and other edge cases.
