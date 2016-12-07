import bs4 as bs
import logging

logger = logging.getLogger(__name__)

class HtmlTreeError(Exception): pass
class CharsetError(HtmlTreeError): pass

class HtmlTree(object):
    def __init__(self, html, parser='html5lib'):
        self.soup = bs.BeautifulSoup(html, parser)

    def doctype(self):
        '''Get the doctype.
        
        There should be just one doctype, 
        and it should be the first item in the soup contents.
        '''
        doctype = self.soup.contents[0]
        if len([t for t in self.soup.contents if isinstance(t, bs.Doctype)]) > 1: 
            raise HtmlTreeError('More than one doctype')
        if isinstance(doctype, bs.Doctype):
            return doctype
        # By default, return None to indicate no doctype found

    def assert_charset(self, expected):
        '''Get the charset definition from the page.
        
        The charset should be the first meta tag in head tag.
        '''
        first_tag = self.soup.head.find(True)
        assert first_tag.name == 'meta' and first_tag.has_attr('charset'), \
            "First tag in <head>: {}: charset not defined".format(first_tag.name)
        assert first_tag['charset'] == expected, \
            "charset: {}: Incorrect charset, expected {}".format(first_tag['charset'], expected)

    def charset(self, expected):
        first_tag = self.soup.head.find(True)
        if not ((first_tag.name == 'meta') and first_tag.has_attr('charset')):
            raise CharsetError("First tag in <head>: {}: charset not defined".format(first_tag.name))
        return first_tag['charset']
