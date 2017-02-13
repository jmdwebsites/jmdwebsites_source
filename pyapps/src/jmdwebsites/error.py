class JmdwebsitesError(Exception): pass
class FatalError(JmdwebsitesError): pass
class NonFatalError(JmdwebsitesError): pass
class PathNotFoundError(JmdwebsitesError): pass
