# ruff: noqa: F841
import copy
import logging

import pytest

from pawlogger import on_new
from pawlogger import DFLT_LOGGER_STR, DFLT_LOG_LEVEL
from tests.loggingdecorators.conftest import ARG1, ARG2, DFLT_ARG1, DFLT_ARG2, DummyClass, NEW_MSG


def test_with_logger_object(caplog, test_logger, dummy_class_fxt):
    decorated_test_class = on_new(logger=test_logger)(DummyClass)
    with caplog.at_level(logging.DEBUG, logger=test_logger.name):
        instance = decorated_test_class(ARG1, arg2=ARG2)  # noqa: F841
    msg = caplog.records[0].msg
    assert NEW_MSG in msg
    caplog.clear()


def test_with_callable(caplog, test_logger):
    def logger_callable():
        return test_logger

    decorated_test_class = on_new(logger=logger_callable)(DummyClass)
    with caplog.at_level(logging.DEBUG, logger=test_logger.name):
        instance = decorated_test_class(ARG1, ARG2)  # noqa: F841
    msg = caplog.records[0].msg
    assert NEW_MSG in msg
    caplog.clear()


def test_no_logargs(caplog, test_logger):
    caplog.clear()
    decorated_test_class = on_new(logger=test_logger, logargs=False)(DummyClass)
    with caplog.at_level(DFLT_LOG_LEVEL, logger=test_logger.name):
        instance = decorated_test_class(ARG1, ARG2)  # noqa: F841
    msg = caplog.records[0].msg
    assert NEW_MSG in msg
    assert ARG1 not in msg
    assert ARG2 not in msg
    assert DFLT_ARG1 not in msg
    assert DFLT_ARG2 not in msg
    caplog.clear()


def test_default_dec(caplog, test_logger):
    dummy = copy.copy(DummyClass)
    decorated_test_class = on_new()(dummy)
    with caplog.at_level(logging.DEBUG, logger=DFLT_LOGGER_STR):
        instance = decorated_test_class(ARG1, ARG2)  # noqa: F841
    msg = caplog.records[-1].msg

    assert NEW_MSG in msg
    assert ARG1 in msg
    assert ARG2 in msg
    assert DFLT_ARG1 not in msg
    assert DFLT_ARG2 not in msg
    caplog.clear()


def test_invalid_logger(caplog, test_logger):
    dummy = copy.copy(DummyClass)
    with pytest.raises(TypeError):
        decorated_test_class = on_new(logger=123)(dummy)
        with caplog.at_level(logging.DEBUG, logger=test_logger.name):
            instance = decorated_test_class(ARG1)  # noqa: F841
            caplog.clear()
