import logging

from . import html
from .content import get_content, merge_content
from .data import get_data, get_object
from .error import JmdwebsitesError
from .log import WRAPPER, WRAPPER_NL
from .orderedyaml import OrderedYaml, CommentedMap
from .spec import get_spec, spec_walker
from .template import get_template

class PageError(JmdwebsitesError): pass
class SourceDirNotFoundError(PageError): pass
class NotFoundError(PageError): pass

logger = logging.getLogger(__name__)


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
    for path, root, key, value in spec_walker(page_spec):
        if value == 'navlink' and page_spec['navlinks'][key] == url:
            logger.debug('Change %r navlink to activenavlink', key)
            root[key] = 'activenavlink'

    logger.debug('Show compiled page spec %r for url %r:' + WRAPPER,
        page_spec_name, url, OrderedYaml(page_spec))

    page_spec['vars']['url'] = url

    return page_spec


def get_html(source_dir, page_spec):
    if not source_dir.check(dir=1):
        raise SourceDirNotFoundError(
            'Source dir not found: {}'.format(source_dir))
    logger.debug("Source data is in %s", source_dir)
    html_text = html.load(source_dir)
    if html_text is None:
        # No source file detected, so use a template and content partials.
        template = get_template(page_spec)
        page_content = get_content(source_dir)
        page_content = merge_content(page_content, page_spec)
        data = get_data(page_spec)
        object = get_object(page_spec)
        html_text = render_html(template, page_content, object=object)
    return html_text


def render_html(template, content, object=None, j2=False, **kwargs):
    logger.debug("Render html using template and content")
    #rendered_html = render(template, content, **kwargs)
    try:
        rendered_html = template.format(object=object, **content)
        # Second pass, to catch variables in content partials
        rendered_html = rendered_html.format(object=object, **content)
    except KeyError as e:
        raise NotFoundError('Missing content: {}'.format(e))
    assert isinstance(rendered_html, unicode)
    logger.debug('Rendered html:' + WRAPPER, rendered_html)
    pretty_html = html.prettify(rendered_html)
    logger.debug('Pretty html:' + WRAPPER_NL, pretty_html)
    return pretty_html

