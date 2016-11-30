import pytest
import logging
import logging.config
import os
import py

logger = logging.getLogger(__name__)

def _config_logging(test_session_log_file):
    logging.config.dictConfig({
        "version":1,
        "disable_existing_loggers":False,
        "handlers":{
            "console":{
                "class":"logging.StreamHandler",
                "formatter":"levelname",
                "stream":"ext://sys.stdout",
                "level":"DEBUG", #use WARNING normally
            },
            "console_test":{
                "class":"logging.StreamHandler",
                "formatter":"levelname_test",
                "stream":"ext://sys.stdout",
                "level":"DEBUG", #use WARNING normally
            },
            "logfile":{
                "class":"logging.handlers.RotatingFileHandler",
                "formatter":"debug",
                "filename":test_session_log_file,
                "maxBytes":"1024",
                "backupCount":"3",
                "level":"DEBUG",
            }
        },
        "formatters":{
            "bare":{
                "format":"%(message)s"
            },
            "levelname":{
                "format":"%(levelname)s: %(message)s"
            },
            "levelname_test":{
                "format":"%(levelname)s:TEST: %(message)s"
            },
            "brief":{
                "format":"%(levelname)s:%(name)s: %(message)s"
            },
            "precise":{
                "format":"[%(asctime)s %(levelname)s:%(name)s]\n%(message)s"
            },
            "debug":{
                "format":"[%(asctime)s LOGGER=%(name)s, FILE=%(pathname)s, LINE=%(lineno)d]\n%(levelname)s: %(message)s\n"
            },
            "tagged":{
                "format":"%(message)s\t[%(levelname)s:%(name)s %(asctime)s]"
            },
        },
        "root":{
            "handlers":["console", "logfile"],
            "level":"DEBUG",
        },
        "loggers":{
            "tests":{
                "handlers":["console_test", "logfile"],
                "level":"DEBUG",
                "propagate": False,
            },
        },
    })

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
def setup_test():
    logger.info('Fixture: Setup the test.')

@pytest.fixture(scope='session')
def setup_test_session(request):
    log_file = 'testsession.log'
    remove(log_file)
    _config_logging(log_file)
    logger.info('Fixture: Setup the test session.')

    #owd = os.getcwd()
    #os.chdir('tmptmp')
    def tear_down():
        print ""
        logger.info('Fixture: Tear down the test session.')
        #os.chdir(owd)
    request.addfinalizer(tear_down)
