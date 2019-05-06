"""Cornice Swagger 2.0 documentor"""

from apispec import APISpec
from apispec.ext.marshmallow import MarshmallowPlugin
from apispec.exceptions import DuplicateComponentNameError

from cornice_apispec.exceptions import CorniceSwaggerException
from cornice_apispec.helpers import get_parameter_from_path, SchemasHelper, ResponseHelper, PathHelper, TagsHelper
from cornice_apispec.utils import get_schema_name
from cornice_apispec.plugins.cornice import CornicePlugin


class CorniceSwagger(object):
    """Handles the creation of a swagger document from a cornice application."""

    spec = None

    default_op_ids = None
    """Provide a callable that takes a cornice service and the method name
    (e.g. GET) and returns an operation Id that is used if an operation Id is
    not provided. Each operation Id should be unique."""

    services = []
    """List of cornice services to document. You may use
    `cornice.service.get_services()` to get it."""

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

        if self.default_op_ids and not callable(self.default_op_ids):
            raise CorniceSwaggerException


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

        for service in self.services:

            self.generate_schemas(service)
            self.generate_responses(service)
            self.generate_parameters(service)
            self.generate_tags(service)
            self.generate_paths(service)

        return self.spec.to_dict()

    def generate_paths(self, service):

        for method, view, args in service.definitions:
            helper = PathHelper(service, args, pyramid_registry=self.pyramid_registry)
            try:
                self.spec.path(
                    service=service,
                    path=helper.path,
                    ignore_methods=self.ignore_methods,
                    default_op_ids=self.default_op_ids
                )
            except DuplicateComponentNameError:
                pass

    def generate_responses(self, service):

        for method, view, args in service.definitions:
            for component_id, status_code, schema in ResponseHelper(service, args).responses:
                try:
                    self.spec.components.response(component_id, service=service, schema=schema, status_code=status_code)
                except DuplicateComponentNameError:
                    pass

    def generate_schemas(self, service):

        for method, view, args in service.definitions:

            helper = SchemasHelper(service, args)

            schemas = list([helper.body, helper.path])

            schemas.extend(args.get('responses_schema', []))

            for schema in [schema for schema in schemas if schema]:

                try:
                    self.spec.components.schema(get_schema_name(schema), schema=schema)
                except DuplicateComponentNameError:
                    pass

    def generate_tags(self, service):

        for method, view, args in service.definitions:

            for tag in TagsHelper(service, args).tags:

                self.spec.tag(tag)

    def generate_parameters(self, service):

        for method, view, args in service.definitions:

            if method.lower() in map(str.lower, self.ignore_methods):
                continue

            if service.path:

                for parameter in get_parameter_from_path(service.path):
                    try:
                        self.spec.components.parameter(parameter, 'path', service=service)
                    except DuplicateComponentNameError:
                        pass

            schemas = list([SchemasHelper(service, args).path])

            for schema in [schema for schema in schemas if schema]:

                try:
                    self.spec.components.parameter(get_schema_name(schema), 'path', service=service, schema=schema)
                except DuplicateComponentNameError:
                    pass
