from __future__ import print_function

import pytest

from jmdwebsites.content import get_vars
from jmdwebsites.orderedyaml import CommentedMap

from .generic_test_data import spec
from .generic_test_data import vars as expected_vars
from .generic_test_data import data as expected_data

#from .generic_test_data import vars
#from .generic_test_data import data
#expected_vars = vars
#expected_data = data
#expected_vars = 1
#expected_data = 2

@pytest.mark.parametrize("spec, name, expected", [
    (spec, 'vars', expected_vars),
    (spec, 'data', expected_data)
])
def test_get_vars(spec, name, expected):
    vars = get_vars(spec, name)
    assert  isinstance(vars, CommentedMap)
    assert vars == expected
