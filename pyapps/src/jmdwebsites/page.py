import logging

from jmdwebsites import html
from jmdwebsites.template import get_template
from jmdwebsites.data import get_data, get_object
from jmdwebsites.content import get_content, merge_content
from jmdwebsites.log import WRAPPER, WRAPPER_NL
from jmdwebsites.error import JmdwebsitesError

class PageError(JmdwebsitesError): pass
class SourceDirNotFoundError(PageError): pass
class NotFoundError(PageError): pass

logger = logging.getLogger(__name__)


def get_html(source_dir, page_spec):
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
        data = get_data(page_spec)
        object = get_object(page_spec)
        html_text = render_html(template, page_content, object=object)
    return html_text


def render_html(template, content, **kwargs):
    logger.debug("Render html using template and content")
    rendered_html = render(template, content, **kwargs)
    pretty_html = html.prettify(rendered_html)
    logger.debug('Rendered html:' + WRAPPER_NL, pretty_html)
    return pretty_html


def render(template, content, object=None, j2=False, **kwargs):
    if j2:
        template = jinja2.Template(template)
        assert 0, "TODO:"
        #TODO:
        #rendered_output = template.render(data=data, **content)
        return
    try:
        rendered_output = template.format(object=object, **content)
        # Second pass, to catch variables in content partials
        rendered_output = rendered_output.format(object=object, **content)
    except KeyError as e:
        raise NotFoundError('Missing content: {}'.format(e))
    assert isinstance(rendered_output, unicode)
    logger.debug('Rendered output:' + WRAPPER, rendered_output)
    return rendered_output


