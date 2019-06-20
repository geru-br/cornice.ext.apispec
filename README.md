## Welcome to Cornice APISpec

### Install

#### Add in Pyramid configuration:

```python
config.include('cornice')
config.include('cornice_apispec')
```

#### Add the Api-Explorer View:

```python
from apispec.ext.marshmallow import MarshmallowPlugin
from cornice_apispec import generate_spec
from pyramid.request import Request
from pyramid.view import view_config

@view_config(route_name='openapi_spec', renderer='json')
def api_spec(request: Request) -> dict:
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
```

#### Add your API views:

```python
from pyramid.view import view_config

@view_config(
    apispec_tags=['health'],
    apispec_summary="Returns healthcheck',
    apispec_description="Long description for operation",
    apispec_show=True)
def health_check(request):
    request.response.status = 200
    request.response.body = "OK"
    return request.response
```

You can also use **docstrings**:

```python
from pyramid.view import view_config

@view_config(apispec_show=True)
def health_check(request):
    """Returns Health Check for API.

        :param request: Pyramid Request
        :return: dict

        ---
        get:
            description: Returns API health check.
            tags:
                - Other
            responses:
                200:
                    description: OK
                    content:
                        application/vnd.api+json:
                            schema:
                                type: object
                                properties:
                                    meta:
                                        type: object
                                        example: {"result": "OK"}
    """
    request.response.status = 200
    request.response.body = "OK"
    return request.response
```

Do not add predicates when using docstrings, `cornice_apispec` will
ignore them, if finds a valid docstring to parse. To add `tag` or
`description` please add them inside Docstring.

#### View Predicates:

| Predicate                | Desc                                                                     |
|:-------------------------|:-------------------------------------------------------------------------|
| apispec_tags             | Tag list for view                                                        |
| apispec_summary          | Short description                                                        |
| apispec_description      | Long description                                                         |
| apispec_show             | Show in Swagger                                                          |
| apispec_response_schemas | Validation schemas dict for Swagger. Format is `{ status_code: schema }` |

## Using Cornice

Both Service and Resource are supported. Also `cornice_apispec` will use
too `schema` and `content_type` cornice predicates for generate Swagger

#### Using Service

```python
from cornice import Service

health_chech_service = Service(
    name='healthcheck_api',
    description='API HealthCheck',
    path="/health",
    apispec_show=True,
    apispec_tags=['health']
)

@health_chech_service.get(
    apispec_description="Long description for operation")
def health_check(request):
    request.response.status = 200
    request.response.body = "OK"
    return request.response
```

#### Using Resource

```python
from cornice.resource import resource, view
from marshmallow import Schema, fields
from cornice.validators import marshmallow_body_validator
from pyramid.request import Request
from pyramid.response import Response

class MyResourceSchema(Schema):
    name = fields.Str()

class BadRequestSchema(Schema):
    error = fields.Str()

my_resource_request_response_schemas = {
    200: MyResourceSchema,
    400: BadRequestSchema
}

@resource(name='my_resource',
          collection_path='/resources',
          path='/resources/{resourceId}',
          apispec_tags=['Resource'], apispec_show=True)
class MyResourceApi:
    def __init__(self, request: Request) -> None:
        self.request = request

    @view(schema=MyResourceSchema,
          validators=(marshmallow_body_validator,),
          apispec_response_schemas=my_resource_request_response_schemas,
          apispec_summary="Summary for this operation",
          content_type='application/json')
    def collection_post(self) -> Response:
        response = self.request.response
        response.status = 201
        response.body = self.request.validated
        return response

```

## Current Issues
1. `cornice_apispec` does not handle `header`, `querystring` and `path` validators. Only `body` validators.
2. Currently not tested with Colander.
