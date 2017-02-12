import logging

import bs4 as bs

logger = logging.getLogger(__name__)

class HtmlPageError(Exception): pass
class CharsetError(HtmlPageError): pass
class DoctypeError(HtmlPageError): pass

class HtmlPage(object):
    def __init__(self, html, parser='html5lib'):
        self.soup = bs.BeautifulSoup(html, parser)

    def doctype(self):
        '''Get the doctype.
        
        There should be just one doctype, 
        and it should be the first item in the soup contents.
        '''
        doctype = self.soup.contents[0]
        if len([t for t in self.soup.contents if isinstance(t, bs.Doctype)]) > 1: 
            raise DoctypeError(
                'More than one doctype')
        if isinstance(doctype, bs.Doctype):
            return doctype
        # By default, return None to indicate no doctype found

    def charset(self):
        '''Get the charset definition from the page.
        
        The charset should be the first meta tag in head tag.
        '''
        first_tag = self.soup.html.head.find(True)
        if not ((first_tag.name == 'meta') and first_tag.has_attr('charset')):
            raise CharsetError(
                "First tag in <head>: {}: charset not defined".format(first_tag.name))
        return first_tag['charset']

    def check_page(self):
        assert 0