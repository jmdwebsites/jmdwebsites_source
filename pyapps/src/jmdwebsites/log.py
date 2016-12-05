import logging.config
import os

def config_logging(test_session_log_file):
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
            "logfile":{
                "class":"logging.handlers.RotatingFileHandler",
                "formatter":"debug",
                "filename":test_session_log_file,
                "maxBytes":"1024",
                "backupCount":"3",
                "level":"DEBUG",
            },
            "console_jmdwebsites":{
                "class":"logging.StreamHandler",
                "formatter":"brief",
                "stream":"ext://sys.stdout",
                "level":"DEBUG", #use WARNING normally
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
            "handlers":["console", "logfile"],
            "level":"DEBUG",
        },
        "loggers":{
            "jmdwebsites":{
                "handlers":["console_jmdwebsites", "logfile"],
                "level":"DEBUG",
                "propagate": False,
            },
        },
    })

