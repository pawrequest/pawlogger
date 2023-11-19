import inspect
import logging
from functools import wraps
from typing import Callable, Union

loggerClass = logging.getLoggerClass()


def on_new(logger: Union[str, loggerClass, Callable] = "logger", level=logging.DEBUG, logargs=True, depth=0):
    """
    Decorator for logging calls to a class's __new__ method.
    """
    const_depth = 2
    total_depth = const_depth + depth

    def decorator[T](cls: type) -> T:
        original_new = cls.__new__

        @wraps(original_new)
        def new_wrapper(cls, *args, **kwargs):
            # Determine the appropriate logger
            if isinstance(logger, str):
                # If logger is a string, use it as an attribute name to find the logger on the class
                _logger = getattr(cls, logger, None)
                if _logger is None:
                    raise AttributeError(f"Logger named '{logger}' not found in class '{cls.__name__}'.")
            elif inspect.isfunction(logger) or inspect.ismethod(logger):
                # If logger is a callable, call it to get the logger instance
                _logger = logger()
            else:
                # Otherwise, assume logger is a logger instance
                _logger = logger

            # Ensure _logger is an instance of a logger
            if not isinstance(_logger, loggerClass):
                raise TypeError(f"logger argument had unexpected type {type(_logger)}, expected {loggerClass}")

            # Log the new call
            if logargs:
                _logger.log(level, f"new: {cls.__name__}({args=}, {kwargs=})", stacklevel=total_depth)
            else:
                _logger.log(level, f"new: {cls.__name__}()", stacklevel=total_depth)

            # Call the original __new__ method
            return original_new(cls, *args, **kwargs)

        setattr(cls, "__new__", new_wrapper)
        return cls

    return decorator

# import inspect
# import logging
# from functools import wraps
# from typing import Union, Callable
#
# loggerClass = logging.Logger
#
# def on_new(logger: Union[str, loggerClass, Callable]="logger", level=logging.DEBUG, logargs=True, depth=0):
#     """
#     When applied to a class, decorate its __new__ method with a wrapper which logs the __new__ call using the
#     given logger at the specified level.
#
#     The logger argument can be a string (an attribute name of the class), a logger instance, or a function
#     that returns a logger instance.
#
#     If logargs is True, the message contains the arguments passed to __new__.
#
#     The depth argument adjusts the stack level for correct file name and line number reporting in nested decorators.
#     """
#
#     const_depth = 2
#     total_depth = const_depth + depth
#
#     def decorator(cls):
#         if not inspect.isclass(cls):
#             raise TypeError(f"{cls} is not a class.")
#
#         original_new = cls.__new__
#
#         @wraps(original_new)
#         def new_wrapper(cls, *args, **kwargs):
#             _logger = getattr(cls, logger) if isinstance(logger, str) \
#                 else logger() if inspect.isfunction(logger) \
#                 else logger
#
#             if not isinstance(_logger, loggerClass):
#                 raise TypeError(f"logger argument had unexpected type {type(_logger)}, expected {loggerClass}")
#
#             if logargs:
#                 _logger.log(level, f"new: {cls.__name__}({args=}, {kwargs=})", stacklevel=total_depth)
#             else:
#                 _logger.log(level, f"new: {cls.__name__}()", stacklevel=total_depth)
#
#             return original_new(cls, *args, **kwargs)
#
#         setattr(cls, "__new__", new_wrapper)
#         return cls
#
#     return decorator
