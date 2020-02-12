import marshmallow
import pytest
from apispec.ext.marshmallow import MarshmallowPlugin
from pyramid.config import Configurator
from pyramid.view import view_config
from webtest import TestApp
from cornice import Service
from cornice.validators import marshmallow_body_validator

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


def main(global_config, **settings):

    config = Configurator(settings=settings)

    config.include('cornice')
    config.include('cornice_apispec')

    config.add_route('openapi_spec', '/api-info')

    config.scan(exclude=['tests'])

    return config.make_wsgi_app()


@pytest.fixture
def app():
    app = main({})

    return TestApp(app)
