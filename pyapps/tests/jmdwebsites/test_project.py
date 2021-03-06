from __future__ import print_function

import pytest

import jmdwebsites


def test_load_specs(tmpdir):
    SPEC_FILE = 'site.yaml'
    #TODO# jmdwebsites.project.load_specs(SPEC_FILE)
    

def test_init_project(tmpdir):
    import os
    import py
    with tmpdir.as_cwd():
        PROJ = '.jmdwebsite'
        jmdwebsites.project.init_project(PROJ)
        assert os.listdir('.') == [PROJ]
        assert py.path.local(PROJ).check(dir=1)


def test_protected_remove(tmpdir):
    site_dir = tmpdir
    build_dir = site_dir.join('build')
    path = build_dir.join('readme.txt').ensure()

    with site_dir.as_cwd():
        # Check we're in a jmdwebsite project tree
        with pytest.raises(jmdwebsites.project.ProjectNotFoundError) as e:
            jmdwebsites.website.protected_remove(build_dir, projectdir=jmdwebsites.website.PROJDIR)
        assert str(e.value) == 'Remove: Not a project (or any parent directories): .jmdwebsite not found'
        site_dir.ensure('.jmdwebsite', dir=1)
        # Check we cant remove the path if we're in a subdir of that directory
        with build_dir.as_cwd():
            with pytest.raises(jmdwebsites.project.PathNotAllowedError) as e:
                jmdwebsites.website.protected_remove(build_dir)
        # Check that only a build dir can be removed
        with pytest.raises(jmdwebsites.project.BasenameNotAllowedError) as e:
            jmdwebsites.website.protected_remove(path)

        # Check the build dir to be removed actually exists
        assert path.check()
        # Check the file is removed successfully
        jmdwebsites.website.protected_remove(build_dir)
        assert not path.check()


