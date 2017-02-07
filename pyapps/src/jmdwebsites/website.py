from __future__ import print_function

from copy import copy, deepcopy
import logging
import os
import platform
from pprint import pformat

import jinja2
import mistune
import py
import six


from jmdwebsites.log import dbgdump, yamldump
from jmdwebsites.html import prettify
from jmdwebsites import orderedyaml
from orderedyaml import OrderedYaml, CommentedMap

logger = logging.getLogger(__name__)

BUILD = 'build'
CONTENT = 'content'
CONTENT_GROUP = 'content_group'
CONFIG_FILE = 'site.yaml'
THEME_FILE = 'theme.yaml'
PAGE_SPECS_FILE = 'pagespecs.yaml'
PROJDIR = '.jmdwebsite'
HOME = 'home'
PAGES = 'pages'
POSTS = 'posts'
DEBUG_SEPARATOR = '%%' * 60 + ' %s ' + '%%' * 60

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
class ThemeNotFoundError(WebsiteError): pass


def ensure_unicode(text):
    print('ensure_unicode:', type(text), repr(text))
    #assert isinstance(text, unicode)
    #TODO: Review how to ensure unicode
    return unicode(text)


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
    logger.info('Remove %s', path)
    path.remove()


def load(filepath):
    if filepath.check(file=1):
        system_platform = platform.system()
        if system_platform == 'Darwin':
            encoding='MacRoman'
        elif system_platform == 'Windows':
            encoding='windows-1252'
        elif system_platform == 'Linux':
            encoding='ISO-8859-1'
        else:
            encoding='utf-8'
        data = filepath.read_text(encoding=encoding)  #Dont need this for the yaml case
        if filepath.ext == '.yaml':
            yaml = orderedyaml.load(data)
            data = yaml.commented_map
            logger.debug('Load data from %s: %s', filepath, yaml)
        else:
            data_dump = dbgdump(data)
            logger.debug('Load data from %s: %s', filepath, data_dump)
    else:
        raise FileNotFoundError('Not found: {}'.format(filepath))
    return data


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


def new_website(site_dirname = ''):
    """New website."""
    site_dir = py.path.local(site_dirname)
    logger.info('Create new website %s', site_dir.strpath)
    if site_dir.check():
        raise PathAlreadyExists(
            'Already exists: {}'.format(site_dir))
    site_dir.ensure( PROJDIR)
    logger.error('TODO:')


def init_website():
    """Initialize website."""
    site_dir = py.path.local()
    logger.info('Init website %s', site_dir.strpath)
    project_dir = py.path.local( PROJDIR)
    if project_dir.check():
        raise WebsiteProjectAlreadyExists(
            'Website project already exists: {}'.format(project_dir))
    logger.info('Create proj dir %s', project_dir.strpath)
    project_dir.ensure(dir=1)
    site_dir.ensure(CONFIG_FILE)


def content_dir_getter(site, site_dir):
    site = ensure_spec(site, [])
    if CONTENT_GROUP in site:
        for content_group, dirname in site[CONTENT_GROUP].items():
            if content_group not in set([HOME, PAGES, POSTS]):
                raise InvalidContentGroupError(
                    'Invalid content group: {}'.format(content_group))
            if dirname is None:
                dirname = os.path.join(CONTENT, content_group)
            yield content_group, site_dir.join(dirname)
    else:
        root, dirs, files = next(os.walk(site_dir.join(CONTENT).strpath))
        for content_group in dirs: 
            yield content_group, site_dir.join(CONTENT, content_group)


def page_path_getter(content_group, content_dir):
    logger.info('Build content: %s: %s', content_group, content_dir)
    if content_group == HOME:
        yield content_dir, ''
    else:
        for page_path in content_dir.visit(fil=isdir):
            yield content_dir, page_path.relto(content_dir)


def get_url(rel_page_path):
    #TODO: Check site config to get slugs and relpagepath to url mappings.
    url = os.path.join('/', rel_page_path)
    return url


class Info():
    def __init__(self, url):
        self.url = url


def build_html_file(html, target_dir):
    target_file = target_dir.join('index.html') 
    target_file.write_text(html, ensure=True, encoding='utf-8')


def get_html(source_dir, page_spec, info=None):
    #TODO: Decide how to handle index.php files
    source_file = source_dir.join('index.html')
    if source_file.check():
        logger.debug("Get html source file %s", source_file)
        html = load(source_file)
        logger.debug('Validate source file: %s', source_file)
        #TODO: Validate that the file is unicode and that the html is ok
    else:
        # No source file detected, so use a template and content partials.
        template = get_template(page_spec)
        content = get_content(source_dir, page_spec, fil=FileFilter('_', ['.html','.md']), info=info)
        html = render_html(template, content, info=info)
    return html


