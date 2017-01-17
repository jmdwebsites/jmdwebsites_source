import filecmp
import logging
import platform

import py

from jmdwebsites.log import STARTSTR, ENDSTR

logger = logging.getLogger(__name__)


def is_different(dcmp):
    if dcmp.left_only or dcmp.right_only or dcmp.funny_files or dcmp.diff_files:
        return True 
    return False


def dump(dcmp):
    diff_report = [
        ('Identical files : {}', dcmp.same_files),
        ('Common subdirectories : {}', dcmp.common_dirs),
        ('Differing files : {}', dcmp.diff_files + dcmp.funny_files),
        ('Only in {} {{}}:'.format(dcmp.left), dcmp.left_only),
        ('Only in {} {{}}:'.format(dcmp.right), dcmp.right_only),
    ]
    return 'diff {} {}\n{}'.format( 
        dcmp.left,
        dcmp.right,
        '\n'.join(text.format(data) for text, data in diff_report if data))
    

def walker(dcmp):
    for sub_dcmp in dcmp.subdirs.values():
        yield sub_dcmp
        for another_dcmp in walker(sub_dcmp):
            yield another_dcmp


def getter(dir1, dir2, recursive=True, ignore=None, **kargs):
    dir1 = py.path.local(dir1).strpath
    dir2 = py.path.local(dir2).strpath
    if ignore is None:
        if platform.system() == 'Darwin':
            ignore = ['.DS_Store']
    top_dircmp = filecmp.dircmp(dir1, dir2, ignore=ignore, **kargs)
    logger.debug('\n{0}\n{1}\n{2}'.format(
        STARTSTR, dump(top_dircmp), ENDSTR))
    yield top_dircmp
    if recursive:
        for dcmp in walker(top_dircmp):
            logger.debug('\n{0}\n{1}\n{2}'.format(
                STARTSTR, dump(dcmp), ENDSTR))
            yield dcmp


def diff(dir1, dir2, verbose=True, **kargs):
    differences = [dircmp for dircmp in getter(dir1, dir2, **kargs) if is_different(dircmp)]
    if verbose:
        for dircmp in differences:
            dircmp.report()
    return differences
