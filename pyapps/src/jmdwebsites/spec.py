from copy import deepcopy
import logging
import os

from .orderedyaml import CommentedMap
from .log import WRAPPER
from .orderedyaml import OrderedYaml, CommentedMap
from .error import JmdwebsitesError

class SpecError(JmdwebsitesError): pass
class DictWalkerError(SpecError): pass
class AncestorNotFoundError(SpecError): pass

logger = logging.getLogger(__name__)


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


def ensure_spec(spec, names=('content_group', 'content', 'layouts', 'partials', 'vars', 'navlinks')):
    names = set(names)
    if spec is None:
        logger.warning('No spec: spec: %r', spec)
        spec = CommentedMap()
    for name in names:
        try:
            _subspec = spec[name]
        except TypeError:
            logger.warning('Invalid spec type: spec: %r', spec)
            spec = CommentedMap()
            spec[name] = CommentedMap()
            raise TypeError
        except KeyError:
            logger.warning('Not found in spec: %r', name)
            spec[name] = CommentedMap()
    return spec


def get_page_spec(url, site_spec, theme_spec, content_spec):
    specs = CommentedMap()
    if isinstance(theme_spec, dict):
        specs.update(theme_spec)
    if isinstance(site_spec, dict):
        specs.update(site_spec)
    if isinstance(content_spec, dict):
        specs.update(content_spec)

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
    logger.debug('Get subspec: %r: %r', 'pages', page_spec_name)

    raw_page_spec = get_spec(page_spec_name, page_specs)
    
    page_spec = CommentedMap()
    for type_, name in raw_page_spec.items():
        logger.debug('Get subspec: %r: %r', type_, name)
        page_spec[type_] = get_spec(name, specs[type_])

    # Active nav links
    for path, root, key, value in dict_walker(page_spec):
        if value == 'navlink' and page_spec['navlinks'][key] == url:
            logger.debug('Change %r navlink to activenavlink', key)
            root[key] = 'activenavlink'

    logger.debug('Show compiled page spec %r for url %r:' + WRAPPER,
        page_spec_name, url, OrderedYaml(page_spec))

    page_spec['vars']['url'] = url

    return page_spec


def get_spec(name, root):
    ancestors = [root[name]] + [anc for anc in inheritor(root[name], root) if anc]
    logger.debug('Inheritance:' + WRAPPER, OrderedYaml(ancestors))
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
