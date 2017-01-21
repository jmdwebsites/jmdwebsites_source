from __future__ import print_function
from copy import copy, deepcopy
import logging
import os
from pprint import pformat

import jinja2
import py
import ruamel.yaml as ryaml
from ruamel.yaml.compat import ordereddict
from ruamel.yaml.comments import CommentedMap
import six
import yaml

from jmdwebsites.log import dbgdump, yamldump
from jmdwebsites.html import prettify

logger = logging.getLogger(__name__)

BUILD = 'build'
CONTENT = 'content'
CONFIG_FILE = 'site.yaml'
PAGE_SPECS_FILE = 'pagespecs.yaml'
PROJDIR = '.jmdwebsite'
HOME = 'home'
PAGES = 'pages'
POSTS = 'posts'

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
class AncestorNotFoundError(WebsiteError): pass
class PartialNotFoundError(WebsiteError): pass
class MissingContentError(WebsiteError): pass
class UnusedContentError(WebsiteError): pass
class MissingVarsError(WebsiteError): pass
class FileFilterError(Exception): pass
class InvalidContentTypeError(Exception): pass


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
    logger.info('Remove {}'.format(path))
    path.remove()


class FileFilter:

    def __init__(self, startswith=None, extensions=None):
        if extensions is None:
            self.extensions = extensions
        elif isinstance(extensions, six.string_types):
            self.extensions = set(extensions.split())
        else:
            self.extensions = set(extensions)
        if isinstance(startswith, six.string_types):
            self.startswith = startswith
        else:
            raise FileFilterError('Not a string: startswith: {}'.format(repr(startswith)))

    def __call__(self, path):
        allow = True
        if self.extensions is not None and path.ext not in self.extensions:
            allow = False
        if allow and not path.basename.startswith(self.startswith):
            allow = False
        return allow


def dict_walker(parent, parent_path=''):
    if isinstance(parent, dict):
        for child_name, child in parent.items():
            child_path = os.path.join(parent_path, child_name)
            yield child_path, child
            for path, value in dict_walker(child, parent_path = child_path):
                yield path, value


def get_site_design(site_dir):
    #TODO: If a CONFIG_FILE exists, use it. 
    #      Otherwise, use a default version in the theme dir
    config_file = site_dir.join(CONFIG_FILE)
    if config_file.check():
        logger.info('Site config file: {}'.format(config_file))
        with site_dir.join(CONFIG_FILE).open() as f:
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


def new_website(site_dirname = ''):
    """New website."""
    site_dir = py.path.local(site_dirname)
    logger.info('Create new website {}'.format(site_dir.strpath))
    if site_dir.check():
        raise PathAlreadyExists(
            'Already exists: {}'.format(site_dir))
    site_dir.ensure( PROJDIR)
    logger.error('TODO:')


def init_website():
    """Initialize website."""
    site_dir = py.path.local()
    logger.info('Init website {}'.format(site_dir.strpath))
    project_dir = py.path.local( PROJDIR)
    if project_dir.check():
        raise WebsiteProjectAlreadyExists(
            'Website project already exists: {}'.format(project_dir))
    logger.info('Create proj dir {}'.format(project_dir.strpath))
    project_dir.ensure(dir=1)
    site_dir.ensure(CONFIG_FILE)


def build_home_page(url, source_dir, build_dir):
    try:
        build_page(url, source_dir, build_dir)
    except SourceDirNotFoundError as e:
        logger.error(e)
    build_dir.ensure(url, 'index.html')


def build_page(url, source_dir, build_dir):
    logger.debug('%%%%%%%%%%%%%%%%%%%%% {} %%%%%%%%%%%%%%%%%%%%%'.format(url))
    logger.info("Build page: {}".format(url))
    if not source_dir.check(dir=1):
        raise SourceDirNotFoundError(
            'Source dir not found: {}'.format(source_dir))
    build_html_file(url, source_dir, build_dir)
    build_page_assets(url, source_dir, build_dir)


def build_html_file(url, source_dir, build_dir):
    logger.debug('build_html_file(): source_dir: {}'.format(source_dir))
    target_dir = build_dir.join(url)

    #TODO: Can also check for index.php file here too
    source_file = source_dir.join('index.html')
    if source_file.check():
        source_file.copy(target_dir)
        return
    logger.debug("No source file found: {}".format(source_file))
    # No source file detected, so use a template

    page_spec = get_page_spec(url, source_dir)
    template = get_template(page_spec)
    content = get_content(page_spec, source_dir, fil=FileFilter('_', ['.html','.md']))
    html = render_html(template, content)
    target_dir.ensure(dir=1)
    target_dir.join('index.html').write(html)


def get_page_spec(url, source_dir=None):
    logger.debug('get_page_spec({})'.format(url, source_dir))
    
    specs = get_page_specs(source_dir)

    page_spec_name = os.path.basename(url)
    if page_spec_name not in specs['pages']:
        page_spec_name = 'page'
    logger.debug('get_page_spec(): spec name: {}'.format(page_spec_name))

    raw_page_spec = get_spec(page_spec_name, specs['pages'])
    logger.debug('get_page_spec(): {}: raw: {}'.format(
        page_spec_name, yamldump(raw_page_spec)))
    
    page_spec = {type_: get_spec(name, specs[type_]) 
        for type_, name in raw_page_spec.items()} 
    logger.debug('get_page_spec(): {}: processed: {}'.format(
        page_spec_name, yamldump(page_spec)))

    return page_spec


def get_page_specs(source_dir=None):
    page_specs_file = source_dir.join(PAGE_SPECS_FILE)
    if source_dir and page_specs_file.check():
        pass
    else:
        page_specs_file = py.path.local(__file__).dirpath(PAGE_SPECS_FILE)
    with page_specs_file.open() as f:
        specs = ryaml.load(f, Loader=ryaml.RoundTripLoader)
    return specs


