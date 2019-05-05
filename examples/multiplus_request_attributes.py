from marshmallow import Schema, fields, validate
from cornice import Service
from cornice.validators import marshmallow_validator
from wsgiref.simple_server import make_server
from pyramid.config import Configurator


class Querystring(Schema):
    referrer = fields.String()


class Payload(Schema):
    username = fields.String(validate=[
        validate.Length(min=3)
    ], required=True)


class SignupSchema(Schema):
    body = fields.Nested(Payload)
    querystring = fields.Nested(Querystring)


signup = Service(name='signup', path='/api/v1/signup', tags=['signup'])


@signup.post(schema=SignupSchema, validators=(marshmallow_validator,))
def signup_post(request):
    username = request.validated['body']['username']
    referrer = request.validated['querystring']['referrer']
    return {'success': True}



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
