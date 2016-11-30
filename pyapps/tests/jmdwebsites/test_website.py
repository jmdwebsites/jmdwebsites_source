import os
import py
from jmdwebsites.website import Website
import logging
import filecmp

logger = logging.getLogger(__name__)

def test_instantiation_of_Website(setup_test_session, setup_test, tmpdir):
    # Use the default build directory
    expected_build_dirname = os.path.join(os.getcwd(), 'build')
    assert Website().build_dir.strpath == expected_build_dirname
    # Specify the build directory
    build_dir = tmpdir.join('build')
    assert Website(build_dir).build_dir == build_dir

def test_clobber(setup_test_session, setup_test, tmpdir):
    with tmpdir.as_cwd():
        build_dir = tmpdir.join('build')
        website = Website(build_dir)
        assert website.build_dir == build_dir
        #Create the build dir and put a web file tree in it
        website.build_dir.ensure('index.html')
        website.build_dir.ensure('contact/index.html')
        website.clobber()
        #The build dir should now be gone
        assert website.build_dir.check() == False, 'The build directory has not been removed: {}'.format(website.build_dir)

def test_build(setup_test_session, setup_test, tmpdir):
    site_dir = py.path.local(__file__).dirpath('data/test_website/test_build')
    with site_dir.as_cwd():
        logger.info("Change working directory to {}".format(os.getcwd()))
        build_dir = tmpdir.join('build')
        website = Website(build_dir)
        assert website.build_dir == build_dir
        assert website.build_dir.check() == False, 'Build directory already exists.'.format(website.build_dir)
        website.build()
        assert website.build_dir.check(), 'Build directory does not exist.'.format(website.build_dir)

        home_page = build_dir.join('index.html')
        assert home_page.check(), 'Home page not found: {}'.format(home_page)

        expected_dir = py.path.local('expected')
        expected_home_page = expected_dir.join('index.html')
        assert filecmp.cmp(str(home_page), str(expected_home_page)), 'Home page not as expected.'

def assert_file_as_expected(website, filename):
    expected = py.path.local('expected').join(filename)
    built = website.build_dir.join(filename)
    assert built.check(), 'File not found: {}'.format(built)
    assert filecmp.cmp(built.strpath, expected.strpath), 'Page not as expected: built'

def test_build_home_page_and_stylesheet(setup_test_session, setup_test, tmpdir):
    site_dir = py.path.local(__file__).dirpath('data/simple_home_page_and_stylesheet')
    with site_dir.as_cwd():
        logger.info("Change working directory to {}".format(os.getcwd()))
        website = Website(build_dir = tmpdir)
        website.build()
        assert_file_as_expected(website, 'index.html')
        assert_file_as_expected(website, 'page.css')
        #TODO: Turn assert_file_as_expected into a test, that has a parametrized list of input data
        #      Or do a directory comparison, and then focus on more detailed tests
