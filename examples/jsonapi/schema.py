import marshmallow as ma
from copy import copy

from marshmallow.class_registry import register


# register(classname, cls)

def JsonApificator(cls):
    class JsonApi(ma.Schema):

        id = ma.fields.Str()
        type = ma.fields.Str()

        attributes = ma.fields.Nested(cls())

        def dump(self, obj, many=None):

            with_meta = dict(attributes=obj, type=cls.__name__)

            return super(JsonApi, self).dump(with_meta, many=None)

    JsonApi.orig = cls
    JsonApi.__name__ = 'JsonApi_' + cls.__name__



    register(JsonApi.__name__, JsonApi)
    return JsonApi




