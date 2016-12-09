import pytest
import os
import py
from jmdwebsites import Website, HtmlPage
import filecmp
import six


def datapath(stem):
    return py.path.local(__file__).dirpath('data', stem)


def test_instantiation_of_Website(tmpdir):
    assert Website().build_dir.strpath == os.path.join(os.getcwd(), 'build')
    assert Website(build_dir = tmpdir).build_dir == tmpdir

def test_clobber(tmpdir):
    with tmpdir.as_cwd():
        # Create a website build including at least some dirs
        website = Website(build_dir = tmpdir)
        website.build_dir.ensure('index.html')
        website.build_dir.ensure('contact/index.html')
        # Now clobber it
        website.clobber()
        # and the build dir should be gone
        assert website.build_dir.check() == False, 'The build directory has not been removed: {}'.format(website.build_dir)

@pytest.mark.parametrize("site_dir", [
    datapath('test_website/test_build'),
    datapath('simple_home_page_and_stylesheet')
])
def test_build(site_dir, tmpdir):
    src_dir = site_dir.join('src')
    expected_dir = site_dir.join('expected')
    build_dir = tmpdir

    with site_dir.as_cwd():
        print("Changed working directory to {}".format(os.getcwd()))

        website = Website(build_dir = tmpdir)
        website.build()
        assert website.build_dir.check(), \
            'Build directory does not exist.'.format(website.build_dir)

        # Visit all files in built website and check they match the expected files
        for built in build_dir.visit():
            print('Check {}'.format(built))
            assert built.check(), \
                'File not found: {}'.format(built)
            expected = expected_dir.join(built.basename)
            assert filecmp.cmp(built.strpath, expected.strpath), \
                'Page not as expected: {}'.format(built)


@pytest.mark.parametrize("file", [
    datapath('data/simple_home_page_and_stylesheet/expected')
])
def tst_html_page(file):
    assert 0

expected_html_data = {
    'ext': '.html',
    'doctype': 'html'
}
@pytest.mark.parametrize("input_dir, file_glob, expected", [
    (datapath('simple_home_page_and_stylesheet/expected'), '*.html', expected_html_data),
    (py.path.local('site/build'), '*.html', expected_html_data)
])
def test_html_files(input_dir, file_glob, expected):
    for html_file in input_dir.visit(fil = file_glob):
        print('Check {}'.format(html_file))
        assert html_file.ext == expected['ext'], \
            "Incorrect file extension"
        #html_page = HtmlPage(html_file.read())
        html_page = HtmlPage(html_file)
        assert html_page.doctype() == expected['doctype'], \
            'Incorrect doctype'

@pytest.mark.parametrize("site_dir, expected", [
    (datapath('simple_home_page_and_stylesheet'), expected_html_data)
])
def test_html_files_built(site_dir, expected, tmpdir):
    with site_dir.as_cwd():
        print("Changed working directory to {}".format(os.getcwd()))
        website = Website(build_dir = tmpdir)
        website.build()
        test_html_files(website.build_dir, '*.html', expected)
        