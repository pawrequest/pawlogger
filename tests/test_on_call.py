import copy
import logging

import pytest

from src.loggingdecorators.consts_formats import call_msg
from src.loggingdecorators.decorators import DFLT_LOGGER_STR, on_call


def dummy_func_noargs():
    return "No args"


def dummy_func_args(arg1, arg2):
    return arg1 + arg2


def dummy_func_kwargs(arg1, arg2, kwarg3, kwarg4_with_def=None):
    return arg1, arg2, kwarg3, kwarg4_with_def


@pytest.mark.parametrize("logger_input", [
    (DFLT_LOGGER_STR, DFLT_LOGGER_STR),
    ("test_logger_obj", logging.getLogger("test_logger_obj")),
    ("test_logger_callable", lambda: logging.getLogger("test_logger_callable")),
    # Callable returning a logger
])
def test_on_call_with_various_loggers(caplog, test_logger, logger_input):
    test_logger_name, logger = logger_input

    dummy = copy.copy(dummy_func_args)
    # decorated_test_function = apply_function_decorator(dummy, logger=logger, logargs=True)
    decorated_test_function = on_call(logger=logger)(dummy)

    with caplog.at_level(logging.DEBUG,
                         logger=test_logger_name if logger != DFLT_LOGGER_STR else DFLT_LOGGER_STR):
        decorated_test_function(10, 20)

    content = call_msg(dummy.__name__, args=(10, 20), kwargs={}, logargs=True)
    assert content in caplog.text
