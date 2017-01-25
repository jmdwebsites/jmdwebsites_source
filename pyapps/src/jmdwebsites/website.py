from __future__ import print_function
from copy import copy, deepcopy
import logging
import os
from pprint import pformat

import jinja2
import mistune
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
CONTENT_GROUP = 'content_group'
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
class InvalidContentGroupError(Exception): pass
class FileNotFoundError(Exception): pass
class NotFoundError(Exception): pass
class DictWalkerError(Exception): pass
class ContentFileError(WebsiteError): pass


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
    if not isinstance(parent, dict):
        raise DictWalkerError('Not a dictionary: {}'.format(root))
    for key, value in parent.items():
        path = os.path.join(parent_path, key)
        root = parent
        yield path, root, key, value
        if isinstance(value, dict):
            for path, root, key, value in dict_walker(value, parent_path=path):
                yield path, root, key, value


def get_site_design(site_dir):
    config_file = None
    if not config_file:
        config_file = site_dir.join(CONFIG_FILE)
        if not config_file.check():
            config_file = None
    ##TODO: If a CONFIG_FILE exists, use it. 
    ##      Otherwise, use a default version in the theme dir
    #if not config_file:
    #    config_file = theme_dir.join(CONFIG_FILE)
    #    if not config_file.check():
    #        config_file = None
    if not config_file:
        config_file = py.path.local(__file__).dirpath(CONFIG_FILE)
        if not config_file.check():
            config_file = None
    if not config_file:
        raise FileNotFoundError('Site config file: Not found: {}'.format(config_file))
        config = { CONTENT_GROUP: {HOME: None, PAGES: None}}
    else:
        logger.info('Site config file: {}'.format(config_file))
        with config_file.open() as f:
            config = ryaml.load(f, Loader=ryaml.RoundTripLoader)
    logger.info('Site config: {}'.format(yamldump(config)))
    return config


#TODO: Use this for testing inherit_file_data() and path_inheritor(). 
#      Will come back to it.
def get_site_design2(site_dir):
    return inherit_file_data(CONFIG_FILE, site_dir)


def inherit_file_data(basename, site_dir):
    for filepath in path_inheritor(basename, site_dir):
        with filepath.open() as file:
            if filepath.ext == '.yaml':
                data = ryaml.load(file, Loader=ryaml.RoundTripLoader)
            else:
                assert 0
                data = file.read()
    logger.error(yamldump(data))
    return data


def path_inheritor(basename, site_dir):
    path = None
    locations = [
        site_dir,  
        py.path.local(__file__).dirpath()
    ]
    look_for = [dirpath.join(basename) for dirpath in locations]
    available = [filepath for filepath in look_for if filepath.check(file=1)]
    if not available:
        raise FileNotFoundError('Not found: {}'.format(basename))
    for filepath in available:
        yield filepath
        break
    

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


def content_dir_getter(site, site_dir):
    site = ensure_spec(site, [])
    logger.error(site)
    if CONTENT_GROUP in site:
        for content_group, dirname in site[CONTENT_GROUP].items():
            if content_group not in set([HOME, PAGES, POSTS]):
                raise InvalidContentGroupError(
                    'Invalid content group: {}'.format(content_group))
            if dirname is None:
                dirname = os.path.join(CONTENT, content_group)
            logger.info('content_dir_getter(): {}: {}'.format(
                content_group, dirname))
            yield content_group, site_dir.join(dirname)
    else:
        root, dirs, files = next(os.walk(site_dir.join(CONTENT).strpath))
        for content_group in dirs: 
            yield content_group, site_dir.join(CONTENT, content_group)


def page_path_getter(content_group, content_dir):
    logger.info('Build content: {}: {}'.format(
        content_group, content_dir))
    if content_group == HOME:
        yield content_dir, ''
    else:
        for page_path in content_dir.visit(fil=isdir):
            yield content_dir, page_path.relto(content_dir)


