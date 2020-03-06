from datetime import datetime
from wsgiref.simple_server import make_server

import marshmallow
from apispec.ext.marshmallow import MarshmallowPlugin
from cornice import Service
from pyramid.config import Configurator
from pyramid.view import view_config

from cornice_apispec import generate_spec
from cornice_apispec.validators import (
    apispec_marshmallow_body_validator
)


class Schema(marshmallow.Schema):
    name = marshmallow.fields.String(required=True)
    birthday = marshmallow.fields.Date()


class Error(marshmallow.Schema):
    code = marshmallow.fields.String()
    description = marshmallow.fields.String()


response_schemas = {
    200: Schema,
    400: Error,
    301: 'Redirect URL',
    404: 'Not Found by ID'
}

user_info = Service(name='users',
                    path='/{id}/{action:.*}',
                    apispec_show=True,
                    apispec_response_schemas=response_schemas,
                    description='Get and set user data.')


@user_info.delete()
def get_info(request):
    return {'name': 'Name', "birthday": datetime.utcnow().date().isoformat()}


@user_info.get()
def get_info(request):
    return {'name': 'Name', "birthday": datetime.utcnow().date().isoformat()}


@user_info.post(
    schema=Schema(),
    content_type='application/json'
)
def post_info(request):
    return {'name': 'Name', "birthday": datetime.utcnow().date().isoformat()}


@user_info.put(
    schema=Schema,
    content_type='application/json',
    validators=(apispec_marshmallow_body_validator,))
def post_info(request):
    return {'name': 'Name', "birthday": datetime.utcnow().date().isoformat()}


@user_info.patch(
    schema=Schema,
    content_type='application/json',
    validators=(apispec_marshmallow_body_validator,))
def post_info(request):
    return {'name': 'Name', "birthday": datetime.utcnow().date().isoformat()}


@view_config(route_name='openapi_spec', renderer='json')
def api_spec(request):
    """Returns OpenApi dictionary for swagger.

    You need to pass a true request object
    for Pyramid Introspector work correctly.

    :param request: Pyramid Request
    :return: Dict
    """
    swagger_info = {
        'title': "My API",
        'version': "1.0.0",
        'tag_list': [{'name': 'My Tag', 'description': 'Tag description'}],
        'main_description': "Main description for API",
        'show_head': False
    }
    openapi_spec = generate_spec(request, swagger_info, plugins=[MarshmallowPlugin])
    return openapi_spec


if __name__ == '__main__':
    with Configurator() as config:
        config.include('cornice')
        config.include('cornice_apispec')

        config.add_route('openapi_spec', '/api-info')

        config.scan(exclude=['tests'])
        app = config.make_wsgi_app()

    server = make_server('0.0.0.0', 6543, app)
    server.serve_forever()
