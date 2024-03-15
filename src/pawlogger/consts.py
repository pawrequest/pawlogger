ASCTIME_PATTERN = r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3}"
CONSOLE_FORMAT_STR = '{levelname} - {module}:{lineno} - {message}'
FILE_FORMAT_STR = '{levelname} - {asctime} - {module}:{lineno} - {message}'


def get_format_str(match_regex=False, console_or_file='file'):
    ret_str = ''
    return ret_str
