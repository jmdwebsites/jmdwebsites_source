import pytest
from jmdwebsites import HtmlPage
import bs4 as bs


@pytest.mark.parametrize("html, expected_doctype, parser", [
    ('Good', None, 'html5lib'),
    ('<!doctype html><html>Hello</html>', 'html', 'html5lib'),
    ('<!doctype xml><!doctype html>Good', 'xml', 'html5lib'),
    ('Hello\n<!doctype html><html>Good</html>', None, 'html5lib')
])
def test_doctype(html, expected_doctype, parser):
    assert HtmlPage(html, parser).doctype() == expected_doctype, 'Incorrect doctype'


@pytest.mark.parametrize("html, expected_charset", [
(u'''<!doctype html><html>
  <head>
    <meta charset='utf-8' />
    <meta der='utf-8' />
  </head>
  <body>Hello</body></html>
''', 'utf-8')
])
def test_charset(html, expected_charset):
    charset = HtmlPage(html).charset()
    assert charset == expected_charset, \
        "charset: {}: Incorrect charset, expected {}".format(charset, expected_charset)


# Prove that a test is skipped when no test data is supplied
@pytest.mark.parametrize("test_data", [
    #('Good', 'expected'),
])
def test_something(test_data):
    input_data, expected_result = test_data
    print("!!! TEST SOMETHING input={} expected={}".format(input_data, expected_result))

    
if __name__ == "__main__":
    test_something((1,2))
