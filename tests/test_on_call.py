import copy
import functools
import logging

import pytest

from loggingdecorators.decorators import on_call
from tests.conftest import KWARG2


ARG0_INT_10 = " - arg  0: <class 'int'> 10"
ARG1_INT_20 = " - arg  1: <class 'int'> 20"

def dummy_func_noargs():
    return "No args"


def dummy_func_args(arg1, arg2):
    return arg1 + arg2


def dummy_func_kwargs(arg1, arg2, kwarg3, kwarg4_with_def=None):
    return arg1, arg2, kwarg3, kwarg4_with_def


def apply_function_decorator(func, **decorator_kwargs):
    decorated_function = on_call(**decorator_kwargs)(func)
    return decorated_function


def test_on_call_with_logger_object(caplog, test_logger):
    dummy = copy.copy(dummy_func_args)
    decorated_test_function = apply_function_decorator(dummy, logger=test_logger, logargs=True)
    with caplog.at_level(logging.DEBUG, logger=test_logger.name):
        decorated_test_function(10, 20)

    assert caplog.messages[0] == f"calling {dummy.__name__} with 2 arg(s) and 0 kwarg(s) "
    assert caplog.messages[1] == ARG0_INT_10
    assert caplog.messages[2] == ARG1_INT_20


def test_on_call_with_callable_logger(caplog, test_logger):
    def logger_callable():
        return test_logger
    dummy = copy.copy(dummy_func_args)
    decorated_dummy_function = apply_function_decorator(dummy, logger=logger_callable, logargs=True)

    with caplog.at_level(logging.DEBUG, logger=test_logger.name):
        decorated_dummy_function(10, 20)  # noqa: F841

    assert caplog.messages[0] == f"calling {dummy.__name__} with 2 arg(s) and 0 kwarg(s) "
    assert caplog.messages[1] == ARG0_INT_10
    assert caplog.messages[2] == ARG1_INT_20


def test_on_call_without_arguments(caplog, test_logger):
    caplog.clear()
    dummy = copy.copy(dummy_func_noargs)
    decorated_dummy_function = apply_function_decorator(dummy, logger=test_logger, logargs=False)

    with caplog.at_level(logging.DEBUG, logger=test_logger.name):
        decorated_dummy_function()

    msg = caplog.records[0].msg
    assert f"calling {decorated_dummy_function.__name__} with 0 arg(s)" in msg


def test_on_call_invalid_logger(caplog):
    dummy = copy.copy(dummy_func_args)
    decorated_dummy_function = apply_function_decorator(dummy, logger=123)
    with pytest.raises(TypeError):
        decorated_dummy_function(10, 20)
        with caplog.at_level(logging.DEBUG, logger='dummy_logger'):
            decorated_dummy_function(10, 20)


def dummy_decorator(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)

    return wrapper


def test_on_call_with_nested_decorators(caplog, test_logger):
    dummy = copy.copy(dummy_func_args)
    decorated_dummy_function = dummy_decorator(
        apply_function_decorator(dummy, logger=test_logger, logargs=True))
    with caplog.at_level(logging.DEBUG, logger=test_logger.name):
        result = decorated_dummy_function(10, 20) # noqa: F841
    assert caplog.messages[0] == f"calling {decorated_dummy_function.__name__} with 2 arg(s) and 0 kwarg(s) "
    assert caplog.messages[1] == ARG0_INT_10
    assert caplog.messages[2] == ARG1_INT_20


def test_on_call_with_complex_arguments(caplog, test_logger):
    dummy = copy.copy(dummy_func_kwargs)
    decorated_dummy_function = apply_function_decorator(dummy, logger=test_logger, logargs=True)

    complex_arg = {'key1': 1, 'key2': [1, 2, 3]}

    with caplog.at_level(logging.DEBUG, logger=test_logger.name):
        decorated_dummy_function(complex_arg, 20, kwarg3=KWARG2)

    assert caplog.messages[0] == f"calling {dummy.__name__} with 2 arg(s) and 1 kwarg(s) "
    assert caplog.messages[1] == f" - arg  0: <class 'dict'> {complex_arg}"
    assert caplog.messages[2] == ARG1_INT_20
    assert caplog.messages[3] == f" - kwarg  0: <class 'str'> kwarg3={KWARG2}"


def test_on_call_log_level(caplog, test_logger):
    dummy = copy.copy(dummy_func_args)
    decorated_dummy_function = apply_function_decorator(dummy, logger=test_logger, logargs=True, level=logging.INFO)

    with caplog.at_level(logging.INFO, logger=test_logger.name):
        decorated_dummy_function(10, 20)

    assert caplog.records[0].levelname == 'INFO'


