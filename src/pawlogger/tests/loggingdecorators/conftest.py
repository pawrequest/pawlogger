import logging
import uuid

import pytest

from pawlogger import DFLT_LOG_LEVEL

ARG1 = "value 1 for test"
ARG2 = "value 2 for test"
DFLT_ARG1 = "default value 1"
DFLT_ARG2 = "default value 2"


@pytest.fixture
def test_logger():
    logger_name = "test_logger_" + str(uuid.uuid4())
    logger = logging.getLogger(logger_name)
    logger.setLevel(DFLT_LOG_LEVEL)
    yield logger
    logger.handlers.clear()
    logger = None


class DummyClass:
    logger_cls_attr = logging.getLogger('logger_cls_attr')
    logger_cls_attr.setLevel(DFLT_LOG_LEVEL)

    def __init__(self, arg1, arg2, arg3=DFLT_ARG1):
        self.arg1 = arg1
        self.arg2 = arg2
        self.arg3 = arg3
        self.logger_inst_attr = logging.getLogger('logger_attr')
        self.logger_inst_attr.setLevel(DFLT_LOG_LEVEL)

    # def __new__(cls, arg1, arg2, arg3=DFLT_ARG1):
    #     return super().__new__(cls)

    def dummy_instance_method(self, arg1, arg2):
        return self, arg1, arg2

    @staticmethod
    def dummy_static_method(arg1, arg2):
        return arg1, arg2

    @classmethod
    def dummy_class_method(cls, arg1, arg2):
        return cls, arg1, arg2


class DummyNewWithArgs(DummyClass):
    def __new__(cls, arg1, arg2, arg3=DFLT_ARG1):
        return super().__new__(cls)


# todo move these
INIT_MSG = f"init: {DummyClass.__name__}"
NEW_MSG = f"new: {DummyClass.__name__}"


def dummy_func(arg1, arg2):
    return arg1, arg2


def dummy_func_noargs():
    return "No args"


def dummy_func_kwargs(arg1, arg2, kwarg3, kwarg4_with_def=None):
    return arg1, arg2, kwarg3, kwarg4_with_def


@pytest.fixture
def dummy_func_fxt():
    return dummy_func


@pytest.fixture
def dummy_func_noargs_fxt():
    return dummy_func_noargs


@pytest.fixture
def dummy_func_kwargs_fxt():
    return dummy_func_kwargs


@pytest.fixture
def dummy_class_fxt():
    return DummyClass


class DummyClassNoArgs:
    def __init__(self):
        self.value = "No args init"

    def __new__(cls):
        return super().__new__(cls)


class DummyClassDefaultArgs:
    def __init__(self, arg1=DFLT_ARG1, arg2=DFLT_ARG2):
        self.arg1 = arg1
        self.arg2 = arg2

    def __new__(cls, arg1=DFLT_ARG1, arg2=DFLT_ARG2):
        return super().__new__(cls)


class DummyInheritedClass(DummyClass):
    def __init__(self, arg1, arg2, extra_arg):
        super().__init__(arg1, arg2)
        self.extra_arg = extra_arg

    def __new__(cls, arg1, arg2, extra_arg):
        return super().__new__(cls)
