class AutoDoc(object):
    """Where magic happens.

    This class will use the introspected view
    to find:

    * View Tags
    * View Request Schema and his location
    * View Response Schemas for each status code
    * View short summary and long description
    """

    def __init__(self, method, introspectable_view):
        """Init class.

        Cornice saves his own @view decorator configurations
        (example: `schema`, `content_type`, etc),
        inside original function view __views__ attribute,
        which is the `callable` key inside the introspectable view.

        :param method: (str) request method
        :param introspectable_view: Pyramid Introspector View instance
        """
        self.method = method
        self.view = introspectable_view
        self.view_operations = {}
        self.cornice_config = getattr(introspectable_view['callable'], '__views__', [])

    @property
    def tags(self):
        return self.view.get('apispec_tags', [])

    @property
    def summary(self):
        return self.view.get('apispec_summary', '')

    @property
    def description(self):
        return self.view.get('apispec_description', '')

    @property
    def request_schema_location(self):
        return self.view.get('apispec_validate_for', None)

    @property
    def response_schemas(self):
        return self.view.get('apispec_response_schemas', [])

    @property
    def content_type(self):
        content_type_info = [
            argument
            for argument in self.cornice_config
            if argument.get('content_type')
        ]
        if not content_type_info:
            return "text/plain"
        else:
            return content_type_info[0]['content_type']

    def find_request_schema(self):
        schema_info = [
            config
            for config in self.cornice_config
            if config.get('schema')
        ]
        return schema_info[0]['schema'] if schema_info else None

    def to_dict(self):
        self.view_operations.setdefault(self.method.lower(), {"responses": {}})
        if self.tags:
            self.view_operations[self.method.lower()].update({'tags': self.tags})
        if self.summary:
            self.view_operations[self.method.lower()].update({'summary': self.summary})
        if self.description:
            self.view_operations[self.method.lower()].update({'description': self.description})
        request_schema = self.find_request_schema()
        if request_schema and self.request_schema_location == 'body':
            request_body_dict = {
                'content': {
                    self.content_type: {
                        'schema': {
                            '$ref': "#/components/schemas/{}".format(request_schema.__name__)
                        }
                    }
                }
            }
            self.view_operations[self.method.lower()].update({'requestBody': request_body_dict})
        if self.response_schemas:
            operations_dict = {}
            for status_code in self.response_schemas:
                schema = self.response_schemas[status_code]
                schema_name = schema.__name__
                status_code_dict = {
                    status_code: {
                        'description': schema.__doc__ or "",
                        'content': {
                            self.content_type: {
                                'schema': {
                                    "$ref": "#/components/schemas/{}".format(schema_name)
                                }
                            }
                        }
                    }
                }
                operations_dict.update(status_code_dict)
            # Update current method dict in Operation
            self.view_operations[self.method.lower()].update({'responses': operations_dict})
        return self.view_operations
