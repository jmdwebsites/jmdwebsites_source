import logging

from .spec import ensure_spec

logger = logging.getLogger(__name__)


class DataObj:
    def __init__(self, data_spec):
        self.__dict__.update(**data_spec)


def get_data(spec):
    logger.debug("Get 'data' from spec")
    spec = ensure_spec(spec, ('data',))
    data = spec['data']
    return data


def get_object(spec):
    logger.debug("Get 'object' from spec")
    spec = ensure_spec(spec, ('object',))
    object = spec['object']
    return DataObj(object)
