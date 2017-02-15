from __future__ import print_function

import pytest
from six import string_types

from jmdwebsites.content import get_vars
from jmdwebsites.orderedyaml import OrderedYaml, CommentedMap, CommentedSeq,\
                                    dump, load

from .generic_test_data import spec


@pytest.mark.parametrize("data", [
    spec
])
def test_dump_and_load(data):
    assert isinstance(data, CommentedMap)
    dumped = dump(spec)
    assert isinstance(dumped, string_types)
    loaded = load(dumped)
    assert isinstance(loaded, OrderedYaml)
    assert isinstance(loaded.commented_map, CommentedMap)
    assert loaded.commented_map == data
    

class TestOrderedYaml:

    def test_init_with_no_parameter(self):
        data = None
        data = OrderedYaml()
        assert isinstance(data.commented_map, CommentedMap)
        assert data.commented_map == CommentedMap()

    @pytest.mark.parametrize("data, expected_type, expected", [
        (None, CommentedMap, CommentedMap()),
        ("Hello", string_types, "Hello"),
        (u"Goodbye", string_types, "Goodbye"),
        ("- listitem", CommentedSeq, (['listitem'])),
        ("key: 2", CommentedMap, CommentedMap([('key', 2)])),
        (spec, CommentedMap, spec)
    ])
    def test_init_with_parameters(self, data, expected_type, expected):
        ordered_yaml = None
        ordered_yaml = OrderedYaml(data)
        assert isinstance(ordered_yaml.commented_map, expected_type)
        assert ordered_yaml.commented_map == expected

    @pytest.mark.parametrize("data", [
        spec
    ])
    def test_dump_and_load(self, data):
        assert isinstance(data, CommentedMap)
        #ordered_yaml = OrderedYaml(data)
        dumped = OrderedYaml(data).dump()
        assert isinstance(dumped, string_types)
        loaded = OrderedYaml().load(dumped)
        assert isinstance(loaded, OrderedYaml)
        assert isinstance(loaded.commented_map, CommentedMap)
        assert loaded.commented_map == data

    @pytest.mark.parametrize("data", [
        "key1: 1\nkey2:\n- item1\n- item2\n"
    ])
    def test_str_repr_unicode(self, data):
        ordered_yaml = OrderedYaml(data)
        assert isinstance(ordered_yaml.commented_map, CommentedMap)
        assert isinstance(str(ordered_yaml), str)
        assert isinstance(repr(ordered_yaml), str)
        assert isinstance(unicode(ordered_yaml), unicode)
        assert repr(ordered_yaml) == repr(unicode(data))
        assert unicode(ordered_yaml) == unicode(data)
        assert str(ordered_yaml) == data
