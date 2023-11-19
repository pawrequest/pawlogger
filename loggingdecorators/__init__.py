import sys

from .decorators import on_init, on_call
if sys.version_info >= (3, 12):
    from loggingdecorators.future.on_new_dec_312 import on_new
else:
    if sys.version_info < (3, 8):
        print("Unsupported Python version")
    from loggingdecorators.on_new_dec_38 import on_new
