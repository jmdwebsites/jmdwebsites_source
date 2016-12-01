import pytest
import os
import py
from jmdwebsites.website import Website
import logging
import filecmp
import six
import bs4

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
        website.build()
        assert website.build_dir.check(), 'Build directory does not exist.'.format(website.build_dir)

        # Visit all files in built website and check they match the expected files
        for built in build_dir.visit():
            assert built.check(), 'File not found: {}'.format(built)
            expected = expected_dir.join(built.basename)
            assert filecmp.cmp(built.strpath, expected.strpath), 'Page not as expected: {}'.format(built)

expected = {
    'doctype': 'html'
}
@pytest.mark.parametrize("test_data", [
    ('simple_home_page_and_stylesheet', '*.html', expected)
])
def test_html_files(setup_test_session, setup_test, test_data, tmpdir):
    site_dirname, file_glob, expected = test_data 
    site_dir = py.path.local(__file__).dirpath('data', site_dirname)
    with site_dir.as_cwd():
        website = Website(build_dir = tmpdir)
        website.build()
        for html_file in website.build_dir.visit(fil = file_glob):
            logger.info('Checking {}'.format(html_file))
            assert html_file.ext == '.html', "Incorrect file extension: {}".format(html_file.ext)
            soup = bs4.BeautifulSoup(html_file.read(), 'html5lib')

            # doctype:
            #   There should be just one doctype, 
            #   and it should be the first item in the soup contents
            doctypes = [t for t in soup.contents if isinstance(t, bs4.Doctype)]
            doctype_count = len(doctypes)
            assert doctype_count > 0, 'Doctype not defined: {}'.format(built)
            assert doctype_count <= 1, 'Too many doctype tags: {} {}'.format(doctype_count, built)
            doctype = soup.contents[0]
            assert isinstance(doctype, bs4.Doctype), 'First element is not doctype: {} {}'.format(doctype, built)
            assert doctype == expected['doctype'], "Doctype should be {} not {}: {}".format(expected['doctype'], doctype, built) 

