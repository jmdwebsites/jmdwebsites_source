import os
import py

from .error import PathNotFoundError

DEFAULT_LOCATIONS = [
    os.getcwd(),
    py.path.local(__file__).dirpath()]


def find_path(basename, locations=DEFAULT_LOCATIONS):
    for dirpath in locations:
        filepath = dirpath.join(basename)
        if filepath.check():
            return filepath
    logger.warning('Not found: %s', basename)
    raise PathNotFoundError


def find_root(basename, locations=DEFAULT_LOCATIONS):
    for dirpath in locations:
        filepath = dirpath.join(basename)
        if filepath.check():
            return dirpath
    logger.warning('Not found: %s', basename)
    raise PathNotFoundError


