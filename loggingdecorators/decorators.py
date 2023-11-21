import inspect
import logging
from functools import wraps
from typing import Callable, Type, TypeVar, Union

LOGGER_CLASS = logging.getLoggerClass()
DFLT_LOGGER_STR = "logger"
LOGGER_LIKE = Union[str, LOGGER_CLASS, Callable]
T = TypeVar('T', bound=Type)


def on_call(logger: Union[LOGGER_CLASS, Callable], level=logging.DEBUG, logargs=True, msg: str = "",
            depth=0):
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
                raise TypeError(
                    f"logger argument had unexpected type {type(_logger)}, expected {LOGGER_CLASS}")

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
                _logger.log(level, f" - kwarg {m:>2}: {type(item)} {key}={item}",
                            stacklevel=total_depth)

        return wrapper

    return decorator


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


def log_object(_logger: LOGGER_CLASS, classname: str, level, depth, msg_prefix: str,
               formatted_args=None):
    formatted_args = formatted_args or ''
    _logger.log(level, f"{msg_prefix}: {classname}({formatted_args})", stacklevel=depth)


def log_with_args(_logger, args, classname, kwargs, cls_or_self, init_or_new, logdefaults, level,
                  depth):
    msg_prefix = 'init' if init_or_new.__name__ == '__init__' else 'new' if init_or_new.__name__ == '__new__' else None
    if msg_prefix is None:
        raise ValueError(f"Unexpected method name {init_or_new.__name__}")

    bound_arguments = get_bound_args(args, kwargs, cls_or_self, init_or_new)
    formatted_args = format_bound_args(bound_arguments, logdefaults)
    log_object(_logger, classname, level, depth, msg_prefix, formatted_args)


def on_init(logger: LOGGER_LIKE = DFLT_LOGGER_STR,
            level=logging.DEBUG,
            logargs=True,
            logdefaults=False,
            depth=0
            ):
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
            classname = self.__class__.__name__
            _logger = _get_logger(self, logger)
            result = original_thing(self, *args, **kwargs)
            if logargs:
                log_with_args(_logger, args, classname, kwargs, self, original_thing, logdefaults,
                              level, total_depth)
            else:
                log_object(_logger, classname, level, total_depth, 'init')
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
                log_with_args(_logger, args, classname, kwargs, cls, original_thing, logdefaults,
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

def _get_logger(cls_or_self, logger: LOGGER_LIKE):
    if isinstance(logger, LOGGER_CLASS):
        return logger
    elif callable(logger):
        return logger()
    elif isinstance(logger, str):
        return getattr(cls_or_self, logger, logging.getLogger(logger))
    else:
        raise TypeError(
            f"logger argument had unexpected type {type(logger)}, expected {LOGGER_CLASS}")


def on_unified(logger: LOGGER_LIKE = DFLT_LOGGER_STR,
               level=logging.DEBUG,
               logargs=True,
               logdefaults=False,
               depth=0,
               decorate_init=True,
               decorate_new=False):
    """
    Unified decorator for logging calls to a class's __init__ and/or __new__ methods.
    """
    const_depth = 2
    total_depth = const_depth + depth

    def decorator(constructor):
        if inspect.isclass(constructor):
            original_init = constructor.__init__ if decorate_init else None
            original_new = constructor.__new__ if decorate_new else None
        else:
            original_init = original_new = constructor if decorate_init or decorate_new else None

        def wrap_function(original_function, msg_prefix):
            @wraps(original_function)
            def wrapper(*args, **kwargs):
                _logger = _get_logger(args[0], logger)
                classname = args[0].__class__.__name__ if msg_prefix == 'init' else args[0].__name__
                if logargs:
                    log_with_args(_logger, args, classname, kwargs, args[0], original_function, logdefaults, level, total_depth)
                else:
                    log_object(_logger, classname, level, total_depth, msg_prefix)
                return original_function(*args, **kwargs)
            return wrapper

        if original_init:
            constructor.__init__ = wrap_function(original_init, 'init')
        if original_new:
            setattr(constructor, '__new__', wrap_function(original_new, 'new'))

        return constructor

    return decorator