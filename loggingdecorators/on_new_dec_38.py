from __future__ import annotations

import inspect
import logging
from functools import wraps
from typing import Callable, Type, TypeVar, Union

DFLT_LOGGER_STR = "logger"
loggerClass = logging.getLoggerClass()
loggerType = Union[str, loggerClass, Callable]
T = TypeVar('T', bound=Type)


def on_new(logger: loggerType = DFLT_LOGGER_STR, level=logging.DEBUG, logargs=True, logdefaults=False,
           depth=0):
    """
    Decorator for logging calls to a class's __new__ method.
    """
    const_depth = 2
    total_depth = const_depth + depth

    def decorator(cls: T) -> T:
        original_new = cls.__new__

        @wraps(original_new)
        def new_wrapper(cls, *args, **kwargs):
            _logger = _get_logger(cls, logger)

            if logargs:
                new_signature = inspect.signature(original_new)
                bound_arguments = new_signature.bind(cls, *args, **kwargs)
                if logdefaults:
                    bound_arguments.apply_defaults()

                formatted_args = ', '.join(f"{k}={v}" for k, v in bound_arguments.arguments.items())
                _logger.log(level, f"new: {cls.__name__}({formatted_args})", stacklevel=total_depth)
            else:
                _logger.log(level, f"new: {cls.__name__}()", stacklevel=total_depth)

            # Call the original __new__ method
            return original_new(cls, *args, **kwargs)

        setattr(cls, "__new__", new_wrapper)
        return cls

    return decorator


def _get_logger(cls, logger: loggerType):
    # if string check first in class attributes else fetch from logging
    _logger = getattr(cls, logger, logging.getLogger(logger)) if isinstance(logger, str) \
        else logger() if any([inspect.isfunction(logger), inspect.ismethod(logger)]) \
        else logger

    if not isinstance(_logger, loggerClass):
        raise TypeError(f"logger argument had unexpected type {type(_logger)}, expected {loggerClass}")
    return _logger
