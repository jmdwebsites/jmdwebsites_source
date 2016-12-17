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

def config_logging(level=None, info=False, debug=False, verbose=0, logfile=None):
    logger_level = 'DEBUG'

    console_handler_level = 'CRITICAL'
    file_handler_level = 'DEBUG'
    if info:
        console_handler_level = 'INFO'
    if debug:
        console_handler_level = 'DEBUG'
        file_handler_level = 'DEBUG'
    if level:
        console_handler_level = level
        file_handler_level = level
    
    _config = {
        "version": 1,
        "disable_existing_loggers": False,
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
                "format": "[%(asctime)s %(name)s:%(levelname)s]\n%(message)s"
            },
            "debug":{
                "format": "%(levelname)s:%(name)s:%(lineno)d: %(message)s"
            },
            "debug_timestamped":{
                "datefmt": "%Y-%m-%d %H:%M:%S",
                "format": "%(asctime)s %(levelname)s:%(name)s:%(lineno)d: %(message)s"
            },
            "file":{
                "datefmt": "%Y-%m-%d %H:%M:%S",
                "format": "%(asctime)s %(levelname)s: %(message)s"
            },
            "tagged":{
                "format": "%(message)s\t[%(levelname)s:%(name)s %(asctime)s]"
            },
        },
        "handlers":{
            "console":{
                "class": "logging.StreamHandler",
                "formatter": "bare",
                "stream": "ext://sys.stdout",
                "level": console_handler_level, 
            },
            "console_jmdwebsites":{
                "class": "logging.StreamHandler",
                "formatter": "bare",
                "stream": "ext://sys.stdout",
                "level": console_handler_level, 
            },
        },
        "root":{
            "handlers":["console"],
            "level":logger_level,
        },
        "loggers":{
            "jmdwebsites":{
                "handlers": ["console_jmdwebsites"],
                "level":logger_level,
                "propagate": False,
            },
        },
    }
    if verbose == 1:
        _config['handlers']['console']['formatter'] = 'levelname' 
        _config['handlers']['console_jmdwebsites']['formatter'] = 'levelname' 
    elif verbose == 2:
        _config['handlers']['console']['formatter'] = 'levelname' 
        _config['handlers']['console_jmdwebsites']['formatter'] = 'brief' 
    elif verbose >= 3:
        _config['handlers']['console']['formatter'] = 'brief' 
        _config['handlers']['console_jmdwebsites']['formatter'] = 'debug' 
    elif debug:
        _config['handlers']['console']['formatter'] = 'debug' 
        _config['handlers']['console_jmdwebsites']['formatter'] = 'debug' 

    if logfile:
        remove(logfile)
        _config['handlers']['file'] = {
            "class": "logging.handlers.RotatingFileHandler",
            #"formatter": "file",
            "formatter": "debug_timestamped",
            "filename": logfile,
            "maxBytes": "1024",
            "backupCount": "3",
            "level": file_handler_level,
        }
        _config['handlers']['file_jmdwebsites'] = {
            "class": "logging.handlers.RotatingFileHandler",
            "formatter": "debug_timestamped",
            "filename": logfile,
            "maxBytes": "1024",
            "backupCount": "3",
            "level": file_handler_level,
        }
        _config['root']['handlers'].append('file')
        _config['loggers']['jmdwebsites']['handlers'].append('file_jmdwebsites')
         # Create a dedicate logger just for writing to logfie
        _config['loggers']['file'] = {
                "handlers": ['file'],
                "level": logger_level,
                "propagate": False,
        }
    logging.config.dictConfig(_config)
    logging.raiseExceptions = 0
    

