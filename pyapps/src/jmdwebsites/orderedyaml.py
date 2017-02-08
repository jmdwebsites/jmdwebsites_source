from __future__ import print_function

import ruamel
from ruamel.yaml.comments import CommentedMap


class OrderedYaml(object):

    def __init__(self, commented_map=None):
        if commented_map is None:
            self.commented_map = CommentedMap()
        else:
            self.commented_map = commented_map
    
    def __unicode__(self):
        return self.dump().decode('utf-8')

    def __str__(self):
        return self.dump()

    def __repr__(self):
        return repr(self.__unicode__())

    def load(self, stream, Loader=ruamel.yaml.RoundTripLoader, **kwargs):
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
    