def get_url(rel_page_path, site):
    #TODO: Check site config to get slugs and relpagepath to url mappings.
    url = os.path.join('/', rel_page_path)
    return url


class Info():
    def __init__(self, url):
        self.url = url


def build_page(page_root, rel_page_path, build_dir, site):
    logger.debug('%%%%%%%%%%%%%%%%%%%%% {} %%%%%%%%%%%%%%%%%%%%%'.format(rel_page_path))
    logger.info("Build page: {}".format(rel_page_path))
    source_dir = page_root.join(rel_page_path)
    url = get_url(rel_page_path, site)
    page_spec = get_page_spec(url, site)
    target_dir = build_dir.join(url)

    logger.debug('22222222222222222222 {} 22222222222222222222'.format(url))
    logger.info("Build file: {}".format(url))
    if not source_dir.check(dir=1):
        raise SourceDirNotFoundError(
            'Source dir not found: {}'.format(source_dir))
    html = get_html(source_dir, page_spec, info=Info(url))

    build_html_file(html, target_dir)
    build_page_assets(source_dir, target_dir)


def build_html_file(html, target_dir):
    target_dir.ensure(dir=1).join('index.html').write(html)


def get_html(source_dir, page_spec, info=None):
    logger.debug('build_html_file(): source_dir: {}'.format(source_dir))
    #TODO: Can also check for index.php file here too
    source_file = source_dir.join('index.html')
    if source_file.check():
        #source_file.copy(target_dir.ensure(dir=1))
        logger.debug('build_html_file(): Validate source file: {}'.format(source_file))
        html = source_file.read()
        # Validate that the file is unicode and that the html is ok
    else:
        logger.debug("No source file found: {}".format(source_file))
        # No source file detected, so use a template
        template = get_template(page_spec)
        content = get_content(source_dir, page_spec, fil=FileFilter('_', ['.html','.md']), info=info)
        html = render_html(template, content, info=info)
    return html


def get_page_spec(url, specs):
    logger.debug('get_page_spec(): url: {}'.format(repr(url)))

    try:
        page_specs = specs['pages']
    except (KeyError, TypeError):
        return None

    if url in page_specs:
        page_spec_name = url
    else:
        page_spec_name = 'default'
    logger.debug('get_page_spec(): page_spec_name: {}'.format(repr(page_spec_name)))

    raw_page_spec = get_spec(page_spec_name, page_specs)
    logger.debug('get_page_spec(): {}: raw: {}'.format(
        page_spec_name, yamldump(raw_page_spec)))
    
    page_spec = CommentedMap((type_, get_spec(name, specs[type_])) 
        for type_, name in raw_page_spec.items())

    # Active nav links
    for path, root, key, value in dict_walker(page_spec):
        if value == 'navlink' and page_spec['navlinks'][key] == url:
            root[key] = 'activenavlink'

    logger.debug('get_page_spec(): {}: processed: {}'.format(
        page_spec_name, yamldump(page_spec)))

    return page_spec


def render_html(template, content, **kwargs):
    logger.debug('render_html(template, content)')
    rendered = render(template, content, **kwargs)
    html = prettify(rendered)
    logger.debug('render_html(): html: ' + dbgdump(html))
    return html


def render(template, content, info=None, j2=False, **kwargs):
    logger.debug('render(template, content)')
    if j2:
        template = jinja2.Template(template)
    try:
        rendered_output = template.format(info=info, **content)
    except KeyError as e:
        raise NotFoundError('Missing content or var: {}'.format(e))
    logger.debug('render(): rendered_output: {}'.format(dbgdump(rendered_output)))
    return rendered_output


def ensure_spec(spec, names=['content_group', 'content', 'layouts', 'partials', 'vars', 'navlinks']):
    names = set(names)
    if spec is None:
        logger.warning('Invalid spec: spec: {}'.format(repr(spec)))
        spec = CommentedMap()
    for name in names:
        try:
            _subspec = spec[name]
        except TypeError:
            logger.warning('Invalid spec: spec: {}'.format(repr(spec)))
            spec = CommentedMap()
            spec[name] = CommentedMap()
            raise TypeError
        except KeyError:
            logger.warning('Not found in spec: {}'.format(repr(name)))
            spec[name] = CommentedMap()
    return spec


