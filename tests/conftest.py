import logging
import uuid

import pytest

from src.loggingdecorators.decorators import DFLT_LOG_LEVEL

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
    def __init__(self, arg1, kwarg2, kwarg3dflt=DFLT_ARG1):
        self.arg1 = arg1
        self.arg2 = kwarg2
        self.arg3 = kwarg3dflt


INIT_MSG = f"init: {DummyClass.__name__}"
NEW_MSG = f"new: {DummyClass.__name__}"


def dummy_function(arg1, arg2=DFLT_ARG1):
    return arg1, arg2
