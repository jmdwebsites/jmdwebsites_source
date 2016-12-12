import logging.config
import os
import click

def remove(filename):
    try:
        os.remove(filename)
    except OSError as e:
        if e.errno == 2:
            pass
        else:
            raise

def config_logging(log_file_name=None):
    _config = {
        "version":1,
        "disable_existing_loggers":False,
        "handlers":{
            "console":{
                "class":"logging.StreamHandler",
                "formatter":"levelname",
                "stream":"ext://sys.stdout",
                "level":"DEBUG", 
            },
            "console_jmdwebsites":{
                "class":"logging.StreamHandler",
                "formatter":"brief",
                "stream":"ext://sys.stdout",
                "level":"DEBUG", 
            },
        },
        "formatters":{
            "bare":{
                "format": "%(message)s"
            },
            "levelname":{
                "format": "%(levelname)s: %(message)s"
            },
            "brief":{
                "format": "%(levelname)s:%(name)s: %(message)s"
            },
            "precise":{
                "format": "[%(asctime)s %(levelname)s:%(name)s]\n%(message)s"
            },
            "debug":{
                "datefmt": "%Y-%m-%d %H:%M:%S",
                "format": "%(asctime)s %(levelname)s [%(name)s, %(lineno)d] %(message)s"
            },
            "tagged":{
                "format": "%(message)s\t[%(levelname)s:%(name)s %(asctime)s]"
            },
        },
        "root":{
            "handlers":["console"],
            "level":"DEBUG",
        },
        "loggers":{
            "jmdwebsites":{
                "handlers":["console_jmdwebsites"],
                "level":"DEBUG",
                "propagate": False,
            },
        },
    }
    if log_file_name:
        click.echo('Log to {}'.format(log_file_name))
        _config['handlers']['logfile'] = {
            "class":"logging.handlers.RotatingFileHandler",
            "formatter":"debug",
            "filename":log_file_name,
            "maxBytes":"1024",
            "backupCount":"3",
            "level":"DEBUG",
        }
        _config['root']['handlers'].append('logfile')
        _config['loggers']['jmdwebsites']['handlers'].append('logfile')
        remove(log_file_name)
    logging.config.dictConfig(_config)
    

