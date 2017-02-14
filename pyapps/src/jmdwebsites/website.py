from __future__ import print_function
import logging
import os

import py

from . import html
from . import orderedyaml
from .error import JmdwebsitesError, PathNotFoundError
from .orderedyaml import CommentedMap
from .page import get_page_spec, build_page
from .project import protected_remove, get_project_dir, \
                     init_project, new_project, load_specs
from .spec import ensure_spec
from .utils import find_path

logger = logging.getLogger(__name__)

PROJDIR = '.jmdwebsite'
BUILD = 'build'
CONTENT = 'content'
CONTENT_GROUP = 'content_group'
CONFIG_FILE = 'site.yaml'
THEME_FILE = 'theme.yaml'
CONTENT_FILE = 'content.yaml'
PAGE_SPECS_FILE = 'pagespecs.yaml'
HOME = 'home'
PAGES = 'pages'
POSTS = 'posts'

class WebsiteError(JmdwebsitesError): pass
class InvalidContentGroupError(WebsiteError): pass
class BuildStylesheetsError(WebsiteError): pass


def content_finder(site, site_dir):
    site = ensure_spec(site, ())
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
        for page_path in content_dir.visit(fil=lambda path: path.check(dir=1)):
            url = get_url(page_path.relto(content_dir))
            yield url, page_path


def get_url(rel_page_path):
    #TODO: Check site config to get slugs and relpagepath to url mappings.
    url = os.path.join('/', rel_page_path)
    return url


def get_specs(locations):
    site_specs = load_specs(CONFIG_FILE, locations)
    theme_specs = load_specs(THEME_FILE, locations)
    content_specs = load_specs(CONTENT_FILE, locations)
    specs = CommentedMap()
    if isinstance(site_specs, dict):
        specs.update(site_specs)
    if isinstance(theme_specs, dict):
        specs.update(theme_specs)
    if isinstance(content_specs, dict):
        specs.update(content_specs)
    return specs


def get_theme_dir(site_specs, site_dir, locations):
    try:
        theme_name = site_specs['theme']['name']
    except:
        logger.warning('%s: Theme not specified, use fallback', 
                       CONFIG_FILE)
        theme_file = find_path(THEME_FILE, locations=locations)
        theme_dir = theme_file.dirpath()
    else:
        theme_dir = site_dir.join('themes', theme_name)
    logger.debug('Theme dir: %s', theme_dir)
    return theme_dir 


def init_website():
    """Initialize website.
    """
    init_project(PROJDIR)
    site_dir = py.path.local()
    site_dir.ensure(CONFIG_FILE, file=1)


def new_website(site_pathname):
    """New website.
    """
    new_project(site_pathname)


class Website(object):

    def __init__(self, site_dir=None, build_dir=None):
        logger.debug('Create website: %s(site_dir=%r, build_dir=%r)',
            self.__class__.__name__, site_dir, build_dir)
        if site_dir is None:
            self.site_dir = get_project_dir(PROJDIR)
        else:
            self.site_dir = py.path.local(site_dir)
        logger.info('Site root directory: %s', self.site_dir)
        if build_dir is None:
            self.build_dir = self.site_dir.join(BUILD)
        else:
            self.build_dir = py.path.local(build_dir)
        logger.info('Build website in %s', self.build_dir)
        self.locations = [
            self.site_dir,  
            py.path.local(__file__).dirpath()
        ]
        self.specs = get_specs(self.locations)
        self.theme_dir  = get_theme_dir(self.specs, self.site_dir, self.locations)

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
        self.build_pages()
        self.build_stylesheets()

    def build_pages(self):
        for content_group, source_dir in content_finder(self.specs, self.site_dir):
            for url, page_dir in page_finder(content_group, source_dir):
                build_page(url, self.specs, page_dir, self.build_dir)

    def build_stylesheets(self):
        logger.info('Build stylesheets')
        src = self.theme_dir.join('stylesheets/page.scss')
        if py.path.local(src).check(file=1):
            tgt = self.build_dir.join('page.css')
            sass_cmdline = "sass {0} {1}".format(src, tgt)
            error_code = os.system(sass_cmdline)
            if error_code:
                raise BuildStylesheetsError
