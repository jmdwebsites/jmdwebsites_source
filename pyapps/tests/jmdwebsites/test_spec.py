from __future__ import print_function

import pytest

import jmdwebsites


@pytest.mark.parametrize("config, expected", [
    (
        { '/': {'blog': {'/first-post': None}, 'contact': None, 'about':{'tmp.html': None }}},
        ['/', '/blog', '/first-post', '/about', '/about/tmp.html', '/contact']
    )
])
def test_spec_walker(config, expected):
    result = [path for path, root, key, value in jmdwebsites.spec.spec_walker(config)]
    assert result == expected


