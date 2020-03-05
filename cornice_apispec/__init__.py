import logging

from apispec import APISpec
from cornice_apispec.paths import add_pyramid_paths
from cornice_apispec.predicates import SwaggerDescriptionPredicate, SwaggerResponseSchemasPredicate, \
    SwaggerShowInPredicate, SwaggerSummaryPredicate, SwaggerTagsPredicate

logger = logging.getLogger(__name__)


def includeme(config):
    config.include('pyramid_apispec.views')
    config.add_view_predicate('apispec_response_schemas', SwaggerResponseSchemasPredicate)
    config.add_view_predicate('apispec_tags', SwaggerTagsPredicate)
    config.add_view_predicate('apispec_summary', SwaggerSummaryPredicate)
    config.add_view_predicate('apispec_description', SwaggerDescriptionPredicate)
    config.add_view_predicate('apispec_show', SwaggerShowInPredicate)
    # To auto-generate the Swagger view
    # use settings["auto_generate.swagger.view"] = True
    # or simply do not set anything.
    # If you explicitly set this to False
    # you can define in you App one or more Swagger views.
    settings = config.registry.settings
    if settings.get("auto_generate.swagger.view", True) is True:
        config.add_route("openapi_spec", "/openapi.json")
        config.pyramid_apispec_add_explorer(
            spec_route_name='openapi_spec')


def generate_spec(request, swagger_info, plugins, filter_by_tags=False):
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
        * `show_options`: Show OPTIONS requests in Swagger (default: True)
        * `tag_list`: Tag dict list. No defaults.
            (example: [{'name': 'my tag', 'description': 'my description'}]).
        * `scheme`: http or https. If not informed, will extract from request.

        The `filter_by_tags` option will filter all views which does not have at
        least one tag from swagger_info tag_list.

    :param request: Pyramid Request
    :param swagger_info: Dict
    :param plugins: APISpec Plugins list
    :param filter_by_tags: Show only views with tags inside tag_list
    :return: Dict
    """
    def check_tag(view):
        if not filter_by_tags:
            return True
        view_tags = view['introspectable'].get('apispec_tags', [])
        openapi_tags = [tag['name'] for tag in spec._tags]
        if not view_tags:
            return False
        for tag in view_tags:
            if tag in openapi_tags:
                return True
        return False

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
    all_api_views = [
        view['introspectable']
        for view in introspector.get_category('views')
        if view['introspectable'].get('apispec_show', False) is True
           and view['introspectable'].get('request_methods')
           and check_tag(view)
    ]

    for api_view in all_api_views:
        add_pyramid_paths(
            spec, api_view.get('route_name'),
            request=request,
            show_head=swagger_info.get('show_head', False),
            show_options=swagger_info.get('show_options', True)
        )

    openapi_spec = spec.to_dict()

    main_description = swagger_info.get('main_description', "")
    if main_description:
        openapi_spec['info'].update({'description': main_description})

    scheme = swagger_info.get('scheme', request.scheme)
    main_server_url = '{}://{}'.format(scheme, request.host)
    logger.info('Server URL for swagger json is {}'.format(main_server_url))
    openapi_spec.update({'servers': [{'url': main_server_url}]})

    return openapi_spec
