import py
import pytest

import jmdwebsites


def datapath(stem):
    return py.path.local(__file__).dirpath('data', stem)


@pytest.mark.parametrize("dir1, dir2", [
    (datapath('test_dircmp/a/both'), datapath('test_dircmp/b/both'))
])
def test_dirs_match(logopt, dir1, dir2):
    assert not jmdwebsites.dircmp.diff(dir1, dir2), \
        'Directories not matching: {} {}'.format(dir1, dir2)


@pytest.mark.parametrize("dir1, dir2", [
    (datapath('test_dircmp/a'), datapath('test_dircmp/b'))
])
def test_dirs_dont_match(logopt, dir1, dir2):
    assert jmdwebsites.dircmp.diff(dir1, dir2), \
        'Incorrect, directories are matching: {} {}'.format(dir1, dir2)