def get_page_spec(url, site_specs, theme_specs):
    specs = CommentedMap()
    if isinstance(theme_specs, dict):
        specs.update(theme_specs)
    if isinstance(site_specs, dict):
        specs.update(site_specs)

    try:
        page_specs = specs['pages']
    except (KeyError, TypeError):
        return None

    if url in page_specs:
        page_spec_name = url
    elif 'page' in page_specs:
        page_spec_name = 'page'
    else:
        page_spec_name = 'default'
    logger.debug('Get subspec: %s: %s', repr('pages'), repr(page_spec_name))

    raw_page_spec = get_spec(page_spec_name, page_specs)
    
    page_spec = CommentedMap()
    for type_, name in raw_page_spec.items():
        logger.debug('Get subspec: %s: %s', repr(type_), repr(name))
        page_spec[type_] = get_spec(name, specs[type_])

    # Active nav links
    for path, root, key, value in dict_walker(page_spec):
        if value == 'navlink' and page_spec['navlinks'][key] == url:
            logger.debug('Change %s navlink to activenavlink', repr(key))
            root[key] = 'activenavlink'

    logger.debug('Show compiled page spec %s for url %s: %s',
        repr(page_spec_name), repr(url), yamldump(page_spec))

    return page_spec


def render_html(template, content, **kwargs):
    logger.debug("Render html using template and content")
    rendered = render(template, content, **kwargs)
    html = prettify(rendered)
    logger.debug('Rendered html: %s', dbgdump(html))
    return html


def render(template, content, info=None, j2=False, **kwargs):
    if j2:
        template = jinja2.Template(template)
        assert 0, "TODO:"
        #TODO:
        #rendered_output = template.render(info=info, **content)
    try:
        rendered_output = template.format(info=info, **content)
        rendered_output = ensure_unicode(rendered_output)
    except KeyError as e:
        raise NotFoundError('Missing content: {}'.format(e))
    logger.debug('Rendered output: %s', dbgdump(rendered_output))
    return rendered_output


def ensure_spec(spec, names=['content_group', 'content', 'layouts', 'partials', 'vars', 'navlinks']):
    names = set(names)
    if spec is None:
        logger.warning('No spec: spec: %s', repr(spec))
        spec = CommentedMap()
    for name in names:
        try:
            _subspec = spec[name]
        except TypeError:
            logger.warning('Invalid spec type: spec: %s', repr(spec))
            spec = CommentedMap()
            spec[name] = CommentedMap()
            raise TypeError
        except KeyError:
            logger.warning('Not found in spec: %s', repr(name))
            spec[name] = CommentedMap()
    return spec


def get_content(source_dir, spec=None, info=None, fil=None):
    logger.debug('Get content from %s', source_dir)
    spec = ensure_spec(spec, ['content', 'vars', 'navlinks'])
        
    source_content = get_source_content(source_dir, fil=fil)

    missing_content = {key:value for key, value in spec['content'].items() if value is None and key not in source_content}
    if missing_content:
        raise MissingContentError('Not found: {}'.format(missing_content.keys()))
    unused_content = [key for key in source_content if key not in spec['content']]
    if unused_content:
        raise UnusedContentError('Unused content: {}'.format(unused_content))

    vars = get_vars(spec['vars'])

    content = copy(spec['content'])
    if info:
        for key, value in content.items():
            content[key] = value.format(info=info)
    logger.debug('content: %s: Initilized with default content from spec', content.keys())

    content.update(source_content)
    logger.debug('content: %s: Updated with source content', content.keys())

    content.update(vars)
    logger.debug('content: %s: Updated with vars', content.keys())

    if 'navlinks' in spec:
        content.update(spec['navlinks'])
        logger.debug('content: %s: Updated with navlinks', content.keys())

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
    logger.debug('vars: %s', vars.keys())
    missing_vars = {var:value for var, value in vars.items() if value is None}
    if missing_vars:
        raise MissingVarsError('Not found: {}'.format(missing_vars.keys()))
    return vars


def get_template(spec, name='doc'):
    logger.debug('Create template from spec')
    template = u'\n'.join(partial_getter(spec))
    template = ensure_unicode(template)
    logger.debug('Show template: %s', dbgdump(template))
    template = ensure_unicode(template)
    return template


