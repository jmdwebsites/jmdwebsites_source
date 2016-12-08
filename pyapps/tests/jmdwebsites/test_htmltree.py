import pytest
from jmdwebsites import HtmlTree
import logging

logger = logging.getLogger(__name__)

@pytest.mark.parametrize("html, expected_doctype", [
    ('Good', None),
    ('<!doctype html><html>Hello</html>', 'html'),
    ('<!doctype xml><!doctype html>Good', 'xml'),
    ('Hello\n<!doctype html><html>Good</html>', None)
])
def test_doctype(html, expected_doctype):
    html_tree = HtmlTree(html)
    doctype = html_tree.doctype()
    #assert doctype == expected_doctype, 'Incorrect doctype {} expected {}'.format(doctype, expected_doctype)
    assert doctype == expected_doctype, 'Incorrect doctype'

@pytest.mark.parametrize("html, expected_charset", [
(u'''<!doctype html><html>
  <head>
    <meta charset='utf-8' />
    <meta der='utf-8' />
  </head>
  <body>Hello</body></html>
''', 'utf-8')
])
def test_assert_charset(html, expected_charset):
    HtmlTree(html).assert_charset(expected_charset)
    assert HtmlTree(html).charset(expected_charset) == expected_charset

@pytest.mark.parametrize("html_page, expected_charset", [(
HtmlTree('''<!doctype html><html>
  <head>
    <meta charset='utf-8' />
    <meta der='utf-8' />
  </head>
  <body>Hello</body></html>
'''), 'utf-8')
])
def test_charset(html_page, expected_charset):
    '''Get the charset definition from the page.
    
    The charset should be the first meta tag in head tag.
    '''
    first_tag = html_page.soup.head.find(True)
    assert first_tag.name == 'meta' and first_tag.has_attr('charset'), \
        "First tag in <head>: {}: charset not defined".format(first_tag.name)
    assert first_tag['charset'] == expected_charset, \
        "charset: {}: Incorrect charset, expected {}".format(first_tag['charset'], expected_charset)


# Prove that a test is skipped when no test data is supplied
@pytest.mark.parametrize("test_data", [
    #('Good', 'expected'),
])
def test_something(test_data):
    input_data, expected_result = test_data
    print("!!! TEST SOMETHING input={} expected={}".format(input_data, expected_result))
    
