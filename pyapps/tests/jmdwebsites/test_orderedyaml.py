from __future__ import print_function

import pytest
from six import string_types

from jmdwebsites.content import get_vars
from jmdwebsites.orderedyaml import OrderedYaml, CommentedMap, dump, load

from .generic_test_data import spec


@pytest.mark.parametrize("data", [
    spec
])
def test_dump_and_load(data):
    assert isinstance(spec, CommentedMap)
    dumped = dump(spec)
    assert isinstance(dumped, string_types)
    loaded = load(dumped)
    assert isinstance(loaded, OrderedYaml)
    assert isinstance(loaded.commented_map, CommentedMap)
    assert loaded.commented_map == spec
    
