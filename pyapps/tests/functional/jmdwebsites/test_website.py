#import pytest
import os
import py
import sys
from jmdwebsites.website import Website
import logging
import shutil

logger = logging.getLogger(__name__)

def test_instantiation_of_Website(setup_test_session, setup_test, tmpdir):
    root_dir = py.path.local(__file__).dirpath('data/test_website/test_build')
    with root_dir.as_cwd():
        logger.info("Change working directory to {}".format(os.getcwd()))
        # Use the default build directory
        assert Website().build_dir == root_dir.join('build')

        # Specify the build directory
        build_dir = os.path.join(os.getcwd(), 'build')
        assert Website(build_dir).build_dir == build_dir


        # Specify the build directory
        build_dir = tmpdir.join('build')
        assert Website(build_dir).build_dir == build_dir
