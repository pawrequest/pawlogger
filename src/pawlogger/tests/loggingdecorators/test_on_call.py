import copy
import logging

import pytest

from pawlogger import DFLT_LOGGER_STR, DFLT_LOG_LEVEL, build_log_msg
from pawlogger.loggingdecorators.decorators import on_call
from tests.loggingdecorators.conftest import ARG1, ARG2, dummy_func, dummy_func_kwargs, dummy_func_noargs


@pytest.mark.parametrize("logger_input", [
    (DFLT_LOGGER_STR, DFLT_LOGGER_STR),
    ("test_logger_obj", logging.getLogger("test_logger_obj")),
    ("test_logger_callable", lambda: logging.getLogger("test_logger_callable")),
])
def test_on_call_with_various_loggers(caplog, logger_input):
    logger_name, logger = logger_input
    dummy = copy.copy(dummy_func)
    decorated_test_function = on_call(logger=logger)(dummy)
    argdict = {
        'arg1': ARG1,
        'arg2': ARG2,
    }
    with caplog.at_level(DFLT_LOG_LEVEL, logger=logger_name):
        decorated_test_function(**argdict)

    content = build_log_msg(dummy, args=argdict)
    assert content in caplog.text



# Test functions with different argument types
@pytest.mark.parametrize("func, args, kwargs", [
    (dummy_func, ('arg1', 'arg2'), {}),
    (dummy_func_noargs, (), {}),
    (dummy_func_kwargs, ('arg1', 'arg2'), {'kwarg3': 'value3', 'kwarg4_with_def': 'value4'}),
])
@pytest.mark.parametrize("logger_input", [
    (DFLT_LOGGER_STR, DFLT_LOGGER_STR),
    ("test_logger_obj", logging.getLogger("test_logger_obj")),
    ("test_logger_callable", lambda: logging.getLogger("test_logger_callable")),
])
def test_on_call_functions(caplog, logger_input, func, args, kwargs):
    logger_name, logger = logger_input
    decorated_function = on_call(logger=logger)(func)

    with caplog.at_level(DFLT_LOG_LEVEL, logger=logger_name):
        result = decorated_function(*args, **kwargs)

    # Build log message
    args_dict = dict(zip(func.__code__.co_varnames, args))
    args_dict.update(kwargs)
    expected_log = build_log_msg(func, args=args_dict)
    assert expected_log in caplog.text


@pytest.mark.parametrize("method_name, args, kwargs", [
    ('dummy_instance_method', ('arg1', 'arg2'), {}),
    ('dummy_static_method', ('arg1', 'arg2'), {}),
    ('dummy_class_method', ('arg1', 'arg2'), {}),
])
@pytest.mark.parametrize("logger_input", [
    (DFLT_LOGGER_STR, DFLT_LOGGER_STR),
    ("test_logger_obj", logging.getLogger("test_logger_obj")),
    ("test_logger_callable", lambda: logging.getLogger("test_logger_callable")),
])
def test_on_call_class_methods(caplog, logger_input, method_name, args, kwargs, dummy_class_fxt):
    logger_name, logger = logger_input
    dummy_class = dummy_class_fxt
    method = getattr(dummy_class, method_name)
    decorated_method = on_call(logger=logger)(method)

    with caplog.at_level(DFLT_LOG_LEVEL, logger=logger_name):
        if 'instance' in method_name:
            # Create an instance of DummyClass for instance method test
            instance = dummy_class(ARG1, ARG2)
            result = decorated_method(instance, *args, **kwargs)
        else:
            result = decorated_method(*args, **kwargs)

    # Build log message
    full_args = (dummy_class,) + args if 'class' in method_name else args
    full_args = (instance,) + args if 'instance' in method_name else full_args
    args_dict = dict(zip(method.__code__.co_varnames[:len(full_args)], full_args))
    args_dict.update(kwargs)
    expected_log = build_log_msg(method, args=args_dict)

    assert expected_log in caplog.text

