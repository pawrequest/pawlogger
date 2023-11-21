import logging

from src.loggingdecorators import on_class
from src.loggingdecorators.decorators import DFLT_LOGGER_STR
from tests.conftest import ARG1, DFLT_ARG1, ARG2, DummyClass, INIT_MSG


def test_dflts(caplog, test_logger):
    with caplog.at_level(logging.DEBUG, logger=DFLT_LOGGER_STR):
        dec_inst = on_class()(DummyClass(ARG1, kwarg2=ARG2))  # noqa: F841
    msg = caplog.messages[-1]
    assert INIT_MSG in msg
    assert ARG1 in msg
    assert ARG2 in msg
    assert DFLT_ARG1 not in msg
    caplog.clear()
    ...


def test_default_arguments():
    decorated_class = apply_decorator(TestClass, logger=logging.getLogger("test"), logargs=True,
                                      decorate_init=True, decorate_new=False)
    instance = decorated_class('arg1')


def test_new_method():
    decorated_class = apply_decorator(TestClass, logger=logging.getLogger("test"), logargs=True,
                                      decorate_init=False, decorate_new=True)
    instance = decorated_class('arg1', arg2='arg2')


def test_function_decoration():
    dummy_function('arg1', arg2='arg2')


def test_both_methods():
    decorated_class = apply_decorator(TestClass, logger=logging.getLogger("test"), logargs=True,
                                      decorate_init=True, decorate_new=True)
    instance = decorated_class('arg1', arg2='arg2')

# import logging
# import pytest
# from loggingdecorators import on_unified  # Replace with your actual module name
# from tests.conftest import ARG1, DFLT_KWARG2, KWARG2
#
# class DummyClass:
#     def __init__(self, arg1, arg2=DFLT_KWARG2):
#         self.arg1 = arg1
#         self.arg2 = arg2
#
#     def __new__(cls, *args, **kwargs):
#         return super(DummyClass, cls).__new__(cls)
#
# def test_on_unified_init_logging(caplog):
#     decorated_class = apply_decorator(DummyClass, logger=logging.getLogger("test"), logargs=True, decorate_init=True, decorate_new=False)
#     with caplog.at_level(logging.DEBUG, logger="test"):
#         instance = decorated_class(ARG1, arg2=KWARG2)
#     assert "init: DummyClass" in caplog.text
#
# def test_on_unified_new_logging(caplog):
#     decorated_class = apply_decorator(DummyClass, logger=logging.getLogger("test"), logargs=True, decorate_init=False, decorate_new=True)
#     with caplog.at_level(logging.DEBUG, logger="test"):
#         instance = decorated_class(ARG1, arg2=KWARG2)
#     assert "new: DummyClass" in caplog.text
#
# def test_on_unified_both_logging(caplog):
#     decorated_class = apply_decorator(DummyClass, logger=logging.getLogger("test"), logargs=True, decorate_init=True, decorate_new=True)
#     with caplog.at_level(logging.DEBUG, logger="test"):
#         instance = decorated_class(ARG1, arg2=KWARG2)
#     assert "init: DummyClass" in caplog.text and "new: DummyClass" in caplog.text
