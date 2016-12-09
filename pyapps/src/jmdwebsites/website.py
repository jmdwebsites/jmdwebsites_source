import logging
import os
import py
import six

logger = logging.getLogger(__name__)

class ExtMatcher:
    def __init__(self, extensions=None):
        if isinstance(extensions, six.string_types):
            extensions = extensions.split()
        self.extensions = extensions

    def __call__(self, path):
        return path.ext in self.extensions
        

class Website(object):
    
    def __init__(self, build_dir='build'):
        logger.info('Instantiate {}({})'.format(self.__class__.__name__, repr(build_dir)))
        self.src_dir = py.path.local('src')
        self.build_dir = py.path.local(build_dir)

    def clean(self):
        """Clean up the build."""
        logger.info(self.clean.__doc__)

    def clobber(self):
        """Clobber the build removing everything."""
        logger.info(self.clobber.__doc__)
        self.build_dir.remove()

    def build(self):
        """Build the website."""
        logger.info(self.build.__doc__)

        #TODO: Write code to update files only if they have changed.
        #      But until then, clobber the build, and build everything from new.
        self.build_dir.remove()
        assert self.build_dir.check() == False, 'Build directory already exists.'.format(self.build_dir)

        web_files = self.src_dir.join('developer').visit(
            fil = ExtMatcher('.html .css'))
        for source in web_files:
            target = self.build_dir.join(source.basename)
            logger.info("Build {}".format(target))
            text = source.read()
            target.write(text, ensure=True)

