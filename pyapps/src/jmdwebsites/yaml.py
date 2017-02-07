from __future__ import print_function

import py
import ruamel
from ruamel.yaml.comments import CommentedMap
from ruamel.yaml.compat import ordereddict


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


def represent_yaml_str(self, data):
    rdata = self.represent_str(data)
    print('represent_yaml_str: ', repr(rdata))
    return self.represent_str(data.encode('utf-8'))
    #return self.represent_str(data)


def represent_yaml_unicode(self, data):
    rdata = self.represent_unicode(data)
    if rdata.tag == u'tag:yaml.org,2002:python/unicode':
        rdata = self.represent_str(data.encode('utf-8'))
    elif rdata.tag == u'tag:yaml.org,2002:str':
        pass
    else:
        raise Exception('YAML representer error: {}'.format(rdata.tag))
    print('represent_yaml_unicode: ', repr(rdata))
    return rdata
    #return self.represent_unicode(data)


def add_representers():
    ruamel.yaml.Dumper.add_representer(str, represent_yaml_str)
    ruamel.yaml.Dumper.add_representer(unicode, represent_yaml_unicode)
    # Not needed as RoundTripDumoer has own representers for string handling
    #ruamel.yaml.RoundTripDumper.add_representer(str, represent_yaml_str)
    #ruamel.yaml.RoundTripDumper.add_representer(unicode, represent_yaml_unicode)





