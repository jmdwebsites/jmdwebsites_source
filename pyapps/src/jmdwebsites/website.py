import logging
import py
import six
import os


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


def get_project_dir(config_basename = '.jmdwebsite'):
    # Check for project file in this dir and ancestor dirs
    for dirpath in py.path.local().parts(reverse=True):
        for path in dirpath.listdir():
            if path.basename == config_basename:
                return path.dirpath()
    raise ProjectNotFoundError, \
        'Not a website project (or any of the parent directories): File not found: {}: {}'.format(config_basename, py.path.local())
 
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

def new_website(site_dirname):
    """New website."""
    site_dir = py.path.local(site_dirname)
    logger.info('Create new website {}'.format(site_dir.strpath))
    if site_dir.check():
        raise PathAlreadyExists, \
            'Already exists: {}'.format(site_dir)
    site_dir.ensure()

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


    def build(self):
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
