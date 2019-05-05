from apispec import BasePlugin
from apispec.utils import build_reference

from cornice_apispec.helpers import get_parameter_from_path, SchemasHelper, ResponseHelper


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

            schema = None if not SchemasHelper(args).body else SchemasHelper(args).body.__name__

            if schema:
                new_operations[method.lower()].update(
                    {'requestBody': {'content': {'application/json': {'schema': schema}}}}
                )

            parameters = {}
            for parameter in get_parameter_from_path(service.path):
                parameters[parameter] = parameter

            parameter_schema = None if not SchemasHelper(args).path else SchemasHelper(args).path.__name__

            if parameter_schema:
                parameters[parameter_schema] = parameter_schema

            new_operations[method.lower()].update({'parameters': parameters})

            for component_id, status_code, schema in ResponseHelper(args).responses:
                new_operations[method.lower()].update({'responses': {status_code: component_id}})

            operations.update(new_operations)

        return service.path

    def parameter_helper(self, parameter, service,  **kwargs):

        if 'schema' in kwargs:
            schema_ref = build_reference('schema', 3, kwargs['schema'].__name__)
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
            schema_ref = build_reference('schema', 3,  schema.__name__)

            return {'description': schema.__name__,
                    'content': {'application/json': {'schema': schema_ref}}}
        else:
            return {'description': 'Default Response',
                    'content': {'text/plain': {'schema': {'type': 'string'}}}}