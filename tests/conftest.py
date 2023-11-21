import logging
import uuid

import pytest

ARG1 = "value 1 for test"
ARG2 = "value 2 for test"
DFLT_ARG1 = "default value 1"
DFLT_ARG2 = "default value 2"


@pytest.fixture
def test_logger():
    logger_name = "test_logger_" + str(uuid.uuid4())
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.DEBUG)
    yield logger
    logger.handlers.clear()
    logger = None


class DummyClass:
    def __init__(self, arg1, arg2=DFLT_ARG1):
        self.arg1 = arg1
        self.arg2 = arg2


INIT_CLASS_MSG = f"init: {DummyClass.__name__}"
