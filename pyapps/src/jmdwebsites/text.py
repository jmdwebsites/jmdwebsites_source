#TODO: Not tested yet


class Utf8(object):

    def __init__(self, obj):
        self.obj = obj
    
    def __unicode__(self):
        return unicode(self.obj)

    def __str__(self):
        return self.__unicode__().encode('utf-8')

    def __repr__(self):
        return repr(self.__str__())


class TextWrapper(object):

    def __init__(self, obj=None, encoding='utf-8'):
        self.encoding = encoding
        if obj is None:
            self.obj = ''
        else:
            self.obj = obj
    
    def __unicode__(self):
        return unicode(self.obj)

    def __str__(self):
        return self.__unicode__().encode(self.encoding)

    def __repr__(self):
        return repr(self.__unicode__())


