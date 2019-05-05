from apispec import BasePlugin
from apispec.utils import build_reference

from cornice_apispec.helpers import get_parameter_from_path, SchemasHelper, ResponseHelper
from cornice_apispec.utils import get_schema_name

class CornicePlugin(BasePlugin):

    def path_helper(self, operations, path, service, ignore_methods=None,  **kwargs):
        """Path helper that parses docstrings for operations. Adds a
        ``func`` parameter to `apispec.APISpec.path`.
        """

        ignore_methods = ignore_methods or ['HEAD', 'OPTIONS']

        for method, view, args in service.definitions:

            if method.lower() in map(str.lower, ignore_methods):
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

            schema = None if not SchemasHelper(service, args).body else get_schema_name(SchemasHelper(service, args).body)

            if schema:
                new_operations[method.lower()].update(
                    {'requestBody': {'content': {'application/json': {'schema': schema}}}}
                )

            parameters = {}
            if service.path:
                for parameter in get_parameter_from_path(service.path):
                    parameters[parameter] = parameter

            parameter_schema = None if not SchemasHelper(service, args).path else get_schema_name(SchemasHelper(service, args).path)

            if parameter_schema:
                parameters[parameter_schema] = parameter_schema

            new_operations[method.lower()].update({'parameters': parameters})

            for component_id, status_code, schema in ResponseHelper(service, args).responses:
                new_operations[method.lower()].update({'responses': {status_code: component_id}})

            operations.update(new_operations)

        return path

    def parameter_helper(self, parameter, service,  **kwargs):

        if 'schema' in kwargs:
            schema_ref = build_reference('schema', 3, get_schema_name(kwargs['schema']))
            parameter.update({'schema': schema_ref})
        else:
            parameter.update({
                'content': {'text/plain': {'schema': {'type': 'string'}}},
                'required': True,
            })
        return parameter

    # def response_helper(self, response, service, status_code, schema, **kwargs):

    def response_helper(self, response, schema, status_code, **kwargs):

        if schema:
            schema_ref = build_reference('schema', 3,  get_schema_name(schema))

            return {'description': get_schema_name(schema),
                    'content': {'application/json': {'schema': schema_ref}}}
        else:
            return {'description': 'Default Response',
                    'content': {'text/plain': {'schema': {'type': 'string'}}}}

