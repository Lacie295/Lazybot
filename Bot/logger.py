import logging
import os

songs = 'Lazybot.log'
dirname = os.path.dirname(__file__)
filename = os.path.join(dirname, songs)
logging.basicConfig(filename=filename,level=logging.DEBUG)


def debug(msg):
    logging.debug(msg)


def info(msg):
    logging.info(msg)


def warning(msg):
    logging.warning(msg)
