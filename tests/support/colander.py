import colander as cl

from cornice_apispec.converters.schema import TypeConverter


class MyNestedSchema(cl.MappingSchema):
    my_precious = cl.SchemaNode(cl.Boolean())


class BodySchema(cl.MappingSchema):
    id = cl.SchemaNode(cl.String())
    timestamp = cl.SchemaNode(cl.Int())
    obj = MyNestedSchema()
    ex = cl.SchemaNode(cl.String(), missing=cl.drop, example='example string')


class QuerySchema(cl.MappingSchema):
    foo = cl.SchemaNode(cl.String(), validator=cl.Length(3), missing=cl.drop)


class HeaderSchema(cl.MappingSchema):
    bar = cl.SchemaNode(cl.String(), missing=cl.drop)


class PathSchema(cl.MappingSchema):
    meh = cl.SchemaNode(cl.String(), default='default')


class GetRequestSchema(cl.MappingSchema):
    querystring = QuerySchema()


class PutRequestSchema(cl.MappingSchema):
    body = BodySchema()
    querystring = QuerySchema()
    header = HeaderSchema()


class ResponseSchema(cl.MappingSchema):
    body = BodySchema()
    header = HeaderSchema()


response_schemas = {
    '200': ResponseSchema(description='Return ice cream'),
    '404': ResponseSchema(description='Return sadness')
}


class DeclarativeSchema(cl.MappingSchema):
    @cl.instantiate(description='my body')
    class body(cl.MappingSchema):
        id = cl.SchemaNode(cl.String())


class AnotherDeclarativeSchema(cl.MappingSchema):
    @cl.instantiate(description='my another body')
    class body(cl.MappingSchema):
        timestamp = cl.SchemaNode(cl.Int())


class AnyType(cl.SchemaType):
    """A simple custom colander type."""
    def deserialize(self, cstruct=cl.null):
        return cstruct


class AnyTypeConverter(TypeConverter):
    def __call__(self, schema_node):
        return {}
