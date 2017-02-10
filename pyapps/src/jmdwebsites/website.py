from __future__ import print_function

import logging
import os

import py

from jmdwebsites import html, orderedyaml
from jmdwebsites.page import get_html
from jmdwebsites.spec import ensure_spec, get_page_spec
from jmdwebsites.error import JmdwebsitesError

logger = logging.getLogger(__name__)

BUILD = 'build'
CONTENT = 'content'
CONTENT_GROUP = 'content_group'
CONFIG_FILE = 'site.yaml'
THEME_FILE = 'theme.yaml'
PAGE_SPECS_FILE = 'pagespecs.yaml'
PROJDIR = '.jmdwebsite'
HOME = 'home'
PAGES = 'pages'
POSTS = 'posts'
DEBUG_SEPARATOR = '%%' * 60 + ' %s ' + '%%' * 60

class FatalError(JmdwebsitesError): pass
class NonFatalError(JmdwebsitesError): pass

class WebsiteError(JmdwebsitesError): pass
# For get_project_dir()
class ProjectNotFoundError(WebsiteError): pass
# For protected_remove()
class ProtectedRemoveError(WebsiteError): pass
class PathNotAllowedError(ProtectedRemoveError): pass
class BasenameNotAllowedError(ProtectedRemoveError): pass
class PathNotFoundError(WebsiteError): pass
class PathAlreadyExists(WebsiteError): pass
class WebsiteProjectAlreadyExists(WebsiteError): pass
class InvalidContentGroupError(WebsiteError): pass
class BuildStylesheetsError(WebsiteError): pass


def isdir(path): 
    return path.check(dir=1)


def get_project_dir(config_basename =  PROJDIR):
    # Check for project file in this dir and ancestor dirs
    for dirpath in py.path.local().parts(reverse=True):
        for path in dirpath.listdir():
            if path.basename == config_basename:
                return path.dirpath()
    raise ProjectNotFoundError(
        'Not a website project (or any parent directories): {} not found'.format(
            config_basename))

 
def protected_remove(path, valid_basenames=None):
    if valid_basenames is None:
        valid_basenames = set([BUILD])
    for disallowed in [os.getcwd(), __file__]:
        if path in py.path.local(disallowed).parts():
            raise PathNotAllowedError(
                'Remove: {}: Path not allowed, protecting: {}'.format(
                    path, 
                    disallowed))
    if valid_basenames and path.basename not in valid_basenames:
        raise BasenameNotAllowedError(
            'Remove: {}: Basename not allowed: {}: Must be one of: {}'.format(
                path, 
                path.basename, 
                valid_basenames))
    try:
        #Check that file/dir is a child of a dir containing a .jmdwebsites file, 
        # thus indicating it is part of a website project.
        get_project_dir()
    except ProjectNotFoundError as e:
        raise ProjectNotFoundError('Remove: {}'.format(e))
    if not path.check():
        raise PathNotFoundError(
            'Remove: Path not found: {}'.format(path))
    logger.info('Remove %s', path)
    path.remove()


def new_website(site_dirname = ''):
    """New website."""
    site_dir = py.path.local(site_dirname)
    logger.info('Create new website %s', site_dir.strpath)
    if site_dir.check():
        raise PathAlreadyExists(
            'Already exists: {}'.format(site_dir))
    site_dir.ensure( PROJDIR)
    logger.error('TODO:')


def init_website():
    """Initialize website."""
    site_dir = py.path.local()
    logger.info('Init website %s', site_dir.strpath)
    project_dir = py.path.local( PROJDIR)
    if project_dir.check():
        raise WebsiteProjectAlreadyExists(
            'Website project already exists: {}'.format(project_dir))
    logger.info('Create proj dir %s', project_dir.strpath)
    project_dir.ensure(dir=1)
    site_dir.ensure(CONFIG_FILE)


def content_finder(site, site_dir):
    site = ensure_spec(site, [])
    if CONTENT_GROUP in site:
        for content_group, dirname in site[CONTENT_GROUP].items():
            if content_group not in set([HOME, PAGES, POSTS]):
                raise InvalidContentGroupError(
                    'Invalid content group: {}'.format(content_group))
            if dirname is None:
                group_dir = site_dir.join(CONTENT, content_group)
            else:
                group_dir = site_dir.join(dirname)
            yield content_group, group_dir
    else:
        root, dirs, files = next(os.walk(site_dir.join(CONTENT).strpath))
        for content_group in dirs: 
            group_dir = site_dir.join(CONTENT, content_group)
            yield content_group, group_dir


