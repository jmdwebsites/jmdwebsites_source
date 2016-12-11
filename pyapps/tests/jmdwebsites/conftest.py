from __future__ import print_function
import pytest
import logging
#import py
#import sys
import jmdwebsites
from jmdwebsites import Website
import os

def remove(filename):
    try:
        os.remove(filename)
    except OSError as e:
        if e.errno == 2:
            pass
        else:
            raise

@pytest.fixture(scope='session', autouse=True)
def setup_test_session():
    print('\nStart the test session.', end='')
    log_file = 'testsession.log'
    remove(log_file)
    jmdwebsites.log.config_logging(log_file)
    yield
    print('Finished the test session.', end='')

@pytest.fixture(autouse=True)
def setup_test():
    print('\nStart the test.')
    yield
    print('\nFinished the test.')

@pytest.fixture()
def website(setup_test, tmpdir, request):
    site_dir = request.getfuncargvalue('site_dir')
    print('cwd {}'.format(os.getcwd()))
    with site_dir.as_cwd():
        print('cwd {}'.format(os.getcwd()))
        yield Website(build_dir = tmpdir)
    print('\ncwd {}'.format(os.getcwd()), end='')