def partial_getter(spec, name='doc'):
    spec = ensure_spec(spec, ['layouts', 'partials'])
    layouts = spec['layouts']
    try:
        top = layouts[name]
    except KeyError:
        return
    logger.debug('Get partial: stem: %s', name)
    if top:
        for child_name, partial_name in top.items():
            if partial_name is None:
                partial_name = child_name
            try:
                fmt = spec['partials'][partial_name]
                fmt = ensure_unicode(fmt)
            except KeyError:
                raise PartialNotFoundError('Partial not found: {}'.format(partial_name))
            if child_name in layouts and layouts[child_name]:
                child = u'\n'.join(partial_getter(spec, name=child_name))
                child = u'\n{}\n'.format(child)
            else:
                logger.debug('Get partial: leaf: %s', child_name)
                child = u'{{{0}}}'.format(child_name)
            fmt = ensure_unicode(fmt)
            child_name = ensure_unicode(child_name)
            child = ensure_unicode(child)
            partial = fmt.format(**{'partialname': child_name, 'partial': child})
            yield partial


def get_spec(name, root):
    ancestors = [root[name]] + [anc for anc in inheritor(root[name], root) if anc]
    logger.debug('Inheritance: %s', yamldump(ancestors))
    if not ancestors:
        return CommentedMap()
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
    for asset in source_dir.visit(fil=str('*.css')):
        logger.info('Get asset %s from %s',
            target_dir.relto(target_dir).join(asset.basename), 
            asset)
        asset.copy(target_dir)


class Website(object):
    def __init__(self, site_dir=None, build_dir=None):
        logger.debug('Create website: %s(site_dir=%s, build_dir=%s)',
            self.__class__.__name__, 
            repr(site_dir),
            repr(build_dir))
        if site_dir is None:
            self.site_dir = get_project_dir()
        else:
            self.site_dir = py.path.local(site_dir)
        logger.info('Site root directory: %s', self.site_dir)
        if build_dir is None:
            self.build_dir = self.site_dir.join(BUILD)
        else:
            self.build_dir = py.path.local(build_dir)
        logger.info('Build website in %s', self.build_dir)
        self.site = self.get_specs(CONFIG_FILE)
        self.theme_dir, self.theme = self.get_theme()

    def get_fallback(self, basename):
        locations = [
            self.site_dir,  
            py.path.local(__file__).dirpath()
        ]
        for dirpath in locations:
            filepath = dirpath.join(basename)
            if filepath.check():
                break
        else:
            raise NotFoundError()
        return dirpath, filepath

    def get_theme(self):
        try:
            theme_name = self.site['theme']['name']
        except:
            logger.warning('%s: Theme not specified, use fallback', CONFIG_FILE)
            theme_dir, theme_file = self.get_fallback(THEME_FILE)
            logger.debug('Load theme from %s', theme_file)
        else:
            theme_dir = self.site_dir.join('themes', theme_name)
            theme_file = theme_dir.join(THEME_FILE)
            logger.debug('Load theme %s from %s', repr(theme_name), theme_file)
        theme = load(theme_file)
        return theme_dir, theme

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

        for content_group, content_dir in content_dir_getter(self.site, self.site_dir):
            for page_root, rel_page_path in page_path_getter(content_group, content_dir):
                self.build_page(page_root, rel_page_path)

        self.build_stylesheets()

    def get_specs(self, basename):
        locations = [
            self.site_dir,  
            py.path.local(__file__).dirpath()
        ]
        for dirpath in locations:
            filepath = dirpath.join(basename)
            try:
                data = load(filepath)
                break
            except FileNotFoundError:
                pass
        else:
            logger.warning('Not found: %s', basename)
            data = None
        return data

    def build_page(self, source_root, source_rel_path):
        url = get_url(source_rel_path)
        logger.debug(DEBUG_SEPARATOR, url)  # Mark page top
        logger.info("Build page: %s", url)
        source_dir = source_root.join(source_rel_path)
        if not source_dir.check(dir=1):
            raise SourceDirNotFoundError(
                'Source dir not found: {}'.format(source_dir))
        logger.debug("Source data is in %s", source_dir)
        target_dir = self.build_dir.join(url)
        page_spec = get_page_spec(url, self.site, self.theme)
        html = get_html(source_dir, page_spec, info=Info(url))
        build_html_file(html, target_dir)
        build_page_assets(source_dir, target_dir)

    def build_stylesheets(self):
        logger.info('Build stylesheets')
        src = self.theme_dir.join('stylesheets/page.scss')
        tgt = self.build_dir.join('page.css')
        sass_cmdline = "sass {0} {1}".format(src, tgt)
        os.system(sass_cmdline)
