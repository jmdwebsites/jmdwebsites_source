import py
import filecmp
import platform

def is_different(dcmp):
    if dcmp.left_only or dcmp.right_only or dcmp.funny_files or dcmp.diff_files:
        return True 
    return False

def walker(dcmp):
    #yield dcmp
    for sub_dcmp in dcmp.subdirs.values():
        for another_dcmp in walker(sub_dcmp):
            yield another_dcmp

def getter(dir1, dir2, recursive=True, ignore=None, **kargs):
    dir1 = py.path.local(dir1).strpath
    dir2 = py.path.local(dir2).strpath
    if ignore is None:
        if platform.system() == 'Darwin':
            ignore = ['.DS_Store']
    top_dircmp = filecmp.dircmp(dir1, dir2, ignore=ignore, **kargs)
    yield top_dircmp
    if recursive:
        for dcmp in walker(top_dircmp):
            yield dcmp

def diff(dir1, dir2, verbose=True, **kargs):
    differences = [dircmp for dircmp in getter(dir1, dir2, **kargs) if is_different(dircmp)]
    if verbose:
        for dircmp in differences:
            dircmp.report()
    return differences
