from __future__ import print_function
import filecmp
import os

import py
import pytest

import jmdwebsites
from jmdwebsites import dircmp
from jmdwebsites import Website, HtmlPage


def datapath(stem):
    return py.path.local(__file__).dirpath('data', stem)


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


def test_init_website(tmpcwd, loginfo):
    site_dir = tmpcwd
    project_dir = site_dir.join('.jmdwebsite')
    assert not project_dir.check()
    jmdwebsites.init_website()
    assert project_dir.check()
    assert site_dir.join('site.yaml').check()


def test_new_website(tmpcwd, loginfo):
    site = 'example-site'
    site_dir = py.path.local(site)
    assert not site_dir.check()
    jmdwebsites.new_website(site_dir)
    assert site_dir.check(), \
        'No new site has been created: {}'.format(site_dir)
    #assert site_dir.join('index').check()


@pytest.mark.parametrize("config, expected", [
    (
        { '/': {'blog': {'/first-post': None}, 'contact': None, 'about':{'tmp.html': None }}},
        ['/', '/blog', '/first-post', '/about', '/about/tmp.html', '/contact']
    )
])
def test_spec_walker(config, expected):
    result = [path for path, root, key, value in jmdwebsites.spec.spec_walker(config)]
    assert result == expected


class TestWebsite:
    def test_instantiation_with_no_project_root(self, tmpdir):
        with tmpdir.join('mysite').ensure(dir=1).as_cwd():
            with pytest.raises(jmdwebsites.project.ProjectNotFoundError):
                Website()
    
    def test_instantiation_in_empty_project(self, tmpdir):
        site_dir = tmpdir.join('mysite').ensure(dir=1)
        site_dir.join('.jmdwebsite').ensure(dir=1)
        site_dir.join('build/index.html')
        site_dir.join('build/index.html')
        with site_dir.as_cwd():
            assert Website().build_dir.strpath == os.path.join(os.getcwd(), 'build')
            assert Website(build_dir = 'somewhere').build_dir == py.path.local('somewhere')

    def test_clobber__no_build_dir_to_clobber(self, tmpdir):
        tmpdir.ensure('.jmdwebsite')
        with tmpdir.as_cwd():
            website = Website()
            with pytest.raises(jmdwebsites.error.PathNotFoundError):
                website.clobber()

    def test_clobber(self, tmpdir):
        site_dir = tmpdir.join('mysite').ensure(dir=1)
        site_dir.ensure('.jmdwebsite')
        build_dir = site_dir.join('build')
        build_dir.ensure('index.html')
        build_dir.ensure('contact/index.html')
        with site_dir.as_cwd():
            Website().clobber()
            assert not build_dir.check(), \
                'The build directory has not been removed: {}'.format(build_dir)

    @pytest.mark.parametrize("site_dir", [
        datapath('test_website/test_build'),
        datapath('simple_home_page_and_stylesheet'),
        datapath('brochure')
    ])
    def test_build(self, site_dir, logopt, website):
        expected_dir = site_dir.join('expected')
        website.build()
        assert website.build_dir.check(), \
            'Build directory does not exist.'.format(website.build_dir)
        assert not dircmp.diff(website.build_dir, expected_dir), \
            'Build dir not equal to expected dir'


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
    print('Validate {}'.format(file))
    assert file.ext == expected['ext'], \
        "Incorrect file extension"
    test_html_page(HtmlPage(file), expected['page'])


@pytest.mark.parametrize("input_dir, file_glob, expected", [
    (datapath('simple_home_page_and_stylesheet/expected'), '*.html', expected_html_file),
    (py.path.local('pyapps/tests/data/example_build'), '*.html', expected_html_file)
])
def test_html_files(input_dir, file_glob, expected):
    for html_file in input_dir.visit(fil = str(file_glob)):
        test_html_file(html_file, expected)


@pytest.mark.parametrize("site_dir, expected", [
    (datapath('simple_home_page_and_stylesheet'), expected_html_file)
])
def test_html_files_built(site_dir, website, expected):
    website.build()
    test_html_files(website.build_dir, '*.html', expected)
