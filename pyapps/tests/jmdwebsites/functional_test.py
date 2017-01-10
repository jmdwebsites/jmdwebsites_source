from __future__ import print_function
import pytest
import jmdwebsites
from subprocess import Popen, PIPE
import py
import filecmp

def datapath(stem):
    return py.path.local(__file__).dirpath('data', stem)

def filt(f):
    if f.ext in ['.DS_Store']:
        return False
    return True

@pytest.mark.parametrize("theme, content, expected", [
    ('','',datapath('brochure/expected'))
])
def tst_init_then_build(tmpcwd, loginfo, theme, content, expected):
    site_dir = tmpcwd
    build_dir = site_dir.join('build')

    #p = Popen(['jmdwebsites new build'], stdout=PIPE, stderr=PIPE, shell=True)
    p = Popen(['jmdwebsites --debug -v init'], stdout=PIPE, stderr=PIPE, shell=True)
    out, err = p.communicate()
    print('{}{}'.format(out, err), end='')
    assert not err
    for f in site_dir.visit(rec=1):
        print('TST: ', f.strpath)

    p = Popen(['jmdwebsites --info -v build'], stdout=PIPE, stderr=PIPE, shell=True)
    out, err = p.communicate()
    print('{}{}'.format(out, err), end='')
    assert not err
    for f in site_dir.visit(rec=1):
        print('TST: ', f.strpath)

    assert build_dir.check()
    # Visit all files in built website and check they match the expected files
    #for built_path in build_dir.visit():
    #    assert built_path.check(), 'Not found: {}'.format(built_path)
    #    expected_path = expected.join(built_path.relto(build_dir))        
    #    assert expected_path.check(), 'Not found: {}'.format(expected_path)
    #    if built_path.check(file=1):
    #        print('Compare {}'.format(built_path))
    #        assert filecmp.cmp(built_path.strpath, expected_path.strpath), \
    #            'Page not as expected: {}'.format(built_path)
    
    # Visit all files in expected website and check they match the buit files
    for expected_path in expected.visit(fil=filt):
        built_path = build_dir.join(expected_path.relto(expected))        
        print('Check {}'.format(built_path))
        assert built_path.check(), 'Not found: {}'.format(built_path)
        if built_path.check(file=1):
            print('Compare {}'.format(built_path))
            assert filecmp.cmp(built_path.strpath, expected_path.strpath), \
                'Page not as expected: {}'.format(built_path)

