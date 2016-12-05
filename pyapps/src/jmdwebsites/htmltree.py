import bs4 as bs
import logging

logger = logging.getLogger(__name__)

class HtmlTreeError(Exception):
    pass

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