from marshmallow import Schema, fields
from cornice.resource import resource, view
from cornice.validators import marshmallow_body_validator
from wsgiref.simple_server import make_server
from pyramid.config import Configurator
from pyramid.security import Allow, Everyone


class CustomerSchema(Schema):
    id = fields.Str(dump_only=True)
    title = fields.Str()


class ProductSchema(Schema):
    id = fields.Str(dump_only=True)
    title = fields.Str()
    name = fields.Str()
    active = fields.Boolean()


class SaleSchema(Schema):
    customer = fields.Nested(CustomerSchema())
    product = fields.Nested(ProductSchema())
    quantity = fields.Decimal()


_USERS = {1: {'name': 'gawel'}, 2: {'name': 'tarek'}}


@resource(collection_path='/customers', path='/customers/{uuid}')
class Customers(object):

    def __init__(self, request, context=None):
        self.request = request

    def __acl__(self):
        return [(Allow, Everyone, 'everything')]

    def collection_get(self):
        return {'users': _USERS.keys()}

    def get(self):
        return _USERS.get(int(self.request.matchdict['id']))

    @view(schema=CustomerSchema, validators=(marshmallow_body_validator,))
    def post(self):
        return _USERS.get(int(self.request.matchdict['id']))

    def collection_post(self):
        print(self.request.json_body)
        _USERS[len(_USERS) + 1] = self.request.json_body
        return True


# Setup and run our app
def setup():
    config = Configurator()
    config.include('cornice')
    config.include('cornice_apispec')
    # Create views to serve our OpenAPI spec
    config.cornice_enable_openapi_view(
        api_path='/__api__',
        title='MyAPI',
        description="OpenAPI documentation",
        version='1.0.0'
    )
    # Create views to serve OpenAPI spec UI explorer
    config.cornice_enable_openapi_explorer(api_explorer_path='/api-explorer')
    config.scan()
    app = config.make_wsgi_app()
    return app


if __name__ == '__main__':
    app = setup()
    server = make_server('127.0.0.1', 8000, app)
    print('Visit me on http://127.0.0.1:8000')
    print('''You can see the API explorer here:
    http://127.0.0.1:8000/api-explorer''')
    server.serve_forever()