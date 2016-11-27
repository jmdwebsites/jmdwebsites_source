import os
import py
from jmdwebsites.website import Website
import logging
import filecmp

logger = logging.getLogger(__name__)

def test_instantiation_of_Website(setup_test_session, setup_test, tmpdir):
    site_dir = py.path.local(__file__).dirpath('data/test_website/test_build')
    with site_dir.as_cwd():
        logger.info("Change working directory to {}".format(os.getcwd()))
        # Use the default build directory
        assert Website().build_dir == site_dir.join('build')

        # Specify the build directory
        build_dir = os.path.join(os.getcwd(), 'build')
        assert Website(build_dir).build_dir == build_dir


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
