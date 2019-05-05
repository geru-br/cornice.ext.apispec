from marshmallow import Schema, fields


class MyNestedSchema(Schema):
    my_precious = fields.Boolean()


class BodySchema(Schema):
    id = fields.String()
    timestamp = fields.Int()
    obj = fields.Nested(MyNestedSchema)
    ex = fields.String()


class QuerySchema(Schema):
    foo = fields.String()


class HeaderSchema(Schema):
    foo = fields.String()


class PathSchema(Schema):
    meh = fields.String()


class GetRequestSchema(Schema):
    querystring = fields.Nested(QuerySchema)


class PutRequestSchema(Schema):
    body = fields.Nested(BodySchema)
    querystring = fields.Nested(QuerySchema)
    path = fields.Nested(PathSchema)


class ResponseSchema(Schema):
    body = fields.Nested(BodySchema)
    header = fields.Nested(HeaderSchema)


response_schemas = {
    '200': ResponseSchema(),
    '404': ResponseSchema()
}