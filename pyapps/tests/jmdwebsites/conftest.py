from __future__ import print_function
import pytest
from jmdwebsites import Website
import jmdwebsites
import os


@pytest.fixture(scope='session', autouse=True)
def setup_test_session():
    print('\nSetup the test session')
    jmdwebsites.log.config_logging(log_file_name='testsession.log')
    print('Start the test session', end='')
    yield
    print('Finished the test session', end='')

@pytest.fixture(autouse=True)
def setup_test():
    print('\nStart the test')
    yield
    print('\nFinished the test')

@pytest.fixture()
def website(setup_test, tmpdir, request):
    site_dir = request.getfuncargvalue('site_dir')
    print('cwd {}'.format(os.getcwd()))
    with site_dir.as_cwd():
        print('cwd {}'.format(os.getcwd()))
        yield Website(build_dir = tmpdir.join('build'))
    print('\ncwd {}'.format(os.getcwd()), end='')
