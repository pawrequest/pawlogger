# ruff: noqa: F401
import sys

from .decorators import on_init, on_call, on_new, on_class

# if sys.version_info >= (3, 12):
#     from loggingdecorators.future.on_new_dec_312 import on_new
# else:
#     if sys.version_info < (3, 8):
#         print("Unsupported Python version")
#     from .decorators import on_new
