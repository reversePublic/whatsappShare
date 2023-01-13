import json
import logging
import os
import re, time
from logging import Logger
from logging.handlers import TimedRotatingFileHandler

from env.env_app import app_env

currentPath = os.path.dirname(__file__) + '/logs/'
# currentPath = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + '/logs'

class FinalLogger():

    def init_logger(self, logger_name):

        if logger_name not in Logger.manager.loggerDict:
            logger = logging.getLogger(logger_name)
            logger.setLevel(logging.DEBUG)
            log_path = os.path.join(currentPath, logger_name)
            msg = {
                "app": os.getenv('APP'),
                "@timestamp": "%(asctime)s",
                "date": "%(asctime)s",
                "logLevel": "%(levelname)s",
                "file": "%(pathname)s:%(lineno)d",
                "msg": "%(message)s"
            }
            format_str = json.dumps(msg)
            formatter = logging.Formatter(format_str, '%Y-%m-%dT%H:%M:%SZ')

            fileHandler = TimedRotatingFileHandler(filename=log_path, when="midnight", backupCount=7)
            fileHandler.suffix = "%Y-%m-%d.log"
            fileHandler.extMatch = re.compile(r"^\d{4}-\d{2}-\d{2}.log$")
            fileHandler.setFormatter(formatter)
            logger.addHandler(fileHandler)

        logger = logging.getLogger(logger_name)
        return logger

class FinalLogger2():

    def init_logger(self, logger_name1=None):

        num = app_env()
        if num == 1:
            logger_name = "1546944914"
        elif num == 2:
            logger_name = "4615761317"
        elif num == 3:
            logger_name = "6412722277"
        else:
            logger_name = "8728356502"

        logger_name = time.strftime('%Y-%m-%d', time.localtime()) + "--" + logger_name + "-" + "Info" + '.log'

        if logger_name not in Logger.manager.loggerDict:
            logger = logging.getLogger(logger_name)
            logger.setLevel(logging.DEBUG)

            # allfilename = time.strftime('%Y-%m-%d', time.localtime()) + "--" + logger_name + "-" + "Info" + '.log'
            all_log_file = os.path.join(currentPath, logger_name)
            msg = {
                "app": os.getenv('APP'),
                "@timestamp": "%(asctime)s",
                "date": "%(asctime)s",
                "logLevel": "%(levelname)s",
                "file": "%(pathname)s:%(lineno)d",
                "msg": "%(message)s",
            }
            format_str = json.dumps(msg)

            formatter = logging.Formatter(format_str, '%Y-%m-%dT%H:%M:%SZ')
            fileHandler = logging.FileHandler(all_log_file)
            fileHandler.setFormatter(formatter)
            logger.addHandler(fileHandler)

        logger = logging.getLogger(logger_name)
        return logger

class FinalLogger1():

    def init_logger(self, logger_name):

        num = app_env()
        if num == 1:
            logger_name = "1546944914"
        elif num == 2:
            logger_name = "4615761317"
        elif num == 3:
            logger_name = "6412722277"
        else:
            logger_name = "8728356502"

        if logger_name not in Logger.manager.loggerDict:

            logger = logging.getLogger(logger_name)
            logger.setLevel(logging.DEBUG)

            allfilename = time.strftime('%Y-%m-%d', time.localtime()) + "--" + logger_name + "-" + "Info" + '.log'
            all_log_file = os.path.join(currentPath, allfilename)

            msg = {
                "app": os.getenv('APP'),
                "@timestamp": "%(asctime)s",
                "date": "%(asctime)s",
                "logLevel": "%(levelname)s",
                "file": "%(pathname)s:%(lineno)d",
                "msg": "%(message)s",
            }
            format_str = json.dumps(msg)
            formatter = logging.Formatter(format_str, '%Y-%m-%dT%H:%M:%SZ')

            all_log_handler = TimedRotatingFileHandler(all_log_file, when='midnight', backupCount=7)
            all_log_handler.setFormatter(formatter)
            all_log_handler.setLevel(logging.INFO)
            logger.addHandler(all_log_handler)

        logger = logging.getLogger(logger_name)
        return logger
