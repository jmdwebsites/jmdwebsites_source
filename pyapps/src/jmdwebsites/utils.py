import logging
import os
import py

from .error import PathNotFoundError

logger = logging.getLogger(__name__)

DEFAULT_LOCATIONS = [
    os.getcwd(),
    py.path.local(__file__).dirpath()]


def find_path(basename, locations=DEFAULT_LOCATIONS):
    for dirpath in locations:
        filepath = dirpath.join(basename)
        if filepath.check():
            return filepath
    logger.warning('Not found: %s', basename)
    #raise PathNotFoundError
    return None


def find_root(basename, locations=DEFAULT_LOCATIONS):
    for dirpath in locations:
        filepath = dirpath.join(basename)
        if filepath.check():
            return dirpath
    logger.warning('Not found: %s', basename)
    raise PathNotFoundError