def get_content(source_dir, spec=None, info=None, fil=None):
    spec = ensure_spec(spec, ['content', 'vars', 'navlinks'])
        
    source_content = get_source_content(source_dir, fil=fil)

    missing_content = {key:value for key, value in spec['content'].items() if value is None and key not in source_content}
    if missing_content:
        raise MissingContentError('Not found: {}'.format(missing_content.keys()))
    unused_content = [key for key in source_content if key not in spec['content']]
    if unused_content:
        raise UnusedContentError('Unused content: {}'.format(unused_content))

    content = copy(spec['content'])
    if info:
        for key, value in content.items():
            content[key] = value.format(info=info)
    logger.debug('Default: content: {}'.format(content.keys()))

    content.update(source_content)
    logger.debug('Update with source_content: content: {}'.format(content.keys()))

    vars = get_vars(spec['vars'])
    content.update(vars)
    logger.debug('Update with vars : content: {}'.format(content.keys()))

    if 'navlinks' in spec:
        content.update(spec['navlinks'])
        logger.debug('Update with navlinks: content: {}'.format(content.keys()))

    return content


def get_source_content(source_dir, fil=None, markdown=mistune.Markdown()):
    source_content = {}
    for partial_file in source_dir.visit(fil=fil):
        partial_name = partial_file.purebasename.lstrip('_')
        text = partial_file.read()
        if partial_file.ext == '.html':
            html = text
        elif partial_file.ext == '.md':
            html = markdown(text)
        else:
            raise ContentFileError('Invalid file type: {}'.format(partial_file))
        source_content[partial_name] = html
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
    spec = ensure_spec(spec, ['layouts', 'partials'])
    layouts = spec['layouts']
    try:
        top = layouts[name]
    except KeyError:
        return
    logger.debug('partial_getter(): stem: ' + name)
    if top:
        for child_name, partial_name in top.items():
            if partial_name is None:
                partial_name = child_name
            try:
                fmt = spec['partials'][partial_name]
            except KeyError:
                raise PartialNotFoundError('Partial not found: {}'.format(partial_name))
            if child_name in layouts and layouts[child_name]:
                child = '\n'.join(partial_getter(spec, name=child_name))
                child = '\n{}\n'.format(child)
            else:
                logger.debug('partial_getter(): leaf: ' + child_name)
                child = '{{{0}}}'.format(child_name)
            partial = fmt.format(**{'partialname': child_name, 'partial': child})
            yield partial


def get_spec(name, root):
    logger.debug('+++++++++++++++++++++++ get_spec() ++++++++++++++++++++++++++++++1')
    logger.debug('get_spec(): name: {}'.format(name))
    logger.debug('get_spec(): root[{}]: {}'.format(name, root[name]))
    ancestors = [root[name]] + [anc for anc in inheritor(root[name], root) if anc]
    logger.debug('get_spec(): ancestors: {}'.format(
        yamldump(ancestors)))
    if not ancestors:
        return ordereddict()
    spec = deepcopy(ancestors[-1])
    for ancestor in reversed(ancestors):
        for key, value in ancestor.items():
            value_copy = deepcopy(value)
            if isinstance(value, dict) and 'inherit' in value:
                spec.setdefault(key, CommentedMap())
                spec[key].update(value_copy)
                del spec[key]['inherit']
            else:
                spec[key] = value_copy
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


def build_page_assets(source_dir, target_dir):
    for asset in source_dir.visit(fil='*.css'):
        logger.info('Get asset {} from {}'.format(
            target_dir.relto(target_dir).join(asset.basename), 
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
        for content_group, content_dir in content_dir_getter(site, self.site_dir):
            for page_root, rel_page_path in page_path_getter(content_group, content_dir):
                build_page(page_root, rel_page_path, self.build_dir, site)
