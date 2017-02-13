import logging

from . import orderedyaml
from .orderedyaml import CommentedMap
from .utils import find_path

logger = logging.getLogger(__name__)


def load_specs(basename, locations=None):
    filepath = find_path(basename, locations=locations)
    logger.debug('Load specs %r: %s' % (basename, filepath))
    if filepath:
        data = orderedyaml.load(filepath).commented_map
    else:
        data = CommentedMap()
    return data


