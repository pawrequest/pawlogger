from pathlib import Path

import pycommence.wrapper.cmc_db
from pycommence import api

from pawlogger import on_class
from pawlogger import configure_logging



def test_logging(caplog, tmp_path: Path, log_level, log_message, level_name, format_args):
    log_file = tmp_path / "test.log"
    logger = configure_logging(log_file.name, level=log_level, log_file=log_file)

    assert log_file.exists()
    with open(log_file) as file:
        log_contents = file.read()

    expected_pattern = re.compile(
        f"{level_name} - \\d{{4}}-\\d{{2}}-\\d{{2}} \\d{{2}}:\\d{{2}}:\\d{{2}},\\d{{3}} - test_l_config:\\d{{2}} - {re.escape(formatted_message)}\n")
    assert expected_pattern.search(log_contents)





def test_cmcq(tmp_path):
    loggername = __name__
    tmpfile = tmp_path / loggername + loggername + '.log'
    logger = configure_logging(logger_name=loggername, log_file=tmpfile)
    decorated = on_class(logger=logger, logdefaults=True)(api.CmcDB)
    db = decorated('Commence.DB')
    assert isinstance(db, pycommence.wrapper.cmc_db.CmcConnection)
    ...
