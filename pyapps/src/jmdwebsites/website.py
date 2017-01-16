from __future__ import print_function
#from collections import OrderedDict
import copy
import logging
import os
from pprint import pformat

import py
import ruamel.yaml as ryaml
from ruamel.yaml.compat import ordereddict
import six
import yaml

#import partials

logger = logging.getLogger(__name__)

BUILD = 'build'
CONTENT = 'content'
CONFIG_FILE = 'site.yaml'
TEMPLATE_FILE = 'templates.yaml'
PROJDIR = '.jmdwebsite'
HOME = 'home'
PAGES = 'pages'
POSTS = 'posts'
STARTSTR     =   '*** START ***'
ENDSTR       =   '**** END ****'
STARTSTR_N   =   '*** START ***\n'
ENDSTR_N     =   '**** END ****\n'
N_STARTSTR   = '\n*** START ***'
N_ENDSTR     = '\n**** END ****'
N_STARTSTR_N = '\n*** START ***\n'
N_ENDSTR_N   = '\n**** END ****\n'

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
class TemplateNotFoundError(WebsiteError): pass
class PartialNotFoundError(WebsiteError): pass


def dir_getter(root_path):
    return (path for path in root_path.visit() if path.check(dir=1))


def url_and_dir_getter(root):
    for dir in dir_getter(root):
        url = os.path.join('/', dir.relto(root))
        yield url, dir  


def yamldump(data):
    return ryaml.dump(data, Dumper=ryaml.RoundTripDumper)


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


def new_website(site_dirname = ''):
    """New website."""
    site_dir = py.path.local(site_dirname)
    logger.info('Create new website {}'.format(site_dir.strpath))
    if site_dir.check():
        raise PathAlreadyExists, \
            'Already exists: {}'.format(site_dir)
    site_dir.ensure( PROJDIR)
    logger.error('TODO:')


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
        #TODO: If a CONFIG_FILE exists, use it. Otherwise, use a default version in the theme dir
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
        
        for content_name, content_dir in self.content_dir_getter(site):
            logger.info('Build content: {}: {}'.format(content_name, content_dir))
            if content_name == HOME:
                self.build_home_page('/', content_dir)
            else:
                for url, source_dir in url_and_dir_getter(content_dir):
                    self.build_page(url, source_dir)

    def content_dir_getter(self, site):
        for name in site[CONTENT]:
            if name in [HOME, PAGES, POSTS]:
                dirname = site[CONTENT][name]
                if dirname is None:
                    dirname = os.path.join(CONTENT, name)
                yield name, self.site_dir.join(dirname)
            else:
                assert 0, \
                    'Content not recognized: {}'.format(name)

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
        self.build_page_file(source_dir, target_dir)
        self.build_page_assets(source_dir, target_dir)

    def build_page_file(self, source_dir, target_dir):
        #TODO: Can also check for index.php file here too
        source_file = source_dir.join('index.html')
        if source_file.check():
            source_file.copy(target_dir)
            return
        logger.debug("No source file found: {}".format(source_file))
        # No source file detected, so use a template

        template = self.get_page_template(source_dir)

        target_dir.ensure(dir=1)
        target_dir.join('index.html').write(template)

    def get_page_template(self, source_dir):
        try:
            template_source = self.get_template_source(source_dir.basename)
        except TemplateNotFoundError:
            template_source = self.get_template_source('empty')

        template = '\n'.join(self.partial_getter(template_source, 'doc'))
        #logger.debug('get_page_template(): template: represented by' + N_STARTSTR_N + repr(template) + N_ENDSTR)
        logger.debug('get_page_template(): template:' + N_STARTSTR_N + template + N_ENDSTR)
        return template

    def get_template_source(self, page_name):
        with py.path.local(__file__).dirpath(TEMPLATE_FILE).open() as f:
            templates = ryaml.load(f, Loader=ryaml.RoundTripLoader)
        
        page_template = self.get_sub_template_source(templates['pages'], page_name)
        logger.debug('get_template_source(): page_template: raw:' + N_STARTSTR_N + yamldump(page_template) + ENDSTR)
        for name in page_template:
            page_template[name] = self.get_sub_template_source(templates[name], page_template[name])
        logger.debug(repr(page_template))
        logger.debug('get_template_source(): page_template: processed:' + N_STARTSTR_N + yamldump(page_template) + ENDSTR)
        return page_template

    def get_sub_template_source(self, templates, name):
        ancestors = [ancestor for ancestor_name, ancestor in self.inheritor(templates, name) if ancestor]
        logger.debug('get_sub_template_source: ancestors:' + N_STARTSTR_N + repr(ancestors) + N_ENDSTR)
        if not ancestors:
            return ordereddict()
        template = copy.deepcopy(ancestors[-1])
        for ancestor in reversed(ancestors):
            for block_name, block in ancestor.items():
                template[block_name] = block
        del template['inherit']
        return template

    def inheritor(self, templates, template_name):
        if template_name not in templates:
            raise TemplateNotFoundError, '{}: Template not found'.format(template_name)
        template = templates[template_name]
        logger.debug('inheritor(): {}: {}'.format(template_name, template))
        yield template_name, template
        while (template and ('inherit' in template) and template['inherit']):
            inherited_name = template['inherit']
            if inherited_name not in templates:
                raise TemplateNotFoundError, '{}: Inherited template not found: {}'.format(template_name, inherited_name)
            template = templates[inherited_name]
            yield inherited_name, template

    def partial_getter(self, source_template, name):
        layouts = source_template['layouts']
        logger.debug('partial_getter(): ' + name)
        if name not in layouts or not layouts[name]:
            return
        for child_name in layouts[name]:
            child = '\n'.join(self.partial_getter(source_template, child_name))
            if child:
                child = '\n{}\n'.format(child)
            logger.debug('partial_getter(): /' + child_name)
            try:
                partial = source_template['partials'][child_name].format(child)
            except KeyError:
                raise PartialNotFoundError, \
                    'Partial not found: {}'.format(child_name)
            yield partial
                
    def build_page_assets(self, source_dir, target_dir):
        for asset in source_dir.visit(fil='*.css'):
            logger.info('Get asset /{} from {}'.format(target_dir.relto(self.build_dir).join(asset.basename), asset))
            asset.copy(target_dir)
