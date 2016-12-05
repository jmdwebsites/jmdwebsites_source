import pytest
import logging
import py
import sys
import jmdwebsites
import os

def remove(filename):
    try:
        os.remove(filename)
    except OSError as e:
        if e.errno == 2:
            pass
        else:
            raise

@pytest.fixture(autouse=True)
def _before_and_after(request):
    print("")
    def tear_down():
        print("")
    request.addfinalizer(tear_down)

@pytest.fixture()
def setup_test(request):
    print('Fixture: Setup the test.')
    yield
    print('\nFixture: Tear down test.')



@pytest.fixture(scope='session')
def setup_test_session(request):
    log_file = 'testsession.log'
    remove(log_file)
    jmdwebsites.log.config_logging(log_file)
    print('Fixture: Setup the test session.')
    yield
    print('Fixture: Tear down the test session.')
