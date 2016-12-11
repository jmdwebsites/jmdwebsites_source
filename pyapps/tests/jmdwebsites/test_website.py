import pytest
import os
import py
from jmdwebsites import Website, HtmlPage
import filecmp
import six


def datapath(stem):
    return py.path.local(__file__).dirpath('data', stem)

def test_instantiation_of_Website():
    assert Website().build_dir.strpath == os.path.join(os.getcwd(), 'build')
    assert Website(build_dir = 'somewhereelse').build_dir == py.path.local('somewhereelse')

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
def test_build(site_dir, website):
    expected_dir = site_dir.join('expected')
    website.build()
    assert website.build_dir.check(), \
        'Build directory does not exist.'.format(website.build_dir)
    # Visit all files in built website and check they match the expected files
    for built in website.build_dir.visit():
        print('Check {}'.format(built))
        assert built.check(), \
            'File not found: {}'.format(built)
        expected = expected_dir.join(built.basename)
        assert filecmp.cmp(built.strpath, expected.strpath), \
            'Page not as expected: {}'.format(built)

expected_html_page = {
    'doctype': 'html',
    'charset': 'utf-8'
}

@pytest.mark.parametrize("page, expected", [
    (HtmlPage(datapath('simple_home_page_and_stylesheet/expected/index.html')), expected_html_page)
])
def test_html_page(page, expected):
    assert page.doctype() == expected['doctype'], \
        'Incorrect doctype'
    assert page.charset() == expected['charset'], \
        'Incorrect charset'

expected_html_file = {
    'ext': '.html',
    'page': expected_html_page,
}

@pytest.mark.parametrize("file, expected", [
    (datapath('simple_home_page_and_stylesheet/expected/index.html'), expected_html_file)
])
def test_html_file(file, expected):
    print('Check {}'.format(file))
    assert file.ext == expected['ext'], \
        "Incorrect file extension"
    test_html_page(HtmlPage(file), expected['page'])

@pytest.mark.parametrize("input_dir, file_glob, expected", [
    (datapath('simple_home_page_and_stylesheet/expected'), '*.html', expected_html_file),
    (py.path.local('build'), '*.html', expected_html_file)
])
def test_html_files(input_dir, file_glob, expected):
    for html_file in input_dir.visit(fil = file_glob):
        test_html_file(html_file, expected)

@pytest.mark.parametrize("site_dir, expected", [
    (datapath('simple_home_page_and_stylesheet'), expected_html_file)
])
def test_html_files_built(site_dir, website, expected):
    website.build()
    test_html_files(website.build_dir, '*.html', expected)
