"""Cornice Swagger 2.0 documentor"""
import inspect
import warnings

from apispec import APISpec, BasePlugin
from apispec.ext.marshmallow import MarshmallowPlugin
from apispec.exceptions import DuplicateComponentNameError

from cornice.service import get_services


class CornicePlugin(BasePlugin):
    ignore_methods = ['HEAD', 'OPTIONS']

    def path_helper(self, operations, service, **kwargs):
        """Path helper that parses docstrings for operations. Adds a
        ``func`` parameter to `apispec.APISpec.path`.
        """

        for method, view, args in service.definitions:

            if method.lower() in map(str.lower, self.ignore_methods):
                continue

            schema = args.get('schema', None)
            response_schemas = args.get('response_schemas', {})
            if schema:
                operations.update({method.lower():
                                       {'parameters': self.parameter_helper('', service, schema=schema),
                                        'description': 'Get a random pet',
                                        'requestBody': {'content': {'application/json': {'schema': schema.__name__}}},
                                        'responses': {k: {'content': {'application/json': {'schema': v.__name__}}}
                                                      for k, v in response_schemas.items()}}})
            else:
                operations.update({method.lower():
                                       {'description': 'Get a random pet',
                                        'parameters': {'uuid': 'uuid'},
                                        'responses': {200: {'content': {'application/json': 'lala'}}}}})

        return service.path

    def parameter_helper(self, parameter, service, **kwargs):
        schema = kwargs.get('schema')
        parameters = []
        for parameter in get_parameter_from_path(service.path):
            parameters.append({
                'name': parameter,
                'description': getattr(schema, 'params_description', {}).get(parameter, ''),
            })

        return parameters


def get_parameter_from_path(path):
    path_components = path.split('/')
    param_names = [comp[1:-1] for comp in path_components
                   if comp.startswith('{') and comp.endswith('}')]

    params = []
    for name in param_names:
        params.append(name)

    return params


class CorniceSwaggerException(Exception):
    """Raised when cornice services have structural problems to be converted."""


class CorniceSwagger(object):
    """Handles the creation of a swagger document from a cornice application."""

    services = []
    """List of cornice services to document. You may use
    `cornice.service.get_services()` to get it."""

    custom_type_converters = {}
    """Mapping for supporting custom types conversion on the default TypeConverter.
    Should map `colander.TypeSchema` to `cornice_apispec.converters.schema.TypeConverter`
    callables."""

    default_type_converter = None
    """Supplies a default type converter matching the interface of
    `cornice_apispec.converters.schema.TypeConverter` to be used with unknown types."""

    default_tags = None
    """Provide a default list of tags or a callable that takes a cornice
    service and the method name (e.g GET) and returns a list of Swagger
    tags to be used if not provided by the view."""

    default_op_ids = None
    """Provide a callable that takes a cornice service and the method name
    (e.g. GET) and returns an operation Id that is used if an operation Id is
    not provided. Each operation Id should be unique."""

    default_security = None
    """Provide a default list or a callable that takes a cornice service and
    the method name (e.g. GET) and returns a list of OpenAPI security policies."""

    summary_docstrings = False
    """Enable extracting operation summaries from view docstrings."""

    ignore_methods = ['HEAD', 'OPTIONS']
    """List of service methods that should NOT be presented on the
    documentation. You may use this to remove methods that are not
    essential on the API documentation. Default ignores HEAD and OPTIONS."""

    ignore_ctypes = []
    """List of service content-types that should NOT be presented on the
    documentation. You may use this when a Cornice service definition has
    multiple view definitions for a same method, which is not supported on
    OpenAPI 2.0."""

    api_title = ''
    """Title of the OpenAPI document."""

    api_version = ''
    """Version of the OpenAPI document."""

    base_path = '/'
    """Base path of the documented API. Default is "/"."""

    swagger = {'info': {}}
    """Base OpenAPI document that should be merged with the extracted info
    from the generate call."""

    def __init__(self, services=None, def_ref_depth=0, param_ref=False,
                 resp_ref=False, pyramid_registry=None):
        """
        :param services:
            List of cornice services to document. You may use
            cornice.service.get_services() to get it.
        :param def_ref_depth:
            How depth swagger object schemas should be split into
            swaggger definitions with JSON pointers. Default (0) is no split.
            You may use negative values to split everything.
        :param param_ref:
            Defines if swagger parameters should be put inline on the operation
            or on the parameters section and referenced by JSON pointers.
            Default is inline.
        :param resp_ref:
            Defines if swagger responses should be put inline on the operation
            or on the responses section and referenced by JSON pointers.
            Default is inline.
        :param pyramid_registry:
            Pyramid registry, should be passed if you use pyramid routes
            instead of service level paths.
        """
        super(CorniceSwagger, self).__init__()

        self.pyramid_registry = pyramid_registry
        if services is not None:
            self.services = services

    def generate(self, title=None, version=None, base_path=None,
                 info=None, swagger=None, **kwargs):
        """Generate a Swagger 2.0 documentation. Keyword arguments may be used
        to provide additional information to build methods as such ignores.

        :param title:
            The name presented on the swagger document.
        :param version:
            The version of the API presented on the swagger document.
        :param base_path:
            The path that all requests to the API must refer to.
        :param info:
            Swagger info field.
        :param swagger:
            Extra fields that should be provided on the swagger documentation.

        :rtype: dict
        :returns: Full OpenAPI/Swagger compliant specification for the application.
        """

        title = title or self.api_title
        version = version or self.api_version
        info = info or self.swagger.get('info', {})
        swagger = swagger or self.swagger
        base_path = base_path or self.base_path

        spec = APISpec(
            title=title,
            version=version,
            openapi_version="3.0.2",
            info=info,
            plugins=[MarshmallowPlugin(), CornicePlugin()],
        )

        for service in get_services():
            for method, view, args in service.definitions:

                if method.lower() in map(str.lower, self.ignore_methods):
                    continue

                schema = args.get('schema', None)
                if schema:
                    try:
                        spec.components.schema(schema.__name__, schema=schema)
                    except DuplicateComponentNameError:
                        pass

                    try:
                        spec.components.parameter(schema.__name__, 'schema', service=service, schema=schema)
                    except DuplicateComponentNameError:
                        pass

                for parameter in get_parameter_from_path(service.path):
                    try:
                        spec.components.parameter(parameter, 'path', service=service)
                    except DuplicateComponentNameError:
                        pass

        for service in get_services():
            spec.path(service=service)

        return spec.to_dict()
