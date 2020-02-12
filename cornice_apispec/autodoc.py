
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
    def validators(self):
        return self.cornice_config[0].get('validators', [])

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

    def _find_request_schema(self):
        schema_info = [
            config
            for config in self.cornice_config
            if config.get('schema')
        ]
        return schema_info[0]['schema'] if schema_info else None

    def find_schema_for(self, location):
        if location not in ['body', 'headers', 'path', 'querystring']:
            raise ValueError('Location not valid for find Schema')
        request_schema = self._find_request_schema()
        if not request_schema:
            return None
        for validator in self.validators:
            if validator.__dict__.get('location', '') == 'all':
                source_class = request_schema._declared_fields.get(location, None)
                return source_class.nested if source_class else None
            if validator.__dict__.get('location', '') == location:
                return request_schema

        # No valid cornice validator was found
        # but request_schema exists. In this case,
        # return the nested match schema
        maybe_nested = request_schema._declared_fields.get(location, None)
        return maybe_nested.nested if maybe_nested else None

    def to_dict(self):
        self.view_operations.setdefault(self.method.lower(), {"responses": {}})
        if self.tags:
            self.view_operations[self.method.lower()].update({'tags': self.tags})
        if self.summary:
            self.view_operations[self.method.lower()].update({'summary': self.summary})
        if self.description:
            self.view_operations[self.method.lower()].update({'description': self.description})

        self.generate_request_body()
        self.generate_parameters()

        if self.response_schemas:
            operations_dict = {}
            for status_code in self.response_schemas:
                schema = self.response_schemas[status_code]
                schema_name = schema.__class__.__name__
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

    def generate_parameters(self):

        def _observed_name(key):
            field = schema._declared_fields[key]
            return getattr(field, "load_from", None) or key

        parameter_list = []
        for parameter_in in ['path', 'querystring', 'headers']:
            schema = self.find_schema_for(parameter_in)
            if schema:
                parameter_list += [
                    {
                        'name': _observed_name(key),
                        'in': parameter_in,
                        'required': schema._declared_fields[key].required,
                        'schema': self.get_type_from_field(schema._declared_fields[key]),
                        'description': schema.__doc__ or ""
                    }
                    for key in schema._declared_fields
                ]
        if parameter_list:
            self.view_operations[self.method.lower()].update({'parameters': parameter_list})

    def generate_request_body(self):
        body_schema = self.find_schema_for('body')
        if body_schema:
            request_body_dict = {
                'content': {
                    self.content_type: {
                        'schema': {
                            '$ref': "#/components/schemas/{}".format(body_schema.__name__)
                        }
                    }
                }
            }
            self.view_operations[self.method.lower()].update({'requestBody': request_body_dict})

    @staticmethod
    def get_type_from_field(field):
        field_name = field.__class__.__name__
        convert_marshmallow_to_data_type = {
            'UUID': {"type": "string", "format": "uuid"},
            'Number': {"type": "number"},
            'Integer': {"type": "integer"},
            'Decimal': {"type": "number"},
            'Boolean': {"type": "boolean"},
            'Float': {"type": "number", "format": "float"},
            'DateTime': {"type": "string", "format": "date-time"},
            'LocalDateTime': {"type": "string", "format": "date-time"},
            'Time': {"type": "string", "format": "time"},
            'Date': {"type": "string", "format": "date"},
            'Email': {"type": "string", "format": "email"},
            'Bool': {"type": "boolean"},
            'Int': {"type": "integer"}
        }
        return convert_marshmallow_to_data_type.get(field_name, {"type": "string"})


