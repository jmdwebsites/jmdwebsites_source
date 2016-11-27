import logging
import os
import py

logger = logging.getLogger(__name__)

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

    def build(self):
        """Build the project."""
        logger.info(self.build.__doc__)
 
        target = self.build_dir.join('index.html')
        source = self.src_dir.join('developer', target.basename)
        html = source.read()
        target.write(html, ensure=True)
