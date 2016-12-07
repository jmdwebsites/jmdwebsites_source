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
def test_doctype(setup_test_session, html, expected_doctype):
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
def test_assert_charset(setup_test_session, html, expected_charset):
    HtmlTree(html).assert_charset(expected_charset)
    assert HtmlTree(html).charset(expected_charset) == expected_charset
