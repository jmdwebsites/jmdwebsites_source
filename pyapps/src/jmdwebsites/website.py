import logging
import py
import six
import os
import yaml


logger = logging.getLogger(__name__)

BUILD = 'build'
CONTENT = 'content'
CONFIG_FILE = 'site.yaml'
PROJDIR = '.jmdwebsite'
PAGES = 'pages'
POSTS = 'posts'
HOME = 'home'

# Exceptions
#
class FatalError(Exception): pass
class NonFatalError(Exception): pass
class WebsiteError(Exception): pass
# For get_project_dir()
class ProjectNotFoundError(WebsiteError): pass
# For protected_remove()
class ProtectedRemoveError(WebsiteError): pass
class PathNotAllowedError(ProtectedRemoveError): pass
class BasenameNotAllowedError(ProtectedRemoveError): pass
class PathNotFoundError(ProtectedRemoveError): pass
class PathAlreadyExists(WebsiteError): pass
class WebsiteProjectAlreadyExists(WebsiteError): pass
class SourceDirNotFoundError(WebsiteError): pass


def get_project_dir(config_basename =  PROJDIR):
    # Check for project file in this dir and ancestor dirs
    for dirpath in py.path.local().parts(reverse=True):
        for path in dirpath.listdir():
            if path.basename == config_basename:
                return path.dirpath()
    raise ProjectNotFoundError, \
        'Not a website project (or any of the parent directories): {} not found'.format(config_basename)
 
def protected_remove(path, valid_basenames=None):
    if valid_basenames  is None:
        valid_basenames = [BUILD]
    logger.info('Remove {}'.format(path))
    for disallowed in [os.getcwd(), __file__]:
        if path in py.path.local(disallowed).parts():
            raise PathNotAllowedError, 'remove: {}: Path not allowed, protecting: {}'.format(path, disallowed)
    if valid_basenames and path.basename not in valid_basenames:
        raise BasenameNotAllowedError, 'remove: {}: Basename not allowed: {}: Must be one of: {}'.format(path, path.basename, valid_basenames)
    
    #Check that file/dir is a child of a dir containing a .jmdwebsites file, 
    # thus indicating it is part of a website project.
    get_project_dir()
    
    if not path.check():
        raise PathNotFoundError, 'protected_remove: Path not found: {}'.format(path)
    path.remove()

class ExtMatcher:
    def __init__(self, extensions=None):
        if extensions is None:
            extensions = []
        if isinstance(extensions, six.string_types):
            extensions = extensions.split()
        self.extensions = extensions

    def __call__(self, path):
        return path.ext in self.extensions

def dict_walker(parent, parent_path=''):
    if isinstance(parent, dict):
        for child_name, child in parent.items():
            child_path = os.path.join(parent_path, child_name)
            yield child_path, child
            for path, value in dict_walker(child, parent_path = child_path):
                yield path, value

brochure = '''
/:
  blog/:
    first-post/:
  contact:
  about:
    tmp.html:
'''

def new_website(site_dirname = ''):
    """New website."""
    site_dir = py.path.local(site_dirname)
    logger.info('Create new website {}'.format(site_dir.strpath))
    if site_dir.check():
        raise PathAlreadyExists, \
            'Already exists: {}'.format(site_dir)
    site_dir.ensure( PROJDIR)
    logger.error('TODO:')
    #for url in urls(yaml.load(brochure)):
    #    logger.info(url)

def init_website():
    """Initialize website."""
    site_dir = py.path.local()
    logger.info('Init website {}'.format(site_dir.strpath))
    project_dir = py.path.local( PROJDIR)
    if project_dir.check():
        raise WebsiteProjectAlreadyExists, \
            'Website project already exists: {}'.format(project_dir)
    logger.info('Create proj dir {}'.format(project_dir.strpath))
    project_dir.ensure(dir=1)
    site_dir.ensure(CONFIG_FILE)


