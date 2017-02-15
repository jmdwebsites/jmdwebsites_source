from __future__ import print_function

import py
import ruamel
from ruamel.yaml.comments import CommentedMap, CommentedSeq, ordereddict
import six


class OrderedYaml(object):

    def __init__(self, data=None):
        if data is None:
            self.commented_map = CommentedMap()
        elif isinstance(data, (CommentedMap, CommentedSeq)):
            self.commented_map = data
        elif isinstance(data, six.string_types):
            self.load(data)
        else:
            self.load(dump(data))
    
    def __unicode__(self):
        return self.dump().decode('utf-8')

    def __str__(self):
        return self.dump()

    def __repr__(self):
        return repr(self.__unicode__())

    def load(self, stream, Loader=ruamel.yaml.RoundTripLoader, **kwargs):
        '''Convert a YAML document to a Python object. 
        
        A byte string or a file must be encoded with utf-8, utf-16-be or 
        utf-16-le encoding. The encoding is detected by checking the 
        BOM (byte order mark) sequence at the beginning of the string/file. 
        If no BOM is present, utf-8 encoding is assumed.
        '''
        if isinstance(stream, py._path.local.LocalPath):
            with stream.open() as fileobj:
                self.commented_map = ruamel.yaml.load(fileobj, Loader=Loader, **kwargs)
        else:
            self.commented_map = ruamel.yaml.load(stream, Loader=Loader, **kwargs)
        return self
        
    def dump(self, stream=None):
        return ruamel.yaml.dump(
            self.commented_map, 
            stream,
            Dumper=ruamel.yaml.RoundTripDumper, 
            allow_unicode=True, 
            default_flow_style=False)


def load(stream, **kwargs):
    return OrderedYaml().load(stream, **kwargs)


def dump(data, stream=None, **kwargs):
    return ruamel.yaml.dump(
        data,
        stream,
        Dumper=ruamel.yaml.RoundTripDumper, 
        allow_unicode=True, 
        default_flow_style=False)
    
