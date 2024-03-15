import inspect
import logging
from functools import wraps

from .consts_formats import DFLT_LOGGER_STR, LOGGER_CLASS, LOGGER_LIKE, \
    build_log_msg


# from src.pawlogger.legacy import log_object


def on_call(logger: LOGGER_LIKE, level=logging.DEBUG, logargs=True,
            logdefaults=False, msg: str = "",
            depth=0):
    """
    Decorate a function with a wrapper which logs the call at the specified level.
    Increase depth by 1 for each level of decorator nesting.
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
            _logger = _get_logger(func, logger)
            logger.debug(f'logger {logger.name}')

            if not isinstance(_logger, LOGGER_CLASS):
                raise TypeError(
                    f"logger argument had unexpected type {type(_logger)}, expected {LOGGER_CLASS}")

            result = func(*args, **kwargs)
            if logargs:
                log_agnostic(_logger, func, level, total_depth, logargs=logargs, args=args,
                             kwargs=kwargs, logdefaults=logdefaults)
            else:
                log_agnostic(_logger, func, level, logargs=False, depth=total_depth)
            return result

        return wrapper

    return decorator


#
# def on_class(logger: LOGGER_LIKE = DFLT_LOGGER_STR,
#              level=logging.DEBUG,
#              logargs=True,
#              logdefaults=False,
#              depth=0,
#              decorate_init=True,
#              decorate_new=False):
#     """
#     Unified decorator for logging calls to a class's __init__ and/or __new__ methods.
#     """
#     const_depth = 2
#     total_depth = const_depth + depth
#
#     def decorator(cls):
#         if not inspect.isclass(cls):
#             raise TypeError("on_class decorator can only be applied to classes.")
#
#         original_init = cls.__init__ if decorate_init and hasattr(cls, '__init__') else None
#         original_new = cls.__new__ if decorate_new and hasattr(cls, '__new__') else None
#
#         def wrap_function(original_function, method_name):
#             @wraps(original_function)
#             def wrapper(*args, **kwargs):
#                 _logger = _get_logger(cls, logger)
#                 if logargs:
#                     bound_arguments = get_bound(cls, use_new=use_new,
#                                                 logdefault=logdefaults, args=args, kwargs=kwargs)
#                     log_msg = build_log_msg(cls, args=bound_arguments.arguments,
#                                             use_new=(method_name == 'new'))
#                 else:
#                     log_msg = build_log_msg(cls, logargs=False, use_new=(method_name == 'new'))
#
#                 _logger.log(level=level, msg=log_msg, stacklevel=total_depth)
#                 return original_function(*args, **kwargs)
#
#             return wrapper
#
#         if original_init:
#             cls.__init__ = wrap_function(original_init, 'init')
#         if original_new:
#             cls.__new__ = wrap_function(original_new, 'new')
#
#         return cls
#
#     return decorator
#
def on_class[T](logger: LOGGER_LIKE = DFLT_LOGGER_STR,
                level=logging.DEBUG,
                logargs=True,
                logdefaults=False,
                depth=0,
                decorate_init=True,
                decorate_new=False) -> T:
    """
    Decorator for logging calls to a class's __init__ and/or __new__ methods.
    If decorate_init is True, replace the class __init__ method with a wrapped version.
    If decorate_new is True, do the same for the __new__ method.
    """

    def decorator(cls):
        if not inspect.isclass(cls):
            raise TypeError("on_class decorator can only be applied to classes.")

        if decorate_init and hasattr(cls, '__init__'):
            original_init = cls.__init__
            wrapped_init = on_call(logger, level, logargs, logdefaults, depth=depth + 1)(
                original_init)
            cls.__init__ = wrapped_init

        if decorate_new and hasattr(cls, '__new__'):
            original_new = cls.__new__
            wrapped_new = on_call(logger, level, logargs, logdefaults, depth=depth + 1)(
                original_new)
            cls.__new__ = wrapped_new

        return cls

    return decorator


def get_bound(obj, use_new=False, logdefault=False, args=None, kwargs=None):
    args = args or ()
    kwargs = kwargs or {}

    if inspect.isclass(obj):
        init_or_new = obj.__new__ if use_new else obj.__init__
        signature_ = inspect.signature(init_or_new)
        args = obj, *args
    elif callable(obj):
        signature_ = inspect.signature(obj)
    else:
        raise TypeError()

    bound_arguments = signature_.bind(*args, **kwargs)
    if logdefault:
        bound_arguments.apply_defaults()

    return bound_arguments


def log_agnostic(_logger, obj, level, depth, args=None, kwargs=None, logargs=True,
                 logdefaults=False,
                 use_new=False):
    if logargs and args is None:
        raise ValueError("if logargs then provide them")
    args, kwargs = args or (), kwargs or {}
    if logargs:
        bound_arguments = get_bound(obj=obj, use_new=use_new, logdefault=logdefaults, args=args,
                                    kwargs=kwargs)
        log_msg = build_log_msg(obj, args=bound_arguments.arguments, use_new=use_new)
    else:
        log_msg = build_log_msg(obj, logargs=False, use_new=use_new)

    _logger.log(level=level, msg=log_msg, stacklevel=depth)
    ...


def _get_logger(objec, loggerlike: LOGGER_LIKE):
    if isinstance(loggerlike, LOGGER_CLASS):
        _logger = loggerlike

    elif isinstance(loggerlike, str):
        _logger = getattr(objec, loggerlike, None)
        _logger = _logger or logging.getLogger(loggerlike)

    elif callable(loggerlike):
        _logger = loggerlike()

    else:
        raise TypeError(
            f"logger argument had unexpected type {type(loggerlike)}, expected {LOGGER_CLASS}")

    if not isinstance(_logger, LOGGER_CLASS):
        raise ValueError(f'Unable to get logger {loggerlike}')

    return _logger
