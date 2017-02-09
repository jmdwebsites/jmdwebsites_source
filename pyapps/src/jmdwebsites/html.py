from __future__  import print_function
import logging
import re

from bs4 import BeautifulSoup

onespace_regexp = re.compile(r'^(\s*)', re.MULTILINE)

logger = logging.getLogger(__name__)


class MyBeautifulSoup(BeautifulSoup):
    def __init__(self, html_doc, html_parser, *args, **kwargs):
        BeautifulSoup.__init__(self, html_doc, html_parser, *args, **kwargs)
        # html5lib adds a head, html and body to docs without them, 
        # so remove if not in original doc
        if html_parser == 'html5lib':
            if html_doc.find('<head') < 0:
                self.find('head').decompose()
            if html_doc.find('<html') < 0:
                self.find('html').unwrap()
            if html_doc.find('<body') < 0:
                self.find('body').unwrap()


def prettify(html_doc, start_tag_name=None, partial=False, indent=2):
    if partial:
        soup = MyBeautifulSoup(html_doc, 'html5lib')
    else:
        soup = BeautifulSoup(html_doc, 'html5lib')
    if indent == 0 or indent > 1:
        indent = r''.join(r'\1' for n in range(indent))
        return onespace_regexp.sub(indent, soup.prettify())
    else:
        return soup.prettify()


def get_index_page(source_dir):
    #TODO: Decide how to handle index.php files
    filepath = source_dir.join('index.html')
    if filepath.check(file=1):
        logger.debug("Get html index page %s", filepath)
        html_text = filepath.read_text(encoding='utf-8') 
        #TODO: Validate that the file is unicode and that the html is ok
        #      May need to check charset and reload with different encoding
        return html_text
    return None
