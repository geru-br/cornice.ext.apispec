"""Cornice Swagger 2.0 documentor"""
import inspect
import warnings

from apispec import APISpec, BasePlugin
from apispec.ext.marshmallow import MarshmallowPlugin
from apispec.exceptions import DuplicateComponentNameError
from apispec.utils import build_reference

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

            new_operations = {method.lower(): {'description': service.description}}

            tags = []

            if hasattr(service, 'tags') and isinstance(service.tags, list):
                for tag in service.tags:
                    if isinstance(tag, dict):
                        tags.extend(tag.keys())
                    else:
                        tags.append(tag)

            if tags:
                new_operations[method.lower()].update({'tags': tags})

            schema = None if not Schemas(args).body else Schemas(args).body.__name__

            if schema:
                new_operations[method.lower()].update(
                    {'requestBody': {'content': {'application/json': {'schema': schema}}}}
                )

            parameters = {}
            for parameter in get_parameter_from_path(service.path):
                parameters[parameter] = parameter

            new_operations[method.lower()].update({'parameters': parameters})

            if None and schema:
                new_operations[method.lower()].update({'responses': {200: '200_' + schema}})

            operations.update(new_operations)

        return service.path

    def parameter_helper(self, parameter, service,  **kwargs):
        return parameter

    # def response_helper(self, response, service, status_code, schema, **kwargs):

    def response_helper(self, response, schema, status_code, **kwargs):

        schema_ref = build_reference('schema', 3,  schema.__name__)

        return {'content': {'application/json': {'schema': schema_ref}}}




def get_parameter_from_path(path):
    path_components = path.split('/')
    param_names = [comp[1:-1] for comp in path_components
                   if comp.startswith('{') and comp.endswith('}')]

    params = []
    for name in param_names:

        params.append(name)

    return params


class Schemas(object):
    def __init__(self, args):
        self.args = args

    def _has_cornice_base_validator(self, validators):
        """
        Cornice has a special validator that expect a especial schema with subsructure
        """
        # TODO: Add colander validator
        for validator in validators:
            if validator.__module__ in ['cornice.validators._marshmallow'] and validator.__name__ == 'validator':
                return True

        return False

    @property
    def body(self):
        if self._has_cornice_base_validator(self.args.get('validators', [])):
            return self.args.get('schema')().fields['body'].schema.__class__
        else:
            return self.args.get('schema', None)

    def querystring(self):
        return []

    def path(self):
        return []

    def headers(self):
        return []






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

        self.spec = APISpec(
            title=title,
            version=version,
            openapi_version="3.0.2",
            info=info,
            plugins=[MarshmallowPlugin(), CornicePlugin()],
        )

        for service in get_services():

            self.generate_schemas(service)
            self.generate_responses(service)
            self.generate_parameters(service)

            self.generate_tags(service)

            self.spec.path(service=service)

        return self.spec.to_dict()

    def generate_responses(self, service):

        for method, view, args in service.definitions:
            for key, value in args.get('response_schemas', {}).items():
                component_id = '{}_{}'.format(key, value.__name__)
                try:
                    self.spec.components.response(component_id, service=service, schema=value, status_code=key)
                except DuplicateComponentNameError:
                    pass

    def generate_schemas(self, service):

        for method, view, args in service.definitions:

            schemas = list([Schemas(args).body])

            schemas.extend(args.get('responses_schema', []))

            for schema in [schema for schema in schemas if schema]:

                try:
                    self.spec.components.schema(schema.__name__, schema=schema)
                except DuplicateComponentNameError:
                    pass

                try:
                    self.spec.components.parameter(schema.__name__, 'schema', service=service, schema=schema)
                except DuplicateComponentNameError:
                    pass

    def generate_tags(self, service):

        if hasattr(service, 'tags'):
            for tag in service.tags:
                if isinstance(tag, dict):
                    for key, value in tag.items():
                        self.spec.tag({'name': key, 'description': value})
                else:
                    self.spec.tag({'name': tag, 'description': service.description})

    def generate_parameters(self, service):

        for method, view, args in service.definitions:

            if method.lower() in map(str.lower, self.ignore_methods):
                continue

            for parameter in get_parameter_from_path(service.path):
                try:
                    self.spec.components.parameter(parameter, 'path', service=service)
                except DuplicateComponentNameError:
                    pass



