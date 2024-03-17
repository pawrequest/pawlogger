from .config_loguru import get_loguru
from .config import get_logger
from .consts import ASCTIME_PATTERN, CONSOLE_FORMAT_STR, FILE_FORMAT_STR, get_format_str
# ASCTIME_PATTERN = r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3}"
# CONSOLE_FORMAT_STR = '{levelname} - {module}:{lineno} - {message}'
# FILE_FORMAT_STR = '{levelname} - {asctime} - {module}:{lineno} - {message}'
#
#
# def get_format_str(match_regex=False, console_or_file='file'):
#     ret_str = ''
#     return ret_str


__all__ = ['get_logger', 'get_loguru', 'ASCTIME_PATTERN', 'CONSOLE_FORMAT_STR', 'FILE_FORMAT_STR',
           'get_format_str']
