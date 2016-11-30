import pytest
import os
import py
from jmdwebsites.website import Website
import logging
import filecmp
import six

logger = logging.getLogger(__name__)

def test_instantiation_of_Website(setup_test_session, setup_test, tmpdir):
    assert Website().build_dir.strpath == os.path.join(os.getcwd(), 'build')
    assert Website(build_dir = tmpdir).build_dir == tmpdir

def test_clobber(setup_test_session, setup_test, tmpdir):
    with tmpdir.as_cwd():
        # Create a website build including at least some dirs
        website = Website(build_dir = tmpdir)
        website.build_dir.ensure('index.html')
        website.build_dir.ensure('contact/index.html')
        # Now clobber it
        website.clobber()
        # and the build dir should be gone
        assert website.build_dir.check() == False, 'The build directory has not been removed: {}'.format(website.build_dir)

@pytest.mark.parametrize("test_data", [
    'test_website/test_build',
    'simple_home_page_and_stylesheet'
])
def test_build(setup_test_session, setup_test, test_data, tmpdir):
    if isinstance(test_data, six.string_types):
        site_dir = py.path.local(__file__).dirpath('data', test_data)
        src_dir = site_dir.join('src')
        expected_dir = site_dir.join('expected')
        build_dir = tmpdir
    else:
        build_dir = tmpdir

    with site_dir.as_cwd():
        logger.info("Change working directory to {}".format(os.getcwd()))

        website = Website(build_dir = tmpdir)
        #assert website.build_dir.check() == False, 'Build directory already exists.'.format(website.build_dir)
        website.build()
        assert website.build_dir.check(), 'Build directory does not exist.'.format(website.build_dir)

        # Visit all files in built website and check they match the expected files
        for built in build_dir.visit():
            assert built.check(), 'File not found: {}'.format(built)
            expected = expected_dir.join(built.basename)
            assert filecmp.cmp(built.strpath, expected.strpath), 'Page not as expected: {}'.format(built)
