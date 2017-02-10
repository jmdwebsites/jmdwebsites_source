from copy import copy
import logging

import mistune
import six

from jmdwebsites.spec import ensure_spec
from jmdwebsites.log import WRAPPER
from jmdwebsites.orderedyaml import OrderedYaml
from jmdwebsites.error import JmdwebsitesError

class ContentError(JmdwebsitesError): pass
class MissingVarsError(ContentError): pass
class FileFilterError(ContentError): pass
class MissingContentError(ContentError): pass
class ContentFileError(ContentError): pass
class UnusedContentError(ContentError): pass

logger = logging.getLogger(__name__)


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


def get_vars(vars):
    logger.debug('vars: %s', vars.keys())
    missing_vars = {var:value for var, value in vars.items() if value is None}
    if missing_vars:
        raise MissingVarsError('Not found: {}'.format(missing_vars.keys()))
    return vars


def get_content(source_dir,
                fil=FileFilter('_', ['.html','.md']),
                markdown=mistune.Markdown()):
    logger.debug('Get content from %s', source_dir)
    source_content = {}
    for path in source_dir.visit(fil=fil):
        part_name = path.purebasename.lstrip('_')
        text = path.read_text(encoding='utf-8')
        if path.ext == '.html':
            html = text
        elif path.ext == '.md':
            html = markdown(text)
        else:
            raise ContentFileError('Invalid file type: {}'.format(path), 2)
        source_content[part_name] = html
    return source_content


def merge_content(source_content, spec=None):
    spec = ensure_spec(spec, ['content', 'vars', 'navlinks'])
    missing_content = {key:value for key, value in spec['content'].items() if value is None and key not in source_content}
    if missing_content:
        raise MissingContentError('Not found: {}'.format(missing_content.keys()))
    unused_content = [key for key in source_content if key not in spec['content']]
    if unused_content:
        raise UnusedContentError('Unused content: {}'.format(unused_content))

    vars = get_vars(spec['vars'])

    content = copy(spec['content'])
    logger.debug('content: %s: Initilized with default content from spec', content.keys())

    content.update(source_content)
    logger.debug('content: %s: Updated with source content', content.keys())

    content.update(vars)
    logger.debug('content: %s: Updated with vars', content.keys())

    if 'navlinks' in spec:
        content.update(spec['navlinks'])
        logger.debug('content: %s: Updated with navlinks', content.keys())
    logger.debug('content:' + WRAPPER, OrderedYaml(content))

    return content


