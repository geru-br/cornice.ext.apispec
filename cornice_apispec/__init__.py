from apispec import APISpec
from cornice_apispec.paths import add_pyramid_paths
from cornice_apispec.predicates import SwaggerDescriptionPredicate, SwaggerResponseSchemasPredicate, \
    SwaggerShowInPredicate, SwaggerSummaryPredicate, SwaggerTagsPredicate, SwaggerValidateForPredicate


def includeme(config):
    config.add_route("openapi_spec", "/openapi.json")
    config.include('pyramid_apispec.views')
    config.add_view_predicate('apispec_response_schemas', SwaggerResponseSchemasPredicate)
    config.add_view_predicate('apispec_tags', SwaggerTagsPredicate)
    config.add_view_predicate('apispec_summary', SwaggerSummaryPredicate)
    config.add_view_predicate('apispec_description', SwaggerDescriptionPredicate)
    config.add_view_predicate('apispec_show', SwaggerShowInPredicate)
    config.add_view_predicate('apispec_validate_for', SwaggerValidateForPredicate)
    config.pyramid_apispec_add_explorer(
        spec_route_name='openapi_spec')


def generate_spec(request, swagger_info, plugins):
    """Generate OpenAPI Spec.

    This function will start the route introspection in Pyramid,
    looking for views with the following cornice_apispec and cornice predicates:

    * `schema`: Cornice predicate for Schema validator
    * `content_type`: Cornice/Pyramid predicate for Content-Type
    * `apispec_response_schemas`: (List) Response Schemas to add in Swagger
    * `apispec_tags`: (List) Tag List for view
    * `apispec_summary`: (Str) Short Summary for view operation in swagger
    * `apispec_description`: (Str) Long description for view operation in swagger
    * `apispec_show`: (Bool) Only views with this predicate will be included in Swagger
    * `apispec_validate_for`: (Str, Enum) For the Request Schema, you need to inform
                                current location for the schema: 'body', 'querystring',
                                'header' or 'path'
                                Currently, only body validators are supported.

    Examples
    ^^^^^^^^

    ## Pyramid::

        @view_config(
            apispec_tags=['health'],
            apispec_summary="Returns healthcheck',
            apispec_description="Long description for operation",
            apispec_show=True)
        def health_check(request):
            request.response.status = 200
            request.response.body = "OK"
            return request.response

    ## Cornice Service::

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

    For more examples, please see ./examples folder.

    swagger_info options
    ^^^^^^^^^^^^^^^^^^^^
        * `title`: Api Title (default: 'OpenAPI Docs')
        * `main_description`: Main description for API. Accepts Markdown. (Default: '')
        * `version`: Api Version (default: '0.1.0')
        * `openapi_version`: OpenAPI version (default: '3.0.2')
        * `show_head`: Show HEAD requests in Swagger (default: False)
        * `tag_list`: Tag dict list. No defaults.
            (example: [{'name': 'my tag', 'description': 'my description'}]).

    :param request: Pyramid Request
    :param swagger_info: Dict
    :param plugins: APISpec Plugins list
    :return: Dict
    """
    spec = APISpec(
        title=swagger_info.get('title', "OpenAPI Docs"),
        version=swagger_info.get('version', '0.1.0'),
        plugins=[plugin() for plugin in plugins],
        openapi_version=swagger_info.get('openapi_version', '3.0.2')
    )
    for tag in swagger_info.get('tag_list', []):
        spec.tag(tag)
    registry = request.registry
    introspector = registry.introspector
    all_views = introspector.get_category('views')
    all_api_views = [
        view['introspectable']
        for view in all_views
        if view['introspectable'].get('apispec_show', False) is True
           and view['introspectable'].get('request_methods')
    ]
    all_api_routes = set([
        view['route_name']
        for view in all_api_views
    ])
    for route in all_api_routes:
        add_pyramid_paths(spec, route, request=request, show_head=swagger_info.get('show_head', False))

    openapi_spec = spec.to_dict()
    main_description = swagger_info.get('main_description', "")
    if main_description:
        openapi_spec['info'].update({'description': main_description})
    openapi_spec.update({'servers': [{'url': request.host_url}]})
    return openapi_spec
