from marshmallow import Schema, fields
from cornice import Service
from cornice.validators import marshmallow_body_validator
from wsgiref.simple_server import make_server
from pyramid.config import Configurator


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


response_schemas = {200: CustomerSchema}
response_product_schemas = {200: ProductSchema}
response_sales_schemas = {200: SaleSchema}


customers = Service(name='customers', path='/api/v1/customers/{uuid}', tags=[{'customers': 'Hello World'}], description='Customers')


@customers.post(schema=CustomerSchema, validators=(marshmallow_body_validator,), response_schemas=response_schemas)
def _customer_post(request):
    """
    :param request:
    :return:
    """
    title = request.validated['title']
    return {'title': title}


# customer_get = Service(name='customer_get', path='/api/v1/customers/{uuid}', tags=['customers'])


@customers.get()
def _customer_get(request):
    return request.matchdict['uuid']


products_post = Service(name='products_post', path='/api/v1/products', tags=['products'])


@products_post.post(schema=ProductSchema, validators=(marshmallow_body_validator,))
def _products_post(request):
    """
    :param request:
    :return:
    """
    uuid = request.validated['uuid']
    return uuid


products_get = Service(name='products_get', path='/api/v1/products/{uuid}', tags=['products'])


@products_get.get(response_schemas=response_product_schemas)
def _products_get(request):
    return request.matchdict['uuid']


sale_post = Service(name='sale_post', path='/api/v1/sales', tags=['sales'], description='Sale service')


@sale_post.post(schema=SaleSchema, validators=(marshmallow_body_validator,))
def _sale_post(request):
    """
    :param request:
    :return:
    """
    uuid = request.validated['uuid']
    return uuid


sale_get = Service(name='sale_get', path='/api/v1/sales/{uuid}', tags=['sales'])


@sale_get.get(response_schemas=response_sales_schemas)
def _sale_get(request):
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