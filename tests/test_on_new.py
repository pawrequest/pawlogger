# ruff: noqa: F841
import logging
import uuid

import pytest

from loggingdecorators import on_new
from loggingdecorators.decorators import DFLT_LOGGER_STR

ARG1 = "value 1 for test"
KWARG2 = "keyword value 2 for test"
DFLT_KWARG2 = "default value kwarg 2"
DFLT_KWARG3 = "default value kwarg 3"


class DummyClass:
    def __new__(cls, arg1, kwarg2=DFLT_KWARG2, kwarg3=DFLT_KWARG3):
        return super().__new__(cls)


NEW_CLASS_MSG = f"new: {DummyClass.__name__}"


@pytest.fixture
def test_logger():
    logger_name = "test_logger_" + str(uuid.uuid4())
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.DEBUG)
    yield logger
    logger.handlers.clear()
    logger = None


def apply_decorator(cls, **decorator_kwargs):
    decorated_class = on_new(**decorator_kwargs)(cls)
    return decorated_class


def test_default_dec(caplog):
    decorated_test_class = apply_decorator(DummyClass)
    with caplog.at_level(logging.DEBUG, logger=DFLT_LOGGER_STR):
        instance = decorated_test_class(ARG1, kwarg2=KWARG2)  # noqa: F841
    msg = caplog.records[0].msg

    assert NEW_CLASS_MSG in msg
    assert ARG1 in msg
    assert KWARG2 in msg
    assert DFLT_KWARG2 not in msg
    assert DFLT_KWARG3 not in msg
    caplog.clear()


def test_with_logger_object(caplog, test_logger):
    decorated_test_class = apply_decorator(DummyClass, logger=test_logger)
    with caplog.at_level(logging.DEBUG, logger=test_logger.name):
        instance = decorated_test_class(ARG1, kwarg2=KWARG2)  # noqa: F841
    msg = caplog.records[0].msg
    assert NEW_CLASS_MSG in msg


def test_with_callable(caplog, test_logger):
    def logger_callable():
        return test_logger

    decorated_test_class = apply_decorator(DummyClass, logger=logger_callable)
    with caplog.at_level(logging.DEBUG, logger=test_logger.name):
        instance = decorated_test_class(ARG1)  # noqa: F841
    msg = caplog.records[0].msg
    assert NEW_CLASS_MSG in msg


def test_no_logargs(caplog, test_logger):
    caplog.clear()
    decorated_test_class = apply_decorator(DummyClass, logger=test_logger.name, logargs=False)
    with caplog.at_level(logging.DEBUG, logger=test_logger.name):
        instance = decorated_test_class(ARG1, kwarg2=KWARG2)  # noqa: F841
    msg = caplog.records[0].msg
    assert NEW_CLASS_MSG in msg
    assert ARG1 not in msg
    assert KWARG2 not in msg
    assert DFLT_KWARG2 not in msg
    assert DFLT_KWARG3 not in msg


def test_log_defaults(caplog, test_logger):
    caplog.clear()

    decorated_test_class = apply_decorator(DummyClass, logger=test_logger, logargs=True, logdefaults=True)
    with caplog.at_level(logging.DEBUG, logger=test_logger.name):
        instance = decorated_test_class(ARG1)  # noqa: F841

    msg = caplog.records[0].msg
    assert NEW_CLASS_MSG in msg
    assert ARG1 in msg
    assert DFLT_KWARG2 in msg
    assert DFLT_KWARG3 in msg


def test_invalid_logger(caplog, test_logger):
    with pytest.raises(TypeError):
        decorated_test_class = apply_decorator(DummyClass, logger=123)
        with caplog.at_level(logging.DEBUG, logger=test_logger.name):
            instance = decorated_test_class(ARG1)  # noqa: F841
