import logging

from jmdwebsites.spec import ensure_spec
from jmdwebsites.log import WRAPPER
from jmdwebsites.error import JmdwebsitesError

class TemplateError(JmdwebsitesError): pass
class PartialNotFoundError(TemplateError): pass

logger = logging.getLogger(__name__)


def ensure_unicode(text):
    #print('ensure_unicode:', type(text), repr(text))
    #assert isinstance(text, unicode)
    #TODO: Review how to ensure unicode
    return unicode(text)


def get_template(spec, name='doc'):
    logger.debug('Create template from spec')
    template = u'\n'.join(partial_getter(spec)) + u'\n'
    template = ensure_unicode(template)
    logger.debug('Show template:' + WRAPPER, template)
    template = ensure_unicode(template)
    return template


def description(name, spec):
    spec = ensure_spec(spec, ('descriptions',))

    if 1 or name == 'About us':
        from .orderedyaml import OrderedYaml
        #print('+++++++++++++++')
        #print(OrderedYaml(spec))
        #print('+++++++++++++++')
        #logger.info('NAME>> %r', name)
        #assert 0

    if name in spec['descriptions']:
        return spec['descriptions'][name]
    else:
        return name

    
def partial_getter(spec, name='doc'):
    spec = ensure_spec(spec, ('layouts', 'partials'))
    layouts = spec['layouts']
    try:
        top = layouts[name]
    except KeyError:
        return
    logger.debug('Get partial: stem: %s', name)
    if top:
        for child_name, partial_name in top.items():
            if partial_name is None:
                partial_name = child_name
            try:
                fmt = spec['partials'][partial_name]
                fmt = ensure_unicode(fmt)
            except KeyError:
                raise PartialNotFoundError('Partial not found: {}'.format(partial_name))
            if child_name in layouts and layouts[child_name]:
                child = u'\n'.join(partial_getter(spec, name=child_name))
                child = u'\n{}\n'.format(child)
            else:
                logger.debug('Get partial: leaf: %s', child_name)
                child = u'{{{0}}}'.format(child_name)
            fmt = ensure_unicode(fmt)
            child_name = ensure_unicode(child_name)
            child = ensure_unicode(child)
            partial = fmt.format(**{'partialname': child_name, 
                                    'partialdescription': description(child_name, spec), 
                                    'partial': child})
            yield partial


