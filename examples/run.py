from wsgiref.simple_server import make_server

import marshmallow
from apispec.ext.marshmallow import MarshmallowPlugin
from cornice import Service
from pyramid.config import Configurator
from cornice.validators import marshmallow_body_validator
from pyramid.view import view_config

from cornice_apispec import generate_spec


class Schema(marshmallow.Schema):
    name = marshmallow.fields.String(required=True)


response_schemas = {
    200: Schema,
}


user_info = Service(name='users',
                    path='/',
                    validators=(marshmallow_body_validator,),
                    apispec_show=True,
                    apispec_response_schemas=response_schemas,
                    description='Get and set user data.')


@user_info.get()
def get_info(request):
    return {'name': 'Name'}


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
        'tag_list': [{'tag': 'My Tag', 'description': 'Tag description'}],
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