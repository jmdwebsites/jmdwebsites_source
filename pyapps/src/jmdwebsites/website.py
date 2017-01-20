from __future__ import print_function
import copy
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
TEMPLATE_FILE = 'templates.yaml'
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
class TemplateNotFoundError(WebsiteError): pass
class PartialNotFoundError(WebsiteError): pass
class MissingContentError(WebsiteError): pass
class UnusedContentError(WebsiteError): pass


def dir_getter(root_path):
    return (path for path in root_path.visit() if path.check(dir=1))


def url_and_dir_getter(root):
    for dir in dir_getter(root):
        url = os.path.join('/', dir.relto(root))
        yield url, dir  


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


class ExtMatcher:
    def __init__(self, extensions=None):
        if extensions is None:
            extensions = []
        if isinstance(extensions, six.string_types):
            extensions = extensions.split()
        self.extensions = set(extensions)

    def __call__(self, path):
        return path.ext in self.extensions


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

    html_content = get_html_content(source_dir)

    #TODO: Can also check for index.php file here too
    source_file = source_dir.join('index.html')
    if source_file.check():
        source_file.copy(target_dir)
        return
    logger.debug("No source file found: {}".format(source_file))
    # No source file detected, so use a template
    template = get_page_template(source_dir)
    html = get_html(template, html_content)
    target_dir.ensure(dir=1)
    target_dir.join('index.html').write(html)


def get_html_content(source_dir):
    def is_content(path):
        if path.basename.startswith('_') and path.ext in set(['.html','.md']):
            return True
        return False
    content = {}
    for partial_file in source_dir.visit(fil=is_content):
        partial_name = partial_file.purebasename.lstrip('_')
        content[partial_name] = partial_file.read()
    return content


def get_page_template(source_dir):
    logger.debug('get_page_template({})'.format(source_dir))
    with py.path.local(__file__).dirpath(TEMPLATE_FILE).open() as f:
        templates = ryaml.load(f, Loader=ryaml.RoundTripLoader)

    if source_dir.basename in templates['pages']:
        tplname = source_dir.basename
    else:
        tplname = 'page'
    logger.debug('get_page_template(): template name: {}'.format(tplname))

    raw_page_tpl = inherit(tplname, 'pages', templates)
    logger.debug('get_page_template(): {}: raw: {}'.format(
        tplname, yamldump(raw_page_tpl)))
    
    page_tpl = {tpltype: inherit(tplname, tpltype, templates) 
        for tpltype, tplname in raw_page_tpl.items()} 
    logger.debug('get_page_template(): {}: processed: {}'.format(
        tplname, yamldump(page_tpl)))

    return page_tpl


def get_html(template, content):
    logger.debug('get_html(template, content)')
    rendered = render(template, content)
    html = prettify(rendered)
    logger.debug('get_html(): html: ' + dbgdump(html))
    return html


def render(template, content, j2=False):
    logger.debug('render(template, content)')
    template_str = get_template_str(template, content)
    logger.debug('render(): template_str: ' + dbgdump(template_str))
    if j2:
        jtemplate = jinja2.Template(template_str)
        rendered_output = jtemplate.render(**content)
    else:
        vars = {}
        vars.update(template['vars'])
        vars.update(content)
        rendered_output = template_str.format(**vars)
    return rendered_output


def get_template_str(template, content, name='doc'):
    logger.debug('get_template_str(): Get template partials. {}'.format(
        '-----------------------------------'))
    template_str = '\n'.join(partial_getter(template))
    logger.debug('get_template_str(): template_str: {}'.format(dbgdump(template_str)))

    # vars
    vars = template['vars']
    logger.debug('vars: {}'.format(vars.keys()))
    valid_vars = {var:value for var, value in vars.items() if value is not None}
    logger.debug('valid_vars: {}'.format(valid_vars.keys()))
    empty_vars = {var:value for var, value in vars.items() if value is None}
    logger.debug('empty_vars: {}'.format(empty_vars.keys()))
    
    # content
    logger.debug('content: {}'.format(content.keys()))
    logger.debug('template_content: {}'.format(template['content'].keys()))
    used_content = {key:'\n{}'.format(content[key]) for key in template['content'] if key in content}
    logger.debug('used_content: {}'.format(used_content.keys()))
    overrides = [key for key in used_content if template['content'][key] is not None]
    logger.debug('overrides: {}'.format(overrides))
    selected_content = template['content']
    selected_content.update(used_content)
    logger.debug('selected_content: {}'.format(selected_content.keys()))
    missing_content = {key:value for key, value in selected_content.items() if value is None}
    logger.debug('missing_content: {}'.format(missing_content.keys()))
    unused_content = [key for key in content if key not in selected_content]
    logger.debug('unused_content: {}'.format(unused_content))

    if missing_content:
        raise MissingContentError('Not found: {}'.format(missing_content.keys()))
    if unused_content:
        raise UnusedContentError('Unused content: {}'.format(unused_content))

    valid = valid_vars
    valid.update(selected_content)
    template_str = template_str.format(**valid)
    logger.debug('get_template_str(): template_str: filled: {}'.format(dbgdump(template_str)))
    return template_str


def partial_getter(template, name='doc'):
    layouts = template['layouts']
    try:
        top = layouts[name]
    except KeyError:
        return
    logger.debug('partial_getter(): stem: ' + name)
    if top:
        for child_name in top:
            fmt = template['partials'][child_name]
            if child_name in layouts and layouts[child_name]:
                child = '\n'.join(partial_getter(template, name=child_name))
                child = '\n{}\n'.format(child)
            else:
                logger.debug('partial_getter(): leaf: ' + child_name)
                child = '{{{0}}}'.format(child_name)
            partial = fmt.format(**{child_name: child})
            yield partial

def inherit(tplname, tpltype, templates):
    logger.debug('inherit(): {}: {}'.format(tpltype, tplname))
    tpl = templates[tpltype][tplname]
    templates = templates[tpltype]
    ancestors = [tpl] + [anc for anc in inheritor(tpl, templates) if anc]
    logger.debug('inherit(): ancestors: {}'.format(
        yamldump(ancestors)))
    if not ancestors:
        return ordereddict()
    template = copy.deepcopy(ancestors[-1])
    for ancestor in reversed(ancestors):
        for key, value in ancestor.items():
            template[key] = value
    del template['inherit']
    return template


def inheritor(template, root):
    while (template):
        try:
            inherited = template['inherit']
        except KeyError:
            break
        if not inherited:
            break
        try:
            template = root[inherited]
        except KeyError:
            raise TemplateNotFoundError('Inherited template not found: {}'.format(inherited))
        yield template


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

    def build_templates(self):
        """Build templates."""

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
                content_name, 
                content_dir))
            if content_name == HOME:
                build_home_page('/', content_dir, self.build_dir)
            else:
                for url, source_dir in url_and_dir_getter(content_dir):
                    build_page(url, source_dir, self.build_dir)

    def content_dir_getter(self, site):
        for name in site[CONTENT]:
            if name in set([HOME, PAGES, POSTS]):
                dirname = site[CONTENT][name]
                if dirname is None:
                    dirname = os.path.join(CONTENT, name)
                yield name, self.site_dir.join(dirname)
            else:
                assert 0, \
                    'Content not recognized: {}'.format(name)
