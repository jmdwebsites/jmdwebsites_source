from __future__ import print_function
import pytest
import jmdwebsites
from jmdwebsites import Website
import os
import logging
import logging.config
import py

_logger = logging.getLogger(__name__)

@pytest.fixture(scope='session', autouse=True)
def session():
    print('\nSetup the test session')
    capture = py.io.StdCaptureFD(out=False, in_=False)
    logging.getLogger().critical('logging.getLogger().critical first msg!')
    logging.getLogger().critical('logging.getLogger().critical second msg!')
    out, err = capture.reset()
    assert err == 'No handlers could be found for logger "root"\n', \
        'logging has been used or configured already'
    print('Start the test session', end='')
    yield
    print('\nTear down the test session', end='')

@pytest.fixture(scope='module', autouse=True)
def module():
    print('\nStart the test module', end='')
    jmdwebsites.log.reset_logging()
    yield
    print('\nTear down the test module')

@pytest.fixture(autouse=True)
def setup():
    print('\nSetup the test')
    assert _logger == logging.getLogger(__name__), \
        '\n!!WARNING!! Module level logger mismatch, logging has been reloaded'
        #TODO: Use a python warning instead, but for now, just print a message
    capture = py.io.StdCaptureFD(out="ext://sys.stdout", in_=False)
    root_logger = logging.getLogger()
    root_logger.critical('logging.getLogger().critical message 1')
    out, err = capture.reset()
    assert err == '' and out == '' and not root_logger.handlers, \
        'logging should be set to default config'
    print('Start the test')
    yield
    print('\nFinished the test')

@pytest.fixture()
def tmpcwd(tmpdir):
    with tmpdir.as_cwd():
        yield tmpdir

@pytest.fixture()
def loginfo():
    print('Setup loginfo')
    jmdwebsites.log.config_logging(info = True, verbose = 1)
    yield
    print('\nTear down loginfo')
    jmdwebsites.log.reset_logging()

@pytest.fixture()
def logdebug():
    print('Setup logdebug')
    jmdwebsites.log.config_logging(debug = True, verbose = 1)
    yield
    print('\nTear down logdebug')
    jmdwebsites.log.reset_logging()

@pytest.fixture()
def logopt(request):
    print('Setup logopt')
    jmddbg = request.config.getoption("--jmddbg")
    jmdinfo = request.config.getoption("--jmdinfo")
    jmdwebsites.log.config_logging(debug = jmddbg, info = jmdinfo, verbose = 1)
    yield
    print('\nTear down logdebug')
    jmdwebsites.log.reset_logging()

@pytest.fixture()
def website(tmpdir, request):
    site_dir = request.getfuncargvalue('site_dir')
    with site_dir.as_cwd():
        print('cwd: {}'.format(os.getcwd()))
        yield Website(build_dir = tmpdir.join('build'))
    print('\ncwd: {}'.format(os.getcwd()), end='')


###########################################################################
# Don't use this fixture!
if 0:
    @pytest.fixture()
    def logreset():
        logging.shutdown()
        reload(logging)
        assert logging._handlerList == []
        root_logger = logging.getLogger()
        assert logging.getLogger('') is root_logger
        assert root_logger.handlers == []
        assert logging.raiseExceptions

