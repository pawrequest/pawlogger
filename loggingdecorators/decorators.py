import inspect
import logging
from functools import wraps
from typing import Callable, Type, TypeVar, Union

LOGGER_CLASS = logging.getLoggerClass()
DFLT_LOGGER_STR = "logger"
LOGGER_LIKE = Union[str, LOGGER_CLASS, Callable]
T = TypeVar('T', bound=Type)


def on_call(logger: Union[LOGGER_CLASS, Callable], level=logging.DEBUG, logargs=True, msg: str = "", depth=0):
    """
    When applied to a function, decorate it with a wrapper which logs the call using the given logger at the specified
    level.

    The "logger" argument must be an instance of a logger from the logging library, or a function which returns an
    instance of a logger.

    If logargs is True, log the function arguments, one per line.

    If the decorated function is to be nested inside other decorators, increase the depth argument by 1 for each
    additional level of nesting in order for the messages emitted to contain the correct source file name & line number.
    """
    const_depth = 2
    total_depth = const_depth + depth

    def decorator(func):

        if not callable(func):
            raise TypeError(f"{func} does not appear to be callable.")

        if getattr(func, "__name__") == "__repr__":
            raise RuntimeError("Cannot apply to __repr__ as this will cause infinite recursion!")

        @wraps(func)
        def wrapper(*args, **kwargs):

            _logger = logger() if inspect.isfunction(logger) else logger

            if not isinstance(_logger, LOGGER_CLASS):
                raise TypeError(f"logger argument had unexpected type {type(_logger)}, expected {LOGGER_CLASS}")

            content = f"calling {func.__name__} with {len(args)} arg(s) and {len(kwargs)} kwarg(s) "
            if msg:
                content = f"{content} ({msg})"
            _logger.log(level, content, stacklevel=total_depth)
            if logargs:
                log_args(_logger, args, kwargs)
            return func(*args, **kwargs)

        def log_args(_logger, args, kwargs):
            for n, arg in enumerate(args):
                _logger.log(level, f" - arg {n:>2}: {type(arg)} {arg}", stacklevel=total_depth)
            for m, (key, item) in enumerate(kwargs.items()):
                _logger.log(level, f" - kwarg {m:>2}: {type(item)} {key}={item}", stacklevel=total_depth)

        return wrapper

    return decorator


def on_init(logger: LOGGER_LIKE = "logger", level=logging.DEBUG, logargs=True, logdefaults=False, depth=0):
    """
    Decorator for logging initialization calls to a class's __init__ method.
    """
    const_depth = 2
    total_depth = const_depth + depth

    def decorator(constructor):
        if inspect.isclass(constructor):
            original_init = constructor.__init__
        else:
            original_init = constructor

        @wraps(original_init)
        def init_wrapper(self, *args, **kwargs):
            _logger = _get_logger(self, logger)

            if logargs:
                init_signature = inspect.signature(original_init)
                bound_arguments = init_signature.bind(self, *args, **kwargs)
                if logdefaults:
                    bound_arguments.apply_defaults()

                formatted_args = ', '.join(f"{k}={v}" for k, v in bound_arguments.arguments.items())
                _logger.log(level, f"init: {self.__class__.__name__}({formatted_args})", stacklevel=total_depth)
            else:
                _logger.log(level, f"init: {self.__class__.__name__}()", stacklevel=total_depth)

            return original_init(self, *args, **kwargs)

        if inspect.isclass(constructor):
            constructor.__init__ = init_wrapper
        else:
            constructor = init_wrapper

        return constructor

    return decorator


# # def on_init(logger: LOGGER_LIKE = "logger", level=logging.DEBUG, logargs=True, depth=0):
# def on_init(logger: LOGGER_LIKE = "logger", level=logging.DEBUG, logargs=True, logdefaults=False, depth=0):
#     """
#     When applied to a class or an __init__ method, decorate it with a wrapper which logs the __init__ call using the
#     given logger at the specified level.
#
#     If "logger" is a string, look up an attribute of this name in the initialised object and use it to log the message.
#     if there is no such attribute, get a logger with this name from the logging library and use it to log the message.
#     If "logger" is a function, call it to obtain a reference to a logger instance.
#     Otherwise, assume "logger" is an instance of a logger from the logging library and use it to log the message.
#
#     If logargs is True, the message contains the arguments passed to __init__.
#
#     If the decorated class or __init__ method is to be nested inside other decorators, increase the depth argument by 1
#     for each additional level of nesting in order for the messages emitted to contain the correct source file name &
#     line number.
#     """
#
#     const_depth = 2
#     total_depth = const_depth + depth
#
#     def decorator(constructor):
#
#         if not callable(constructor):
#             raise TypeError(f"{constructor} does not appear to be callable.")
#
#         is_class = inspect.isclass(constructor)
#
#         to_call = getattr(constructor, "__init__") if is_class else constructor
#
#
#         @wraps(constructor)
#         def init_wrapper(self, *args, **kwargs):
#             _logger = _get_logger(self, logger)
#
#             if logargs:
#                 init_signature = inspect.signature(to_call)
#                 bound_arguments = init_signature.bind(self, *args, **kwargs)
#                 if logdefaults:
#                     bound_arguments.apply_defaults()
#
#                 formatted_args = ', '.join(f"{k}={v}" for k, v in bound_arguments.arguments.items())
#                 _logger.log(level, f"init: {self.__class__.__name__}({formatted_args})", stacklevel=total_depth)
#             else:
#                 _logger.log(level, f"init: {self.__class__.__name__}()", stacklevel=total_depth)
#
#             to_call(self, *args, **kwargs)
#         #
#         #
#         # @wraps(constructor)
#         # def init_wrapper(self, *args, **kwargs):
#         #     _logger = _get_logger(self, logger)
#         #
#         #     if logargs:
#         #         _logger.log(level, f"init: {self.__class__.__name__}({args=}, {kwargs=})", stacklevel=total_depth)
#         #     else:
#         #         _logger.log(level, f"init: {self.__class__.__name__}()", stacklevel=total_depth)
#         #
#         #     to_call(self, *args, **kwargs)
#
#         if is_class:
#             setattr(constructor, "__init__", init_wrapper)
#             return constructor
#         else:
#             return init_wrapper
#
#     return decorator


def on_new(logger: LOGGER_LIKE = DFLT_LOGGER_STR, level=logging.DEBUG, logargs=True, logdefaults=False,
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


def _get_logger(cls_or_self, logger: LOGGER_LIKE):
    if isinstance(logger, LOGGER_CLASS):
        return logger
    elif callable(logger):
        return logger()
    elif isinstance(logger, str):
        return getattr(cls_or_self, logger, logging.getLogger(logger))
    else:
        raise TypeError(f"logger argument had unexpected type {type(logger)}, expected {LOGGER_CLASS}")