class Website(object):
    
    def __init__(self, site_dir=None, build_dir=None):
        logger.debug('Instantiate: {}({})'.format(self.__class__.__name__, repr(build_dir)))
        if site_dir is None:
            self.site_dir = get_project_dir()
        else:
            self.site_dir = py.path.local(site_dir)
        if build_dir is None:
            self.build_dir = self.site_dir.join(BUILD)
        else:
            self.build_dir = py.path.local(build_dir)
        #self.content_dir = self.site_dir.join(CONTENT)
        logger.info('Website root: {}'.format(self.site_dir))

    def clean(self):
        """Clean up the build."""
        logger.info(self.clean.__doc__)
        raise WebsiteError, 'TODO: Write code clean the website build'

    def clobber(self):
        """Clobber the build removing everything."""
        logger.info(self.clobber.__doc__)
        #if self.build_dir.check():
        #    protected_remove(self.build_dir)
        #else:
        #    print('clobber: No such build dir: {}'.format(self.build_dir))
        protected_remove(self.build_dir)

    def get_site_design(self):
        #TODO: If a site.yaml exisits in .jmdwebsites, use it otherwise use the default base theme
        config_file = self.site_dir.join(CONFIG_FILE)
        if config_file.check():
            logger.info('Site config file: {}'.format(config_file))
            with self.site_dir.join(CONFIG_FILE).open() as f:
                config = yaml.load(f)
        else:
            if 0:
                #TODO: Change this to theme.yaml and use as a default theme
                theme_dir = py.path.local(__file__).dirpath('themes','base')
                with theme_dir.join(CONFIG_FILE).open() as f:
                    config = yaml.load(f)
            config = { CONTENT: {HOME: None, PAGES: None}}
        logger.info('Site config: {}'.format(config))
        return config

    def build_templates(self):
        """Build templates."""

    def build(self):
        """Build the website."""
        #TODO: Write code to update files only if they have changed.
        #      But until then, clobber the build first, and then build everything from new.
        if self.build_dir.check():
            protected_remove(self.build_dir)
        assert self.build_dir.check() == False, 'Build directory already exists.'.format(self.build_dir)
        self.build_dir.ensure(dir=1)
        site = self.get_site_design()
        
        for content_name, content_dir in self.get_content_dir(site):
            logger.info('Build content: {}: {}'.format(content_name, content_dir))
            if content_name == HOME:
                self.build_home_page('/', content_dir)
            else:
                for url, source in self.get_source_dir(content_dir):
                    self.build_page(url, source)

    def get_content_dir(self, site):
        for name in site[CONTENT]:
            if name in [HOME, PAGES, POSTS]:
                dirname = site[CONTENT][name]
                if dirname is None:
                    dirname = os.path.join(CONTENT, name)
                yield name, self.site_dir.join(dirname)
            else:
                assert 0, \
                    'Content not recognized: {}'.format(name)

    def get_source_dir(self, content_dir):
        for source in content_dir.visit():
            if source.check(dir=1):
                rel_source = source.relto(content_dir)
                url = os.path.join('/', rel_source)
                yield url, source  

    def build_home_page(self, url, source_dir):
        try:
            self.build_page(url, source_dir)
        except SourceDirNotFoundError as e:
            logger.warning(e.message)
        self.build_dir.ensure(url, 'index.html')

    def build_page(self, url, source_dir):
        logger.info("Build page: {}".format(url))
        if not source_dir.check(dir=1):
            raise SourceDirNotFoundError, \
                'Source dir not found: {}'.format(source_dir)
        target_dir = self.build_dir.join(url)
        source = self.get_page_source(source_dir)
        self.build_page_file(source, target_dir)
        self.build_page_assets(source_dir, target_dir)

    def get_page_source(self, source_dir):
        #TODO: Can also check for index.php file here too
        source_file = source_dir.join('index.html')
        if source_file.check():
            return source_file
        # No source file detected, so use a template

    def build_page_file(self, source, target_dir):
        if isinstance(source, py.path.local):
            #target_dir.ensure(dir=1)
            source.copy(target_dir)
        else:
            logger.warning("No source file found: {}".format(source))
            #TODO: Use a template to generate the file
            target_dir.join('index.html').ensure()

    def build_page_assets(self, source_dir, target_dir):
        for asset in source_dir.visit(fil='*.css'):
            logger.info('Get asset /{} from {}'.format(target_dir.relto(self.build_dir).join(asset.basename), asset))
            asset.copy(target_dir)