def page_finder(content_group, content_dir):
    logger.info('Build content: %s: %s', content_group, content_dir)
    if content_group == HOME:
        url = '/'
        yield url, content_dir 
    else:
        for page_path in content_dir.visit(fil=isdir):
            url = get_url(page_path.relto(content_dir))
            yield url, page_path


def get_url(rel_page_path):
    #TODO: Check site config to get slugs and relpagepath to url mappings.
    url = os.path.join('/', rel_page_path)
    return url


class PageData():
    def __init__(self):
        # Use this as test data to check mechanism 
        # for passing in data to template/content works
        self.stats = 'Stats=56%'


def build_page_assets(source_dir, target_dir):
    for asset in source_dir.visit(fil=str('*.css')):
        logger.info('Get asset %s from %s',
            target_dir.relto(target_dir).join(asset.basename), 
            asset)
        asset.copy(target_dir)


class Website(object):
    def __init__(self, site_dir=None, build_dir=None):
        logger.debug('Create website: %s(site_dir=%r, build_dir=%r)',
            self.__class__.__name__, site_dir, build_dir)
        if site_dir is None:
            self.site_dir = get_project_dir()
        else:
            self.site_dir = py.path.local(site_dir)
        logger.info('Site root directory: %s', self.site_dir)
        if build_dir is None:
            self.build_dir = self.site_dir.join(BUILD)
        else:
            self.build_dir = py.path.local(build_dir)
        logger.info('Build website in %s', self.build_dir)
        self.site = self.get_specs(CONFIG_FILE)
        self.theme_dir, self.theme = self.get_theme()

    def get_fallback(self, basename):
        locations = [
            self.site_dir,  
            py.path.local(__file__).dirpath()
        ]
        for dirpath in locations:
            filepath = dirpath.join(basename)
            if filepath.check():
                break
        else:
            raise PathNotFoundError()
        return dirpath, filepath

    def get_theme(self):
        try:
            theme_name = self.site['theme']['name']
        except:
            logger.warning('%s: Theme not specified, use fallback', CONFIG_FILE)
            theme_dir, theme_file = self.get_fallback(THEME_FILE)
            logger.debug('Load theme from %s', theme_file)
        else:
            theme_dir = self.site_dir.join('themes', theme_name)
            theme_file = theme_dir.join(THEME_FILE)
            logger.debug('Load theme %r from %s', theme_name, theme_file)
        theme = orderedyaml.load(theme_file).commented_map

        return theme_dir, theme

    def clean(self):
        """Clean up the build."""
        logger.info(self.clean.__doc__)
        raise WebsiteError(
            'TODO: Write code clean the website build')

    def clobber(self):
        """Clobber the build removing everything."""
        logger.info(self.clobber.__doc__)
        #if self.build_dir.check():
        #    protected_remove(self.build_dir)
        #else:
        #    print('clobber: No such build dir: {}'.format(self.build_dir))
        protected_remove(self.build_dir)

    def build(self):
        """Build the website."""
        #TODO: Write code to update files only if they have changed.
        #      But until then, clobber the build first, 
        #      and then build everything from new.
        if self.build_dir.check():
            protected_remove(self.build_dir)
        assert self.build_dir.check() == False, \
            'Build directory already exists.'.format(self.build_dir)
        self.build_dir.ensure(dir=1)

        for content_group, source_dir in content_finder(self.site, self.site_dir):
            for url, path in page_finder(content_group, source_dir):
                self.build_page(url, path)

        self.build_stylesheets()

    def get_specs(self, basename):
        locations = [
            self.site_dir,  
            py.path.local(__file__).dirpath()
        ]
        for dirpath in locations:
            filepath = dirpath.join(basename)
            if filepath.check(file=1):
                data = orderedyaml.load(filepath).commented_map
                break
        else:
            logger.warning('Not found: %s', basename)
            data = None
        return data

    def build_page(self, url, source_dir):
        logger.debug(DEBUG_SEPARATOR, url)  # Mark page top
        logger.info("Build page: %s", url)
        page_spec = get_page_spec(url, self.site, self.theme)
        html_page = get_html(source_dir, page_spec, data=PageData())
        target_dir = self.build_dir.join(url)
        html.dump(html_page, target_dir)
        build_page_assets(source_dir, target_dir)

    def build_stylesheets(self):
        logger.info('Build stylesheets')
        src = self.theme_dir.join('stylesheets/page.scss')
        if py.path.local(src).check(file=1):
            tgt = self.build_dir.join('page.css')
            sass_cmdline = "sass {0} {1}".format(src, tgt)
            error_code = os.system(sass_cmdline)
            if error_code:
                raise BuildStylesheetsError
