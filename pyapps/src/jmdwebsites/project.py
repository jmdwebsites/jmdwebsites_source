import logging
import os

import py

from . import orderedyaml
from .error import JmdwebsitesError, PathNotFoundError
from .orderedyaml import CommentedMap
from .utils import find_path

logger = logging.getLogger(__name__)


class ProjectError(JmdwebsitesError): pass
# For get_project_dir()
class ProjectNotFoundError(ProjectError): pass
# For protected_remove()
class ProtectedRemoveError(ProjectError): pass
class PathNotAllowedError(ProtectedRemoveError): pass
class BasenameNotAllowedError(ProtectedRemoveError): pass
class PathAlreadyExists(ProjectError): pass
class WebsiteProjectAlreadyExists(ProjectError): pass


def load_specs(basename, locations=None):
    try:
        filepath = find_path(basename, locations=locations)
    except PathNotFoundError as e:
        logger.warning('Load specs: %s' % e)
        data = CommentedMap()
    else:
        logger.info('Load specs: %s: %s' % (basename, filepath))
        data = orderedyaml.load(filepath).commented_map
    return data


def get_project_dir(basename):
    # Check for project file in this dir and ancestor dirs
    for dirpath in py.path.local().parts(reverse=True):
        for path in dirpath.listdir():
            if path.basename == basename:
                return path.dirpath()
    raise ProjectNotFoundError(
        'Not a project (or any parent directories): {} not found'.format(
            basename))

 
def protected_remove(path, valid_basenames=None, projectdir=None):
    if valid_basenames is None:
        valid_basenames = set(['build'])
    for disallowed in [os.getcwd(), __file__]:
        if path in py.path.local(disallowed).parts():
            raise PathNotAllowedError(
                'Remove: {}: Path not allowed, protecting: {}'.format(
                    path, 
                    disallowed))
    if valid_basenames is not None and path.basename not in valid_basenames:
        raise BasenameNotAllowedError(
            'Remove: {}: Basename not allowed: {}: Must be one of: {}'.format(
                path, 
                path.basename, 
                valid_basenames))
    if projectdir is not None:
        try:
            #Check that path has a .jmdwebsites file somewhere in one of its 
            #parent directories, thus indicating it is part of a website project.
            get_project_dir(projectdir)
        except ProjectNotFoundError as e:
            raise ProjectNotFoundError('Remove: {}'.format(e))
    if not path.check():
        raise PathNotFoundError(
            'Remove: Path not found: {}'.format(path))
    logger.info('Remove %s', path)
    path.remove()


def init_project(projdir):
    """Initialize project.
    """
    project_dir = py.path.local(projdir)
    if project_dir.check():
        raise WebsiteProjectAlreadyExists(
            'Project already exists: {}'.format(project_dir))
    logger.info('Create project %r: %s', projdir, project_dir.strpath)
    project_dir.ensure(dir=1)


def new_project(project_pathname):
    """New project.
    """
    project_path = py.path.local(project_pathname)
    logger.info('Create new project %s', project_path.strpath)
    if project_path.check():
        raise PathAlreadyExists(
            'Already exists: {}'.format(project_path))
    # Use ensure for the time-being
    project_path.ensure(dir=1)
    logger.error('TODO:')
