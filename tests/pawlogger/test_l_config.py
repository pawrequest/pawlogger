import logging
import os
import re
from pathlib import Path

import pytest

import logger_factory
from pawlogger.consts import ASCTIME_PATTERN
from pawlogger import configure_logging

test_params = [
    (logging.DEBUG, "Debug message", "DEBUG", [42]),
    (logging.INFO, "Info message with number: {}", "INFO", [42]),
    (logging.WARNING, "Warning message with float: {:.2f}", "WARNING", [3.14159]),
    (logging.ERROR, "Error message with object: {}", "ERROR", [Exception("Test error")]),
    (logging.CRITICAL, "Critical message with multiline\nNew line included", "CRITICAL", (21,)),
]


@pytest.mark.parametrize("log_level, log_message, level_name, format_args", test_params)
def test_logging(caplog, tmp_path: Path, log_level, log_message, level_name, format_args):
    log_file = tmp_path / "test.log"
    logger = configure_logging(str(log_file.name), level=log_level, log_file=log_file)
    logger.log(log_level, log_message.format(*format_args))

    formatted_message = log_message.format(*format_args)
    assert formatted_message in caplog.messages[-1]
    assert any(level_name in record.levelname for record in caplog.records)

    assert os.path.exists(log_file)
    with open(log_file) as file:
        log_contents = file.read()

    expected_pattern = re.compile(
        f"{level_name} - {ASCTIME_PATTERN} - test_l_config:\\d{{2}} - {re.escape(formatted_message)}\n")
    assert expected_pattern.search(log_contents)


@pytest.fixture
def logger_from_factory(tmp_path: Path):
    log_file = tmp_path / "factory_logger.log"
    return logger_factory.get_logger(log_file=str(log_file))


def test_logging_from_different_sources(caplog, tmp_path: Path, logger_from_factory):
    # Logger from the test module
    log_file_test = tmp_path / "test_logger.log"
    logger_test = configure_logging(log_file=str(log_file_test))

    # Log a message from the test module logger
    test_message = "Log message from test module"
    logger_test.info(test_message)

    # Log a message from the factory logger
    factory_message = "Log message from factory"
    logger_from_factory.info(factory_message)

    # Assertions
    assert test_message in caplog.text
    assert factory_message in caplog.text
    assert os.path.exists(log_file_test) and os.path.exists(tmp_path / "factory_logger.log")

    # You can add more assertions to check the content of the log files
