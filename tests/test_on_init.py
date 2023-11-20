import logging

import pytest

from loggingdecorators import on_init
from loggingdecorators.decorators import DFLT_LOGGER_STR
from tests.conftest import ARG1, DFLT_KWARG2, KWARG2


class DummyClass:
    def __init__(self, arg1, arg2=DFLT_KWARG2):
        self.arg1 = arg1
        self.arg2 = arg2


INIT_CLASS_MSG = f"init: {DummyClass.__name__}"


def apply_decorator(cls, **decorator_kwargs):
    decorated_class = on_init(**decorator_kwargs)(cls)
    return decorated_class


def test_on_init_with_string_logger(caplog):
    decorated_test_class = apply_decorator(DummyClass, logger=DFLT_LOGGER_STR, logargs=True)
    with caplog.at_level(logging.DEBUG, logger=DFLT_LOGGER_STR):
        instance = decorated_test_class('arg1_value', arg2='arg2_value')  # noqa: F841
    msg = caplog.messages[-1]

    assert INIT_CLASS_MSG in msg
    assert 'arg1_value' in msg
    assert 'arg2_value' in msg
    caplog.clear()


def test_on_init_with_logger_instance(caplog, test_logger):
    decorated_test_class = apply_decorator(DummyClass, logger=test_logger, logargs=True)
    with caplog.at_level(logging.DEBUG, logger=test_logger.name):
        instance = decorated_test_class(ARG1)  # noqa: F841
    msg = caplog.messages[-1]

    assert INIT_CLASS_MSG in msg
    assert ARG1 in msg
    caplog.clear()


def test_on_init_without_logargs(caplog, test_logger):
    decorated_test_class = apply_decorator(DummyClass, logger=test_logger.name, logargs=False)
    with caplog.at_level(logging.DEBUG, logger=test_logger.name):
        instance = decorated_test_class(ARG1, arg2=KWARG2)  # noqa: F841
    msg = caplog.messages[-1]

    assert INIT_CLASS_MSG in msg
    assert ARG1 not in msg
    assert KWARG2 not in msg
    caplog.clear()


def test_on_init_with_exception(caplog, test_logger):
    class DummyClass:
        def __init__(self, arg1):
            raise ValueError("Init error")

    decorated_test_class = apply_decorator(DummyClass, logger=test_logger, logargs=True)
    with caplog.at_level(logging.DEBUG, logger=test_logger.name):
        with pytest.raises(ValueError):
            instance = decorated_test_class(ARG1)  # noqa: F841



def test_on_init_with_depth(caplog, test_logger):
    class DummyClass:
        def __init__(self, test_arg=None):
            self.test_arg = test_arg

    # Additional dummy decorator to simulate depth
    def dummy_decorator(func):
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        return wrapper

    @dummy_decorator
    @on_init(logger=test_logger, logargs=True, depth=1)
    class DummyClassDecorated(DummyClass):
        pass

    with caplog.at_level(logging.DEBUG, logger=test_logger.name):
        instance = DummyClassDecorated(ARG1)  # noqa: F841

    msg = caplog.messages[-1]

    assert INIT_CLASS_MSG + 'Decorated' in msg
    assert ARG1 in msg


def test_on_init_with_callable_logger(caplog):
    def logger_callable():
        return logging.getLogger('callable_logger')

    decorated_test_class = apply_decorator(DummyClass, logger=logger_callable, logargs=True)
    with caplog.at_level(logging.DEBUG, logger='callable_logger'):
        instance = decorated_test_class('arg1_value')  # noqa: F841

    msg = caplog.messages[-1]

    assert INIT_CLASS_MSG in msg
    assert 'arg1_value' in msg


def test_on_init_with_class_attribute_logger(caplog, test_logger):
    class DummyClass:
        def __init__(self, arg):
            pass

        logger_attr = test_logger

    decorated_test_class = apply_decorator(DummyClass, logger='logger_attr', logargs=True)
    with caplog.at_level(logging.DEBUG, logger=DummyClass.logger_attr.name):
        instance = decorated_test_class(ARG1)  # noqa: F841

    msg = caplog.messages[-1]

    assert INIT_CLASS_MSG in msg
    assert ARG1 in msg


def test_on_init_with_instance_attribute_logger(caplog, test_logger):
    class DummyClass:
        def __init__(self, arg):
            self.logger_attr = test_logger

    decorated_test_class = apply_decorator(DummyClass, logger='logger_attr', logargs=True)
    with caplog.at_level(logging.DEBUG, logger='logger_attr'):
        instance = decorated_test_class(ARG1)  # noqa: F841

    msg = caplog.messages[-1]
    assert INIT_CLASS_MSG in msg
    assert ARG1 in msg


def test_on_init_log_defaults(caplog, test_logger):
    decorated_test_class = apply_decorator(DummyClass, logger=test_logger, logargs=True, logdefaults=True)
    with caplog.at_level(logging.DEBUG, logger=test_logger.name):
        instance = decorated_test_class(ARG1)  # noqa: F841
    msg = caplog.messages[-1]

    assert INIT_CLASS_MSG in msg
    assert ARG1 in msg
    assert f"arg2={DFLT_KWARG2}" in msg
    caplog.clear()
