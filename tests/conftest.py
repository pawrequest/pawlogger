import logging
import uuid

import pytest

ARG1 = "value 1 for test"
KWARG2 = "keyword value 2 for test"
DFLT_KWARG2 = "default value kwarg 2"
DFLT_KWARG3 = "default value kwarg 3"


@pytest.fixture
def test_logger():
    logger_name = "test_logger_" + str(uuid.uuid4())
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.DEBUG)
    yield logger
    logger.handlers.clear()
    logger = None
