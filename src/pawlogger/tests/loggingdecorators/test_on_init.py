import logging

import pytest

from pawlogger import on_init
from pawlogger import DFLT_LOGGER_STR, DFLT_LOG_LEVEL
from tests.loggingdecorators.conftest import ARG1, ARG2, DFLT_ARG1, DummyClass


def test_on_init_dflt(caplog):
    decorated_class = on_init()(DummyClass)
    with caplog.at_level(logging.DEBUG, logger=DFLT_LOGGER_STR):
        instance = decorated_class(ARG1, ARG2)  # noqa: F841
    msg = caplog.messages[-1]
    assert INIT_MSG in msg
    assert ARG1 in msg
    assert ARG2 in msg
    assert DFLT_ARG1 not in msg
    caplog.clear()


@pytest.mark.parametrize("logger_input", [
    ("default_logger", DFLT_LOGGER_STR),
    ("test_logger_instance", "test_logger"),
])
def test_on_init_with_various_loggers(caplog, test_logger, logger_input):
    logger_type, logger = logger_input
    logger = test_logger if logger == "test_logger" else logger
    decorated_class = on_init(logger=logger)(DummyClass)
    with caplog.at_level(logging.DEBUG,
                         logger=test_logger.name if logger_type == "test_logger_instance" else DFLT_LOGGER_STR):
        instance = decorated_class(ARG1, arg2=ARG2)  # noqa: F841
    msg = caplog.messages[-1]
    assert INIT_MSG in msg
    assert ARG1 in msg
    assert ARG2 in msg
    assert DFLT_ARG1 not in msg
    caplog.clear()



def test_on_init_with_exception(caplog, test_logger):
    class DummyClassExcepts:
        def __init__(self, arg1):
            raise ValueError("Init error")

    decorated_class = on_init(logger=test_logger)(DummyClassExcepts)

    with caplog.at_level(logging.DEBUG, logger=test_logger.name):
        with pytest.raises(ValueError):
            instance = decorated_class(ARG1)  # noqa: F841


def test_on_init_with_depth(caplog, test_logger):
    def dummy_decorator(func):
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        return wrapper

    @dummy_decorator
    @on_init(logger=test_logger, depth=1)
    class DummyClassDecorated(DummyClass):
        pass

    with caplog.at_level(DFLT_LOG_LEVEL, logger=test_logger.name):
        instance = DummyClassDecorated(ARG1, ARG2)  # noqa: F841
    msg = caplog.messages[-1]

    assert INIT_MSG + 'Decorated' in msg
    assert ARG1 in msg


def test_on_init_with_callable_logger(caplog):
    def logger_callable():
        return logging.getLogger('callable_logger')

    decorated_test_class = on_init(logger=logger_callable)(DummyClass)
    with caplog.at_level(logging.DEBUG, logger='callable_logger'):
        instance = decorated_test_class(ARG1, ARG2)  # noqa: F841

    msg = caplog.messages[-1]

    assert INIT_MSG in msg
    assert ARG1 in msg


def test_on_init_with_class_attribute_logger(caplog, test_logger):
    logger = DummyClass.logger_cls_attr
    decorated_test_class = on_init(logger=logger.name)(DummyClass)

    with caplog.at_level(DFLT_LOG_LEVEL, logger=logger.name):
        instance = decorated_test_class(ARG1, ARG2)  # noqa: F841

    msg = caplog.messages[-1]

    assert INIT_MSG in msg
    assert ARG1 in msg


def test_on_init_with_instance_attribute_logger(caplog, test_logger):
    decorated_test_class = on_init(logger='logger_attr')(DummyClass)
    with caplog.at_level(logging.DEBUG, logger='logger_attr'):
        instance = decorated_test_class(ARG1, ARG2)  # noqa: F841

    msg = caplog.messages[-1]
    assert INIT_MSG in msg
    assert ARG1 in msg
    assert ARG2 in msg


def test_on_init_log_defaults(caplog, test_logger):
    decorated_test_class = on_init(logger=test_logger, logdefaults=True)(DummyClass)
    with caplog.at_level(logging.DEBUG, logger=test_logger.name):
        instance = decorated_test_class(ARG1, ARG2)  # noqa: F841
    msg = caplog.messages[-1]

    assert INIT_MSG in msg
    assert ARG1 in msg
    assert f"arg3={DFLT_ARG1}" in msg
    caplog.clear()
