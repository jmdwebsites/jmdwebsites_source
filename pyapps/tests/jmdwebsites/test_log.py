from __future__ import print_function
import logging

import py
import pytest

import jmdwebsites

_logger = logging.getLogger(__name__)


@pytest.fixture(autouse=True)
def setup():
    # Override setup() from conftest.py, which protects against a logging reload
    print('\nSetup the test from test_log')
    jmdwebsites.log.reset_logging()
    yield
    print('\nTear down the test from test_log')


pytestmark = [
    # Reloading logging interferes with other test modules'
    # So the tests in this module should be run on their own
    pytest.mark.skipif(
        not pytest.config.getoption('--testlogging'),
        reason = 'need --testlogging to run the test in this module',
    )
]


def log_to_all(logger):
    ''' Exercise each logging level.
    Do not change this function, it is used for tests,
    which rely on the relative line number of the logger calls
    '''
    logger.critical("critical")
    logger.error("error")
    logger.warning("warning")
    logger.info("info")
    logger.debug("debug")


def test_config_logging__root_logger(capsys):
    jmdwebsites.log.config_logging(disable_existing_loggers = False)
    root_logger = logging.getLogger()
    assert [h.name for h in root_logger.handlers] == ['console']
    assert isinstance(root_logger.handlers[0], logging.StreamHandler)
    assert not logging.raiseExceptions
    logging.raiseExceptions = 1
    log_to_all(root_logger)
    out, err = capsys.readouterr()
    print("stdout = {}\nstderr = {}".format(repr(out), repr(err)))
    assert out == u'critical\n'
    assert err == u''


formats = {
    'empty': '',
    'bare':  '{msg}\n',
    'levelname': '{level}: {msg}\n',
    'brief': '{level}:{logger}: {msg}\n',
    'debug': '{level}:{logger}:{lineno}: {msg}\n',
}
def render(tpl, lvl, offset):
    lineno = log_to_all.func_code.co_firstlineno + 5 + offset
    return tpl.format(level=lvl.upper(), msg=lvl, logger='{logger}', lineno=lineno)
def results(tpl):
    levels = ['critical', 'error', 'warning', 'info', 'debug']
    while levels:
        lvl = levels[-1]
        result_as_a_list = [render(tpl, lvl, i) for i,lvl in enumerate(levels)]
        result = unicode(''.join(result_as_a_list))
        yield lvl, result
        levels.pop()
expected = {fmt:dict(results(tpl)) for fmt,tpl in formats.iteritems()}


@pytest.mark.parametrize('logger_name, args, kargs, expected', [
    ('jmdwebsites.log',   (), {},                               expected['bare']['critical']),
    ('jmdwebsites.log',   ('DEBUG', False, False, 0, None), {}, expected['bare']['debug']),
    ('jmdwebsites.log',   (), {'info':True},                    expected['bare']['info']),
    ('jmdwebsites.log',   (), {'level':'DEBUG'},                expected['bare']['debug']),
    ('jmdwebsites.log',   (), {'level':'DEBUG', 'verbose':1},   expected['levelname']['debug']),
    ('jmdwebsites.log',   (), {'level':'DEBUG', 'verbose':2},   expected['brief']['debug']),
    ('jmdwebsites.log',   (), {'level':'DEBUG', 'verbose':3},   expected['debug']['debug']),
    ('jmdwebsites.log',   (), {'level':'DEBUG', 'verbose':3},   expected['debug']['debug']),
    ('jmdwebsites.log',   (), {'debug':True},                   expected['debug']['debug']),
    ('',   (), {},                               expected['bare']['critical']),
    ('',   (), {'verbose':1},                    expected['levelname']['critical']),
    ('',   (), {'verbose':2},                    expected['levelname']['critical']),
    ('',   (), {'level':'WARNING', 'verbose':3}, expected['brief']['warning']),
    # TODO: Test for the file loger, and file handlers
    #('file', (), {'debug':True},                   expected['empty']['debug']),
])
def test_config_logging(capsys, logger_name, args, kargs, expected):
    jmdwebsites.log.config_logging(*args, disable_existing_loggers = False, **kargs)
    logging.raiseExceptions = 1
    logger = logging.getLogger(logger_name)
    log_to_all(logger)
    out, err = capsys.readouterr()
    print("logger_name = {}, args = {}, kargs = {}".format(repr(logger_name), args, kargs))
    print("stdout = {}\nstderr = {}".format(repr(out), repr(err)))
    assert out == expected.format(logger=logger.name)
    assert err == u''


#############################################################################
# Not needed, so named tst_ instead of test_.
# May develop a test based on this.

working_config = { 
    'version': 1, 
    "disable_existing_loggers": False, 
    "formatters":{
        "bare":{
            "format": "%(message)s"
        },
        "levelname":{
            "format": "%(levelname)s: %(message)s"
        },
    },
    "handlers":{
        "console":{
            "class": "logging.StreamHandler",
            "formatter": "levelname",
            "stream": "ext://sys.stdout",
            "level": 'NOTSET', 
        },
    },
    "root":{
        "handlers":["console"],
        "level": "NOTSET",
    },
}

def tst_dictConfig():
    # Kept this code to demonstrate StdCaptureFD
    assert _logger == logging.getLogger(__name__), \
        '\n!!WARNING!! Module level logger mismatch, logging has been reloaded'
        #TODO: Use a python warning instead, but for now, just print a message
    capture = py.io.StdCaptureFD(out="ext://sys.stdout", in_=False)
    root_logger = logging.getLogger()
    if 1:
        jmdwebsites.log.reset_logging()
        root_logger.critical('logging.getLogger().critical message 1')
        out, err = capture.suspend()
        print('\nout!:', out, end='')
        print('err!:', err)
        assert err == '' and out == '' and not root_logger.handlers, \
            'logging should be set to default config'
        capture.reset()

    if 1:
        logging.config.dictConfig(working_config)
        capture = py.io.StdCaptureFD(out="ext://sys.stdout", in_=False)
        root_logger.critical("logging.getLogger().critical message 2")
        out, err = capture.suspend()
        print('2out!:', out, end='')
        print('2err!:', err)
        assert out == 'CRITICAL: logging.getLogger().critical message 2\n' and err == ''
        capture.resume()


    if 1:
        logging.disable(logging.NOTSET)
        root_logger.log(1, 'logging.getLogger().log message 3')
        out, err = capture.suspend()
        print('out!:', out, end='')
        print('err!:', err)
        assert out == 'Level 1: logging.getLogger().log message 3\n' and err == ''
        capture.resume()

    logging.disable(logging.CRITICAL)
    root_logger.critical("logging.getLogger().critical message 4")
    out, err = capture.suspend()
    capture.reset()
    assert err == '' and out == ''

    assert logging.raiseExceptions
    logging.disable(logging.NOTSET)
    root_logger.critical("logging.getLogger().critical message 5")

    print("&&&&&&&&&&&&&&&&&&&&&&")
    print('\nStart the test')
    yield
    print('\nFinished the test')
