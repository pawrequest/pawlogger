# ruff: noqa: F841
import copy
import logging

import pytest

from src.loggingdecorators import on_new
from tests.conftest import ARG1, ARG2, DFLT_ARG1, DFLT_ARG2


class DummyClass:
    def __new__(cls, arg1, kwarg2=DFLT_ARG1, kwarg3=DFLT_ARG2):
        return super().__new__(cls)


NEW_CLASS_MSG = f"new: {DummyClass.__name__}"


def apply_decorator(cls, **decorator_kwargs):
    decorated_class = on_new(**decorator_kwargs)(cls)
    return decorated_class


def test_with_logger_object(caplog, test_logger):
    decorated_test_class = apply_decorator(DummyClass, logger=test_logger)
    with caplog.at_level(logging.DEBUG, logger=test_logger.name):
        instance = decorated_test_class(ARG1, kwarg2=ARG2)  # noqa: F841
    msg = caplog.records[0].msg
    assert NEW_CLASS_MSG in msg
    caplog.clear()


def test_with_callable(caplog, test_logger):
    def logger_callable():
        return test_logger

    decorated_test_class = apply_decorator(DummyClass, logger=logger_callable)
    with caplog.at_level(logging.DEBUG, logger=test_logger.name):
        instance = decorated_test_class(ARG1)  # noqa: F841
    msg = caplog.records[0].msg
    assert NEW_CLASS_MSG in msg
    caplog.clear()


def test_no_logargs(caplog, test_logger):
    caplog.clear()
    decorated_test_class = apply_decorator(DummyClass, logger=test_logger.name, logargs=False)
    with caplog.at_level(logging.DEBUG, logger=test_logger.name):
        instance = decorated_test_class(ARG1, kwarg2=ARG2)  # noqa: F841
    msg = caplog.records[0].msg
    assert NEW_CLASS_MSG in msg
    assert ARG1 not in msg
    assert ARG2 not in msg
    assert DFLT_ARG1 not in msg
    assert DFLT_ARG2 not in msg
    caplog.clear()


def test_log_defaults(caplog, test_logger):
    caplog.clear()

    decorated_test_class = apply_decorator(DummyClass, logger=test_logger, logargs=True,
                                           logdefaults=True)
    with caplog.at_level(logging.DEBUG, logger=test_logger.name):
        instance = decorated_test_class(ARG1)  # noqa: F841

    msg = caplog.records[0].msg
    assert NEW_CLASS_MSG in msg
    assert ARG1 in msg
    assert DFLT_ARG1 in msg
    assert DFLT_ARG2 in msg
    caplog.clear()
    caplog.messages.clear()


def test_default_dec(caplog, test_logger):
    dummy = copy.copy(DummyClass)
    decorated_test_class = apply_decorator(dummy)
    with caplog.at_level(logging.DEBUG, logger=test_logger.name):
        instance = decorated_test_class(ARG1, kwarg2=ARG2)  # noqa: F841
    msg = caplog.records[-1].msg

    assert NEW_CLASS_MSG in msg
    assert ARG1 in msg
    assert ARG2 in msg
    assert DFLT_ARG1 not in msg
    assert DFLT_ARG2 not in msg
    caplog.clear()


def test_invalid_logger(caplog, test_logger):
    dummy = copy.copy(DummyClass)
    with pytest.raises(TypeError):
        decorated_test_class = apply_decorator(dummy, logger=123)
        with caplog.at_level(logging.DEBUG, logger=test_logger.name):
            instance = decorated_test_class(ARG1)  # noqa: F841
            caplog.clear()
