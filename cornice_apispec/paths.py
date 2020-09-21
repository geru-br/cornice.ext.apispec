import inspect

from pyramid.threadlocal import get_current_request
from pyramid_apispec.helpers import check_methods_matching, is_view, reformat_pattern, should_ignore_view

from cornice_apispec.operations import get_operations
from cornice_apispec.utils import add_schema_in_spec


def add_pyramid_paths(
        spec,
        route_name,
        request=None,
        request_method=None,
        operations=None,
        autodoc=True,
        **kwargs
):
    """
    Adds a route and view info to spec
    :param spec:
        ApiSpec object
    :param route_name:
        Route name to inspect
    :param request:
        Request object, if `None` then `get_current_request()` will be used
    :param request_method:
        Request method predicate
    :param operations:
        Operations dict that will be used instead of introspection
    :param autodoc:
        Include information about endpoints without markdown docstring
    :param kwargs:
        Additional kwargs for predicate matching
    :return:
    """
    if request is None:
        request = get_current_request()

    show_head = kwargs.pop('show_head', False)
    show_options = kwargs.pop('show_options', True)
    registry = request.registry
    # TODO: This is the original pyramid_apispec introspector use,
    #   getting routes instead of views.
    #   I don't know if we can ride this one and use only the
    #   introspector views used before in `generate_spec` function
    introspector = registry.introspector
    route = introspector.get("routes", route_name)
    introspectables = introspector.related(route)
    ignored_view_names = kwargs.pop("ignored_view_names", None)
    # needs to be rewritten to internal name
    if request_method:
        kwargs["request_methods"] = request_method

    for maybe_view in introspectables:
        # skip excluded views/non-views
        if (
                not is_view(maybe_view)
                or not check_methods_matching(maybe_view, **kwargs)
                or should_ignore_view(maybe_view, ignored_views=ignored_view_names)
                or not maybe_view.get('apispec_show', False)
        ):
            continue

        # Find Response Schemas if available in View Predicate
        response_schemas = maybe_view.get('apispec_response_schemas', {})
        for _, schema in response_schemas.items():
            if inspect.isfunction(schema): # It maybe a lambda function
                schema = schema()
            add_schema_in_spec(spec, schema)

        original_pattern = route["pattern"]
        pattern = reformat_pattern(original_pattern)
        spec.path(
            pattern,
            operations=get_operations(
                spec, pattern, maybe_view, operations,
                autodoc=autodoc,
                show_head=show_head,
                show_options=show_options,
                cornice_service=request.registry.cornice_services.get(original_pattern)
            )
        )
