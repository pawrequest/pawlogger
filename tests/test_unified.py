import logging

from loggingdecorators import on_unified
from tests.conftest import ARG1, DFLT_ARG1, ARG2


def apply_decorator(cls, **decorator_kwargs):
    decorated_class = on_unified(**decorator_kwargs)(cls)
    return decorated_class


class TestClass:
    def __init__(self, arg1, arg2='default_arg2'):
        self.arg1 = arg1
        self.arg2 = arg2

    def __new__(cls, *args, **kwargs):
        instance = super(TestClass, cls).__new__(cls)
        # Additional __new__ logic here, if any
        return instance


@on_unified(logger=logging.getLogger("test"), logargs=True, decorate_init=True, decorate_new=False)
def dummy_function(arg1, arg2='default_arg2'):
    return arg1, arg2


def test_basic_initialization():
    decorated_class = apply_decorator(TestClass, logger=logging.getLogger("test"), logargs=True,
                                      decorate_init=True, decorate_new=False)
    instance = decorated_class('arg1', arg2='arg2')
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
