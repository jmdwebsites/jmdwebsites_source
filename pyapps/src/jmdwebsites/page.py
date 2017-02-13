import logging

from . import html
from .content import get_content, merge_content
from .data import get_data, get_object
from .error import JmdwebsitesError
from .log import WRAPPER, WRAPPER_NL
from .template import get_template

class PageError(JmdwebsitesError): pass
class SourceDirNotFoundError(PageError): pass
class NotFoundError(PageError): pass

logger = logging.getLogger(__name__)


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

