from marshmallow import Schema, fields
from cornice import Service
from cornice.validators import marshmallow_body_validator
from wsgiref.simple_server import make_server
from pyramid.config import Configurator


class PostSchema(Schema):
    id = fields.Str(dump_only=True)
    title = fields.Str()



class ProductSchema(Schema):
    id = fields.Str(dump_only=True)
    title = fields.Str()
    name = fields.Str()


requests_post = Service(name='resources_post', path='/api/v1/resource', tags=['resources'])
requests_get = Service(name='resource_get', path='/api/v1/resource/{uuid}', tags=['resources'])


@requests_post.post(schema=PostSchema, validators=(marshmallow_body_validator,))
def _requests_post(request):
    """

    :param request:
    :return:
    """
    uuid = request.validated['uuid']
    return uuid


@requests_get.get()
def _requests_get(request):
    return request.matchdict['uuid']



products_post = Service(name='products_post', path='/api/v1/products', tags=['products'])
products_get = Service(name='products_get', path='/api/v1/products/{uuid}', tags=['products'])

@products_post.post(schema=ProductSchema, validators=(marshmallow_body_validator,))
def _products_post(request):
    """

    :param request:
    :return:
    """
    uuid = request.validated['uuid']
    return uuid


@products_get.get(response_schemas=ProductSchema)
def _products_get(request):
    return request.matchdict['uuid']



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
