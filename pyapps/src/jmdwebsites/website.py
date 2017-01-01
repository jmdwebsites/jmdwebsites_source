import logging
import py
import six
import os
import yaml


logger = logging.getLogger(__name__)


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


def get_project_dir(config_basename = '.jmdwebsite'):
    # Check for project file in this dir and ancestor dirs
    for dirpath in py.path.local().parts(reverse=True):
        for path in dirpath.listdir():
            if path.basename == config_basename:
                return path.dirpath()
    raise ProjectNotFoundError, \
        'Not a website project (or any of the parent directories): {} not found'.format(config_basename)
 
def protected_remove(path, valid_basenames=None):
    if valid_basenames  is None:
        valid_basenames = ['build']
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

def get_paths(parent, root_path='', sep='/'):
    for child_name, child in parent.items():
        if root_path.endswith(sep) or child_name.startswith(sep):
            child_path = root_path + child_name
        else:
            child_path = root_path + sep + child_name
        yield child_path
        if child:
            for path in get_paths(child, root_path = child_path):
                yield path

ISDIR = 1
ISFILE = 0
def get_targets(content_dict):
    for content_location in content_dict:
        for path in get_paths(content_dict[content_location]):
            if path.endswith('/'):
                yield os.path.join(path, 'index.html'), ISFILE
            else:
                yield path, ISDIR


brochure = '''
/:
  blog/:
    first-post/:
  contact:
  about:
    tmp.html:
'''

page = '''
<html>
</html>
'''
templates = {
    'page': '<><>'
}

def new_website(site_dirname = ''):
    """New website."""
    site_dir = py.path.local(site_dirname)
    logger.info('Create new website {}'.format(site_dir.strpath))
    if site_dir.check():
        raise PathAlreadyExists, \
            'Already exists: {}'.format(site_dir)
    site_dir.ensure('.jmdwebsite')
    for url in urls(yaml.load(brochure)):
        logger.info(url)

def get_site_design():
    #TODO: If a site.yaml exisits in .jmdwebsites, use it otherwise use the default base theme
    theme_dir = py.path.local(__file__).dirpath('themes','base')
    #print(theme_dir.join('site.yaml'))
    with theme_dir.join('site.yaml').open() as f:
        return yaml.load(f)

def init_website():
    """Initialize website."""
    site_dir = py.path.local()
    logger.info('Create new website {}'.format(site_dir.strpath))
    project_dir = py.path.local('.jmdwebsite')
    if project_dir.check():
        raise WebsiteProjectAlreadyExists, \
            'Website project already exists: {}'.format(project_dir)
    project_dir.ensure()
    #site_design = get_site_design()
    #for url in urls(yaml.load(brochure)):
    #    logger.info(url)


class Website(object):
    
    def __init__(self, site_dir=None, build_dir=None):
        logger.debug('Instantiate: {}({})'.format(self.__class__.__name__, repr(build_dir)))
        if site_dir is None:
            self.site_dir = get_project_dir()
        else:
            self.site_dir = py.path.local(site_dir)
        if build_dir is None:
            self.build_dir = self.site_dir.join('build')
        else:
            self.build_dir = py.path.local(build_dir)
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


    def build1(self):
        """Build the website."""

        #TODO: Write code to update files only if they have changed.
        #      But until then, clobber the build first, and then build everything from new.
        if self.build_dir.check():
            protected_remove(self.build_dir)
        assert self.build_dir.check() == False, 'Build directory already exists.'.format(self.build_dir)

        logger.info(self.build.__doc__.splitlines()[0])
        design_dir = self.site_dir.join('design')
        design_files = design_dir.visit(fil = ExtMatcher('.html .css'))
        for source in design_files:
            target = self.build_dir.join(source.basename)
            logger.info("Build {}".format(target))
            text = source.read()
            target.write(text, ensure=True)

    def build(self):
        """Build the website."""
        #TODO: Write code to update files only if they have changed.
        #      But until then, clobber the build first, and then build everything from new.
        if self.build_dir.check():
            protected_remove(self.build_dir)
        assert self.build_dir.check() == False, 'Build directory already exists.'.format(self.build_dir)

        design = get_site_design()
        for target, dir in get_targets(design['content']):
            logger.info(target)
            self.build_dir.ensure(target, dir=dir)
            
