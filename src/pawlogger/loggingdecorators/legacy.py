import inspect
import logging
from functools import wraps
from typing import Callable, Union

from .consts_formats import DFLT_LOGGER_STR, LOGGER_CLASS, LOGGER_LIKE
from .decorators import _get_logger, log_agnostic

loggerClass = logging.getLoggerClass()


def on_call_og(logger: Union[loggerClass, Callable], level=logging.DEBUG, logargs=True,
               msg: str = "", depth=0):
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

            if not isinstance(_logger, loggerClass):
                raise TypeError(
                    f"logger argument had unexpected type {type(_logger)}, expected {loggerClass}")

            content = f"calling {func} with {len(args)} arg(s) and {len(kwargs)} kwarg(s) "
            if msg:
                content = f"{content} ({msg})"
            _logger.log(level, content, stacklevel=total_depth)
            if logargs:
                for n, arg in enumerate(args):
                    _logger.log(level, f" - arg {n:>2}: {type(arg)} {arg}", stacklevel=total_depth)
                for m, (key, item) in enumerate(kwargs.items()):
                    _logger.log(level, f" - kwarg {m:>2}: {type(item)} {key}={item}",
                                stacklevel=total_depth)
            return func(*args, **kwargs)

        return wrapper

    return decorator


def on_init_og(logger: Union[str, loggerClass, Callable] = "logger", level=logging.DEBUG,
               logargs=True, depth=0):
    """
    When applied to a class or an __init__ method, decorate it with a wrapper which logs the __init__ call using the
    given logger at the specified level.

    If "logger" is a string, look up an attribute of this name in the initialised object and use it to log the message.
    If "logger" is a function, call it to obtain a reference to a logger instance.
    Otherwise, assume "logger" is an instance of a logger from the logging library and use it to log the message.

    If logargs is True, the message contains the arguments passed to __init__.

    If the decorated class or __init__ method is to be nested inside other decorators, increase the depth argument by 1
    for each additional level of nesting in order for the messages emitted to contain the correct source file name &
    line number.
    """

    const_depth = 2
    total_depth = const_depth + depth

    def decorator(constructor):

        if not callable(constructor):
            raise TypeError(f"{constructor} does not appear to be callable.")

        is_class = inspect.isclass(constructor)

        to_call = getattr(constructor, "__init__") if is_class else constructor

        @wraps(constructor)
        def init_wrapper(self, *args, **kwargs):

            _logger = getattr(self, logger) if isinstance(logger, str) \
                else logger() if inspect.isfunction(logger) \
                else logger

            if not isinstance(_logger, loggerClass):
                raise TypeError(
                    f"logger argument had unexpected type {type(_logger)}, expected {loggerClass}")

            if logargs:
                _logger.log(level, f"init: {self.__class__.__name__}({args=}, {kwargs=})",
                            stacklevel=total_depth)
            else:
                _logger.log(level, f"init: {self.__class__.__name__}()", stacklevel=total_depth)

            to_call(self, *args, **kwargs)

        if is_class:
            setattr(constructor, "__init__", init_wrapper)
            return constructor
        else:
            return init_wrapper

    return decorator


def on_init[T](logger: LOGGER_LIKE = DFLT_LOGGER_STR,
               level=logging.DEBUG,
               logargs=True,
               logdefaults=False,
               use_new=False,
               depth=0
               ) -> [T]:
    """
    Decorator for logging initialization calls to a class's __init__ method.
    """
    const_depth = 2
    total_depth = const_depth + depth

    def decorator(constructor):
        if inspect.isclass(constructor):
            original_thing = constructor.__init__
        else:
            original_thing = constructor

        @wraps(original_thing)
        def wrapper(self, *args, **kwargs):
            _logger = _get_logger(self, logger)
            classname = self.__class__.__name__
            result = original_thing(self, *args, **kwargs)
            if logargs:
                log_agnostic(_logger, args, kwargs, self, logdefaults, level, total_depth)
            else:
                log_agnostic(_logger, obj=self, logdefaults=logdefaults, logargs=False,
                             use_new=use_new)
                # log_object(_logger, classname, level, total_depth, 'init')
            return result

        if inspect.isclass(constructor):
            constructor.__init__ = wrapper
        else:
            constructor = wrapper

        return constructor

    return decorator


def on_new(logger: LOGGER_LIKE = DFLT_LOGGER_STR,
           level=logging.DEBUG,
           logargs=True,
           logdefaults=False,
           depth=0):
    """
    Decorator for logging calls to a class's __new__ method.
    """
    const_depth = 2
    total_depth = const_depth + depth

    def decorator(constructor):
        if inspect.isclass(constructor):
            original_thing = constructor.__new__
        else:
            original_thing = constructor

        @wraps(original_thing)
        def wrapper(cls, *args, **kwargs):
            _logger = _get_logger(cls, logger)
            classname = cls.__name__ if inspect.isclass(cls) else cls.__class__.__name__
            if logargs:
                log_agnostic(_logger, args, classname, kwargs, cls, original_thing, logdefaults,
                             level, total_depth)
            else:
                log_object(_logger, classname, level, total_depth, 'new')
            return original_thing(cls, *args, **kwargs)

        if inspect.isclass(constructor):
            setattr(constructor, "__new__", wrapper)
        else:
            constructor = wrapper

        return constructor

    return decorator


# def log_with_args_cl(_logger, args, kwargs, callable_func, logdefaults, level, depth):
#     callable_name = callable_func.__name__
#     bound_arguments = get_bound_args(args, kwargs, callable_func)
#     formatted_args = format_bound_args(bound_arguments, logdefaults)
#     log_object(_logger, callable_name, level, depth, formatted_args)


# if not inspect.isclass(obj) and hasattr(obj, '__init__'):
#     callable_obj = obj.__init__
# elif hasattr(obj, '__call__'):
#     callable_obj = obj.__call__
# else:
#     callable_obj = obj
#
# signature_ = inspect.signature(callable_obj)
# bound_arguments = signature_.bind(*args, **kwargs)
# return bound_arguments


# def binder_func(obj, use_new = False, *args, **kwargs):
#     # args = args or ()
#     # kwargs = kwargs or {}
#     args = args
#     if inspect.isclass(obj):
#         # args = (obj, *args)
#         signature_ = inspect.signature(obj.__new__) if use_new else inspect.signature(obj.__init__)
#     else:
#         signature_ = inspect.signature(obj)
#     res = signature_.bind(*args, **kwargs)
#     return res


def get_bound_args(args, kwargs, cls_or_self, init_or_new):
    init_signature = inspect.signature(init_or_new)
    bound_arguments = init_signature.bind(cls_or_self, *args, **kwargs)
    return bound_arguments


def format_bound_args(bound_arguments, logdefaults):
    if logdefaults:
        bound_arguments.apply_defaults()
    formatted_args = ', '.join(f"{k}={v.__class__.__name__ if k == 'self' or v == 'cls' else v}"
                               for k, v in bound_arguments.arguments.items())
    return formatted_args


def log_object_cl(_logger: LOGGER_CLASS, callable_name: str, level, depth, formatted_args=None):
    formatted_args = formatted_args or ''
    _logger.log(level, f"{callable_name}({formatted_args})", stacklevel=depth)


def log_object(_logger: LOGGER_CLASS, classname: str, level, depth, msg_prefix: str,
               formatted_args=None):
    formatted_args = formatted_args or ''
    _logger.log(level, f"{msg_prefix}: {classname}({formatted_args})", stacklevel=depth)
