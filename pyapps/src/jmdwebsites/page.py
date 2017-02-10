import logging

from jmdwebsites import html
from jmdwebsites.template import get_template
from jmdwebsites.content import get_content, merge_content
from jmdwebsites.log import WRAPPER, WRAPPER_NL
from jmdwebsites.error import JmdwebsitesError

class PageError(JmdwebsitesError): pass
class SourceDirNotFoundError(PageError): pass
class NotFoundError(PageError): pass

logger = logging.getLogger(__name__)


def get_html(source_dir, page_spec, data=None):
    if not source_dir.check(dir=1):
        raise SourceDirNotFoundError(
            'Source dir not found: {}'.format(source_dir))
    logger.debug("Source data is in %s", source_dir)
    html_text = html.get_index_page(source_dir)
    if html_text is None:
        # No source file detected, so use a template and content partials.
        template = get_template(page_spec)
        page_content = get_content(source_dir)
        page_content = merge_content(page_content, page_spec)
        html_text = render_html(template, page_content, data=data)
    return html_text


def render_html(template, content, **kwargs):
    logger.debug("Render html using template and content")
    rendered_html = render(template, content, **kwargs)
    pretty_html = html.prettify(rendered_html)
    logger.debug('Rendered html:' + WRAPPER_NL, pretty_html)
    return pretty_html


def render(template, content, data=None, j2=False, **kwargs):
    if j2:
        template = jinja2.Template(template)
        assert 0, "TODO:"
        #TODO:
        #rendered_output = template.render(data=data, **content)
        return
    try:
        rendered_output = template.format(data=data, **content)
        # Second pass, to catch variables in content partials
        rendered_output = rendered_output.format(data=data, **content)
    except KeyError as e:
        raise NotFoundError('Missing content: {}'.format(e))
    assert isinstance(rendered_output, unicode)
    #rendered_output = ensure_unicode(rendered_output)
    logger.debug('Rendered output:' + WRAPPER, rendered_output)
    return rendered_output


