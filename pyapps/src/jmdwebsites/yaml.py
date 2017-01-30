from __future__ import print_function

import ruamel


#TODO: Review all this. Not tested yet. Didnt need in the end
def construct_yaml_str(self, node):
    print(repr(node))
    if node.tag == 'tag:yaml.org,2002:str':
        #node.value = unicode(node.value)
        if not isinstance(node.value, unicode):
            assert 0
    return self.construct_scalar(node)

def construct_yaml_python_str(self, node):
    assert 0


def add_contructors():
    ruamel.yaml.RoundTripLoader.add_constructor(u'tag:yaml.org,2002:str', construct_yaml_str)
    ruamel.yaml.RoundTripLoader.add_constructor(u'tag:yaml.org,2002:python/str', construct_yaml_python_str)


#add_contructors()