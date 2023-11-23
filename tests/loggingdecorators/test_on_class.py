import logging

import pytest

from pawlogger import DFLT_LOGGER_STR, build_log_msg
from pawlogger.loggingdecorators.decorators import on_class
from tests.loggingdecorators.conftest import (ARG1, ARG2, DFLT_LOG_LEVEL, DummyClass, DummyClassDefaultArgs,
                                              DummyClassNoArgs,
                                              DummyInheritedClass, DummyNewWithArgs)


@pytest.mark.parametrize("logger_input", [
    (DFLT_LOGGER_STR, DFLT_LOGGER_STR),
    ("test_logger_obj", logging.getLogger("test_logger_obj")),
    ("test_logger_callable", lambda: logging.getLogger("test_logger_callable")),
])
def test_on_class_init(caplog, logger_input):
    logger_name, logger = logger_input
    DecoratedClass = on_class(logger=logger, decorate_init=True, decorate_new=False)(DummyClass)

    with caplog.at_level(DFLT_LOG_LEVEL, logger=logger_name):
        instance = DecoratedClass(ARG1, ARG2)  # noqa 481

    expected_log = f'calling __init__ with 2 arg(s): arg1 = {ARG1}, arg2 = {ARG2}'
    assert expected_log in caplog.text


@pytest.mark.parametrize("logger_input", [
    (DFLT_LOGGER_STR, DFLT_LOGGER_STR),
    ("test_logger_obj", logging.getLogger("test_logger_obj")),
    ("test_logger_callable", lambda: logging.getLogger("test_logger_callable")),
])
def test_on_class_new(caplog, logger_input):
    logger_name, logger = logger_input
    DecoratedClass = on_class(logger=logger, decorate_init=False, decorate_new=True)(
        DummyNewWithArgs)

    with caplog.at_level(DFLT_LOG_LEVEL, logger=logger_name):
        instance = DecoratedClass(ARG1, ARG2)

    expected_log = f'calling __new__ with 2 arg(s): arg1 = {ARG1}, arg2 = {ARG2}'
    assert expected_log in caplog.text
#
#
# @pytest.mark.parametrize("decorate_init, decorate_new", [
#     (True, False),
#     # (False, True),
#     # (True, True)
# ])
# @pytest.mark.parametrize("class_type, init_args", [
#     (DummyClassNoArgs, ()),
#     # (DummyClassDefaultArgs, ()),
#     # (DummyInheritedClass, (ARG1, ARG2, "Extra Arg")),
# ])
# @pytest.mark.parametrize("logger_input", [
#     (DFLT_LOGGER_STR, DFLT_LOGGER_STR),
#     # ("test_logger_obj", logging.getLogger("test_logger_obj")),
#     # ("test_logger_callable", lambda: logging.getLogger("test_logger_callable")),
# ])
# def test_on_class_various_types(caplog, logger_input, class_type, init_args, decorate_init, decorate_new):
#     logger_name, logger = logger_input
#     DecoratedClass = on_class(logger=logger, decorate_init=decorate_init, decorate_new=decorate_new)(class_type)
#
#     with caplog.at_level(DFLT_LOG_LEVEL, logger=logger_name):
#         instance = DecoratedClass(*init_args)
#
#     # args_dict = dict(zip(func.__code__.co_varnames, args))
#     # args_dict.update(kwargs)
#     # expected_log = build_log_msg(func, args=args_dict)
#
#     method_name = "__init__" if decorate_init else "__new__"
#     arg_details = ', '.join([f'arg{i+1} = {arg}' for i, arg in enumerate(init_args)])
#     expected_log = f'calling {method_name} with {len(init_args)} arg(s): {arg_details}'
#     assert expected_log in caplog.text


@pytest.mark.parametrize("decorate_init, decorate_new", [
    (True, False),
    (False, True),
    (True, True)
])
@pytest.mark.parametrize("class_type, init_args", [
    (DummyClassNoArgs, ()),
    (DummyClassDefaultArgs, ()),
    (DummyInheritedClass, (ARG1, ARG2, "Extra Arg")),
])
@pytest.mark.parametrize("logger_input", [
    (DFLT_LOGGER_STR, DFLT_LOGGER_STR),
    ("test_logger_obj", logging.getLogger("test_logger_obj")),
    ("test_logger_callable", lambda: logging.getLogger("test_logger_callable")),
])

def test_on_class_various_types(caplog, logger_input, class_type, init_args, decorate_init, decorate_new):
    logger_name, logger = logger_input
    DecoratedClass = on_class(logger=logger, decorate_init=decorate_init, decorate_new=decorate_new)(class_type)

    with caplog.at_level(DFLT_LOG_LEVEL, logger=logger_name):
        instance = DecoratedClass(*init_args)

    # Determine the actual method and its class
    method = DecoratedClass.__init__ if decorate_init else DecoratedClass.__new__
    method_class = type(method)

    # Construct args_dict based on method and class
    arg_names = method.__code__.co_varnames[1:method.__code__.co_argcount]
    args_dict = dict(zip(arg_names, init_args))
    if decorate_init:
        args_dict = {'self': instance, **args_dict}
    else:
        args_dict = {'cls': DecoratedClass, **args_dict}

    expected_log = build_log_msg(method, args=args_dict)

    assert expected_log in caplog.text

# def test_on_class_various_types(caplog, logger_input, class_type, init_args, decorate_init, decorate_new):
#     logger_name, logger = logger_input
#     DecoratedClass = on_class(logger=logger, decorate_init=decorate_init, decorate_new=decorate_new)(class_type)
#
#     with caplog.at_level(DFLT_LOG_LEVEL, logger=logger_name):
#         instance = DecoratedClass(*init_args)
#
#     # Choose the method (__init__ or __new__) from the decorated class
#     method = DecoratedClass.__init__ if decorate_init else DecoratedClass.__new__
#     method_name = "__init__" if decorate_init else "__new__"
#
#     # Extract argument names (excluding 'self' and 'cls')
#     arg_names = method.__code__.co_varnames[1:method.__code__.co_argcount]
#
#     # Construct the args_dict with correct argument names and values
#     args_dict = dict(zip(arg_names, init_args))
#     if decorate_init:
#         args_dict = {'self': instance, **args_dict}
#     else:  # If decorate_new is True
#         args_dict = {'cls': DecoratedClass, **args_dict}
#
#     expected_log = build_log_msg(method, args=args_dict)
#
#     assert expected_log in caplog.text
