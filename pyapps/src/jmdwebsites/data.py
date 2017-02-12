import logging

#from .orderedyaml import OrderedYaml
from .spec import ensure_spec

logger = logging.getLogger(__name__)

class PageData():
    def __init__(self):
        # Use this as test data to check mechanism 
        # for passing in data to template/content works
        self.stats = 'Stats=56%'


class DataObj:
    def __init__(self, data_spec):
        self.__dict__.update(**data_spec)

def get_data(spec):
    logger.debug("Get 'data' from spec")
    spec = ensure_spec(spec, ['data'])
    #data = PageData()
    data = spec['data']
    data['stats'] = 'Stats=56%'

    #print('==========') 
    #print(OrderedYaml(data))
    #assert 0

    return data

def get_object(spec):
    logger.debug("Get 'object' from spec")
    spec = ensure_spec(spec, ['object'])
    object = spec['object']
    return DataObj(object)
