import inspect
import logging
from typing import Callable, Union

DFLT_LOGGER_STR = "DEFAULT_LOGGER_STR"
DFLT_LOG_LEVEL = logging.DEBUG
LOGGER_CLASS = logging.getLoggerClass()
LOGGER_LIKE = Union[str, LOGGER_CLASS, Callable]


def call_msg(func_name, args=None, kwargs=None, logargs=True, logdefaults=False):
    if all([args is None, kwargs is None, logargs]):
        raise ValueError("Must provide either args or kwargs if logargs is True")

    args, kwargs = args or [], kwargs or {}

    arg_details = f": {args}" if args else ""
    arg_msg = f"{len(args)} arg(s){arg_details}"

    kwarg_details = f" : {kwargs}" if kwargs else ""
    kwarg_msg = f"{len(kwargs)} kwarg(s){kwarg_details}"

    content = f"calling {func_name} with {arg_msg} and {kwarg_msg}"
    return content


def class_msg2(cls_or_self, use_new=False, args=None, kwargs=None, logargs=True, logdefaults=False):
    if all([args is None, kwargs is None, logargs]):
        raise ValueError("Must provide either args or kwargs if logargs is True")

    args, kwargs = args or [], kwargs or {}

    arg_details = f": {args}" if args else ""
    arg_msg = f"{len(args)} arg(s){arg_details}"

    kwarg_details = f" : {kwargs}" if kwargs else ""
    kwarg_msg = f"{len(kwargs)} kwarg(s){kwarg_details}"

    method_type = "creating" if use_new else "initializing"
    content = f"{method_type} {cls_or_self.__class__.__name__} with {arg_msg} and {kwarg_msg}"
    return content


def build_log_msg(obj, args: dict = None, logargs=True, use_new=False):
    if args is None and logargs:
        raise ValueError('if want to log args then provide some!')
    args = {k: v for k, v in args.items() if k not in ['self', 'cls']} if args else {}
    arg_details = ': ' + ', '.join([f"{k} = {v}" for k, v in args.items()]) if args else ""
    arg_msg = f"{len(args)} arg(s){arg_details}"

    if inspect.isfunction(obj) or inspect.ismethod(obj):
        content = f"calling {obj.__name__} with {arg_msg}"

    elif inspect.isclass(obj):
        method_type = "new:" if use_new else "init:"
        class_name = obj.__name__ if inspect.isclass(obj) else obj.__class__.__name__
        content = f"{method_type} {class_name} with {arg_msg}"
    else:
        raise TypeError("Unsupported object type for logging")

    return content
