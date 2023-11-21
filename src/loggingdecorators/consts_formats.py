ARG0_INT_10 = " - arg  0: <class 'int'> 10"
ARG1_INT_20 = " - arg  1: <class 'int'> 20"


def call_msg(func_name, args = None, kwargs= None, logargs=True, logdefaults=False):
    if all([args is None, kwargs is None, logargs]):
        raise ValueError("Must provide either args or kwargs if logargs is True")

    if args is None:
        args = []
    if kwargs is None:
        kwargs = {}

    arg_details = f": {args}" if args else ""
    kwarg_details = f" : {kwargs}" if kwargs else ""
    arg_msg = f"{len(args)} arg(s){arg_details}"
    kwarg_msg = f"{len(kwargs)} kwarg(s){kwarg_details}"
    content = f"calling {func_name} with {arg_msg} and {kwarg_msg}"
    return content


# def log_args(_logger, args, kwargs):
#     for n, arg in enumerate(args):
#         _logger.log(level, f" - arg {n:>2}: {type(arg)} {arg}", stacklevel=total_depth)
#     for m, (key, item) in enumerate(kwargs.items()):
#         _logger.log(level, f" - kwarg {m:>2}: {type(item)} {key}={item}",
#                     stacklevel=total_depth)
