from copy import deepcopy
import logging
import os

from .error import JmdwebsitesError
from .log import WRAPPER
from .orderedyaml import OrderedYaml, CommentedMap

class SpecError(JmdwebsitesError): pass
class SpecWalkerError(SpecError): pass
class AncestorNotFoundError(SpecError): pass

logger = logging.getLogger(__name__)


def spec_walker(parent, parent_path=''):
    if not isinstance(parent, dict):
        raise SpecWalkerError('Not a dictionary: {}'.format(root))
    for key, value in parent.items():
        path = os.path.join(parent_path, key)
        root = parent
        yield path, root, key, value
        if isinstance(value, dict):
            for path, root, key, value in spec_walker(value, parent_path=path):
                yield path, root, key, value


def ensure_spec(spec, names=None):
    names = set(names)
    if spec is None:
        logger.warning('No spec: %r', spec)
        spec = CommentedMap()
    if names is not None:
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
