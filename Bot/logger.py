import logging
import os

songs = 'Lazybot.log'
dirname = os.path.dirname(__file__)
filename = os.path.join(dirname, songs)
logging.basicConfig(filename=filename, filemode='w', level=logging.INFO)


def debug(msg):
    logging.debug(msg)
    print("DEBUG: {}".format(msg))


def info(msg):
    logging.info(msg)
    print("INFO: {}".format(msg))


def warning(msg):
    logging.warning(msg)
    print("WARN: {}".format(msg))