def render_html(template, content):
    logger.debug('render_html(template, content)')
    rendered = render(template, content)
    html = prettify(rendered)
    logger.debug('render_html(): html: ' + dbgdump(html))
    return html


def render(template, content, j2=False):
    logger.debug('render(template, content)')
    if j2:
        jtemplate = jinja2.Template(template)
        rendered_output = jtemplate.render(**content)
    else:
        rendered_output = template.format(**content)
    logger.debug('render(): rendered_output: {}'.format(dbgdump(rendered_output)))
    return rendered_output


def get_content(spec, source_dir, fil=None):
    content_spec = spec['content']
    source_content = get_source_content(source_dir, fil=fil)

    missing_content = {key:value for key, value in content_spec.items() if value is None and key not in source_content}
    if missing_content:
        raise MissingContentError('Not found: {}'.format(missing_content.keys()))
    unused_content = [key for key in source_content if key not in content_spec]
    if unused_content:
        raise UnusedContentError('Unused content: {}'.format(unused_content))

    vars = get_vars(spec['vars'])

    content = copy(content_spec)
    logger.debug('content: spec: {}'.format(content.keys()))

    content.update(source_content)
    logger.debug('content: source_content update: {}'.format(content.keys()))

    content.update(vars)
    logger.debug('content: vars update: {}'.format(content.keys()))

    return content


def get_source_content(source_dir, fil=None):
    source_content = {}
    for partial_file in source_dir.visit(fil=fil):
        partial_name = partial_file.purebasename.lstrip('_')
        source_content[partial_name] = partial_file.read()
    return source_content


def get_vars(vars):
    logger.debug('vars: {}'.format(vars.keys()))
    missing_vars = {var:value for var, value in vars.items() if value is None}
    if missing_vars:
        raise MissingVarsError('Not found: {}'.format(missing_vars.keys()))
    return vars


def get_template(spec, name='doc'):
    logger.debug('get_template(): Get partials. {}')
    template = '\n'.join(partial_getter(spec))
    logger.debug('get_template(): template: {}'.format(dbgdump(template)))
    return template


def partial_getter(spec, name='doc'):
    layouts = spec['layouts']
    try:
        top = layouts[name]
    except KeyError:
        return
    logger.debug('partial_getter(): stem: ' + name)
    if top:
        for child_name in top:
            fmt = spec['partials'][child_name]
            if child_name in layouts and layouts[child_name]:
                child = '\n'.join(partial_getter(spec, name=child_name))
                child = '\n{}\n'.format(child)
            else:
                logger.debug('partial_getter(): leaf: ' + child_name)
                child = '{{{0}}}'.format(child_name)
            partial = fmt.format(**{child_name: child})
            yield partial

def get_spec(name, root):
    logger.debug('get_spec(): {}'.format(name))
    ancestors = [root[name]] + [anc for anc in inheritor(root[name], root) if anc]
    logger.debug('get_spec(): ancestors: {}'.format(
        yamldump(ancestors)))
    if not ancestors:
        return ordereddict()
    spec = deepcopy(ancestors[-1])
    for ancestor in reversed(ancestors):
        for key, value in ancestor.items():
            spec[key] = value
    del spec['inherit']
    return spec


def inheritor(current, root):
    while(current):
        try:
            inherited = current['inherit']
        except KeyError:
            break
        if not inherited:
            break
        try:
            current = root[inherited]
        except KeyError:
            raise AncestorNotFoundError('Not found: inherited: {}'.format(inherited))
        yield current


def build_page_assets(url, source_dir, build_dir):
    target_dir = build_dir.join(url)
    for asset in source_dir.visit(fil='*.css'):
        logger.info('Get asset /{} from {}'.format(
            target_dir.relto(build_dir).join(asset.basename), 
            asset))
        asset.copy(target_dir)


class Website(object):
    def __init__(self, site_dir=None, build_dir=None):
        logger.debug('Instantiate: {}({})'.format(
            self.__class__.__name__, 
            repr(build_dir)))
        if site_dir is None:
            self.site_dir = get_project_dir()
        else:
            self.site_dir = py.path.local(site_dir)
        if build_dir is None:
            self.build_dir = self.site_dir.join(BUILD)
        else:
            self.build_dir = py.path.local(build_dir)
        #self.content_dir = self.site_dir.join(CONTENT)
        logger.info('site dir name: {}'.format(self.site_dir))
        logger.info('build dir name: {}'.format(self.build_dir))

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
        site = get_site_design(self.site_dir)
        
        for content_name, content_dir in self.content_dir_getter(site):
            logger.info('Build content: {}: {}'.format(
                content_name, content_dir))
            if content_name == HOME:
                build_home_page('/', content_dir, self.build_dir)
            else:
                for page_path in content_dir.visit(fil=isdir):
                    url = self.get_url(page_path.relto(content_dir), site)
                    build_page(url, page_path, self.build_dir)

    def get_url(self, rel_page_path, site):
        #TODO: Check site config to get slugs and relpagepath to url mappings.
        url = os.path.join('/', rel_page_path)
        return url

    def content_dir_getter(self, site):
        for content_type, dirname in site[CONTENT].items():
            if content_type not in set([HOME, PAGES, POSTS]):
                raise InvalidContentTypeError(
                    'Invalid content type: {}'.format(content_type))
            if dirname is None:
                dirname = os.path.join(CONTENT, content_type)
            logger.info('content_dir_getter(): {}: {}'.format(
                content_type, dirname))
            yield content_type, self.site_dir.join(dirname)

