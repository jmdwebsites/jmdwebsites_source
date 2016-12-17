from __future__ import print_function
import pytest
from jmdwebsites import Website
import jmdwebsites
import os
import logging


def reset_logging():
    logging.shutdown()
    reload(logging)
    root_logger = logging.getLogger()
    assert logging._handlerList == []
    assert logging.getLogger('') is root_logger
    assert root_logger.handlers == []
    assert logging.raiseExceptions

def setup_logging():
    jmdwebsites.log.config_logging()

@pytest.fixture()
def logreset():
    reset_logging()
    yield
    reset_logging()
    setup_logging()

@pytest.fixture(scope='module')
def mlogreset():
    reset_logging()
    yield
    reset_logging()
    setup_logging()

@pytest.fixture(autouse=True)
def setup():
    print('\nStart the test')
    yield
    print('\nFinished the test')

@pytest.fixture(scope='module', autouse=True)
def module():
    print('\nStart the module', end='')
    yield
    print('\nFinished the module')

@pytest.fixture(scope='session', autouse=True)
def session():
    print('\nSetup the test session')
    reset_logging()
    setup_logging()
    print('Start the test session', end='')
    yield
    print('\nFinished the test session', end='')

@pytest.fixture()
def website(tmpdir, request):
    site_dir = request.getfuncargvalue('site_dir')
    print('cwd {}'.format(os.getcwd()))
    with site_dir.as_cwd():
        print('cwd {}'.format(os.getcwd()))
        yield Website(build_dir = tmpdir.join('build'))
    print('\ncwd {}'.format(os.getcwd()), end='')



