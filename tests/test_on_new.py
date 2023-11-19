import io
import logging

from loggingdecorators import on_new


class StringStreamHandler(logging.Handler):
    def __init__(self):
        super().__init__()
        self.stream = io.StringIO()

    def emit(self, record):
        self.stream.write(self.format(record))


# Set up a logger for testing
logger = logging.getLogger("test")
logger.setLevel(logging.DEBUG)
string_handler = StringStreamHandler()
logger.addHandler(string_handler)


# Your TestClass and on_new decorator as before
@on_new(logger=logger, logargs=True, log_defaults=True, level=logging.DEBUG)
class TestClass:
    def __new__(cls, arg1, arg2="default"):
        return super().__new__(cls)


def test_on_new_decorator():
    instance = TestClass("value1", arg2="value2")
    logged_output = string_handler.stream.getvalue()
    assert "new: TestClass" in logged_output
    assert "value1" in logged_output
    assert "value2" in logged_output

    # Clear the StringIO stream before the next instantiation
    string_handler.stream.seek(0)
    string_handler.stream.truncate()

    # Test with default arguments
    instance_default = TestClass("value1")
    new_logged_output = string_handler.stream.getvalue()
    assert "default" in new_logged_output
