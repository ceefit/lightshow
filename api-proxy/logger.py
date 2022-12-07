""" Logging facility """
import logging
import sys


class Logger:
    def get_logger(self, logger_name):
        loglevel = logging.DEBUG
        format = "%(asctime)s - %(levelname)s - %(message)s"
        logger = logging.getLogger(logger_name)
        logger.setLevel(loglevel)
        console_formatter = logging.Formatter(format)

        logFile = 'access.log'
        logging.basicConfig(filename=logFile, filemode='a', level=logging.INFO,
                            format=format, datefmt='%m/%d/%Y %I:%M:%S %p')

        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(console_formatter)
        console_handler.setLevel(loglevel)
        logger.addHandler(console_handler)

        return logger
