from __future__ import print_function
from subprocess import Popen, PIPE

import pytest


@pytest.mark.parametrize("cmd", [
    'clean',
    'clobber',
    'build',
])
def test_projdir_not_detected(tmpdir, cmd):
    with tmpdir.as_cwd():
        p = Popen(['jmdwebsites', cmd], stdout=PIPE, stderr=PIPE)
        out, err = p.communicate()
        #print("returncode: {}\nstdout: {}\nstderr: {}".format(p.returncode, repr(out), repr(err)))
        assert p.returncode == 1
        assert out == ''
        assert err == 'Not a website project (or any parent directories): .jmdwebsite not found\n'


class TestClobber:
    def test_clobber__no_build_dir_to_clobber(self, tmpdir, capsys):
        tmpdir.ensure('.jmdwebsite')
        with tmpdir.as_cwd():
            p = Popen(['jmdwebsites', 'clobber'], stdout=PIPE, stderr=PIPE)
            out, err = p.communicate()
            print("returncode: {}\nstdout: {}\nstderr: {}".format(p.returncode, repr(out), repr(err)))
            assert p.returncode == 1
            assert out == ''
            assert err == 'clobber: No such build dir: {}\n'.format(tmpdir.join('build'))

