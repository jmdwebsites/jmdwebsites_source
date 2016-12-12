import logging
import py
import six
import os

logger = logging.getLogger(__name__)

class RemoveError(Exception): pass

def remove(path):
    logger.info('Remove {}'.format(path))
    for disallowed in [os.getcwd(), __file__]:
        if path in py.path.local(disallowed).parts():
            logger.error('{}: Removal not allowed'.format(path))
            raise RemoveError
    assert path.basename in ['build']
    #TODO: Check that file/dir is a child of a dir containing a .jmdwebsites file, 
    # thus indicating it is part of a website project.
    # for ancestor in path.parts():
    #     if not ancestor.join('.jmdwebsites').check():
    #         raise RemoveError
    if path.check():
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
        

class Website(object):
    
    def __init__(self, build_dir='build'):
        logger.debug('Instantiate: {}({})'.format(self.__class__.__name__, repr(build_dir)))
        self.site_dir = py.path.local()
        self.build_dir = py.path.local(build_dir)
        logger.info('Website root: {}'.format(self.site_dir))

    def clean(self):
        """Clean up the build."""
        logger.info(self.clean.__doc__)

    def clobber(self):
        """Clobber the build removing everything."""
        logger.info(self.clobber.__doc__)
        remove (self.build_dir)

    def build(self):
        """Build the website."""

        #TODO: Write code to update files only if they have changed.
        #      But until then, clobber the build first, and then build everything from new.
        remove (self.build_dir)
        assert self.build_dir.check() == False, 'Build directory already exists.'.format(self.build_dir)

        logger.info(self.build.__doc__.splitlines()[0])
        design_dir = self.site_dir.join('design')
        design_files = design_dir.visit(fil = ExtMatcher('.html .css'))
        for source in design_files:
            target = self.build_dir.join(source.basename)
            logger.info("Build {}".format(target))
            text = source.read()
            target.write(text, ensure=True)

#assert 0
# Should the a build subdir be created in the testdir in the fixture
# Then can test that it is removed first!