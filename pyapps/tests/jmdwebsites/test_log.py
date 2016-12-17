from __future__ import print_function
import pytest
import jmdwebsites
import logging


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


def test_config_logging__root_logger(logreset, capsys):
    root_logger = logging.getLogger()
    root_logger.critical('Critical!')
    out, err = capsys.readouterr()
    assert out == u''
    assert err == u'No handlers could be found for logger "root"\n'

    jmdwebsites.log.config_logging()
    assert not logging.raiseExceptions
    assert [h.name for h in root_logger.handlers] == ['console']
    assert isinstance(root_logger.handlers[0], logging.StreamHandler)
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
def test_config_logging(logreset, capsys, logger_name, args, kargs, expected):
    jmdwebsites.log.config_logging(*args, **kargs)
    logger = logging.getLogger(logger_name)
    log_to_all(logger)
    out, err = capsys.readouterr()
    print("logger_name = {}, args = {}, kargs = {}".format(repr(logger_name), args, kargs))
    print("stdout = {}\nstderr = {}".format(repr(out), repr(err)))
    assert out == expected.format(logger=logger.name)
    assert err == u''
