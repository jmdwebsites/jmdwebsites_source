from __future__ import print_function

import py
import pytest

from jmdwebsites.orderedyaml import OrderedYaml


def datapath(stem):
    return py.path.local(__file__).dirpath('data', stem)


expected_yaml_output = '''\
/:
  blog:
    /first-post:
  about:
    tmp.html:
  contact:
'''
@pytest.mark.parametrize("inputfile, expected", [
    (
        datapath('test_yaml/simple.yaml'),
        expected_yaml_output
    )
])
class TestYaml:
    def test_init(self, inputfile, expected):
        yml = OrderedYaml()
        yml.load(inputfile.read_text(encoding='MacRoman'))
        print('---------------1--')
        print(repr(yml.dump()))
        print('---------------2--')
        print(repr(expected))
        print('---------------3--')
        assert yml.dump() == expected
        print(yml)
        print('---------------4--')
        print(repr(yml))
