from cornice_apispec.constants import DEFAULT_CONTENT_TYPE
from cornice_apispec.utils import get_schema_name

VALIDATOR_FOR_OPEN_API = {
    'querystring': 'query',
    'headers': 'header',
    'path': 'path'
}


class AutoDoc(object):
    """Where magic happens.

    This class will use the introspected view
    to find:

    * View Tags
    * View Request Schema and his location
    * View Response Schemas for each status code
    * View short summary and long description
    """

    def __init__(self, method, introspectable_view, cornice_service):
        """Init class.

        Cornice saves his own @view decorator configurations
        (example: `schema`, `content_type`, etc),
        inside original function view __views__ attribute,
        which is the `callable` key inside the introspectable view.

        :param method: (str) request method
        :param introspectable_view: Pyramid Introspector View instance
        :param cornice_service (Service): cornice service instance
        """
        self.method = method
        self.view = introspectable_view
        self.view_operations = {self.method.lower(): {}}
        self.cornice_service = cornice_service

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
        return self.cornice_service.get_validators(self.method)

    @property
    def content_type(self):
        content_type_info = self.cornice_service.get_contenttypes(self.method)
        return content_type_info[0] if content_type_info[0] else DEFAULT_CONTENT_TYPE

    def _find_request_schema(self):
        return self.cornice_service.filter_argumentlist(self.method, 'schema')[0]

    def add_path_parameter(self, path_parameters):
        parameter_list = []
        for parameter_name in path_parameters:
            parameter_list += [{
                'name': parameter_name,
                'in': 'path',
                'required': True,
                'schema': self.get_type_from_field('String'),
                'description': "{} parameter".format(parameter_name)
            }]
        self._add_parameter(parameter_list)

    def find_schema_for(self, location):
        if location not in ['body', 'headers', 'querystring']:
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

        # assumes the standard request scheme for http methods that contains data in the request body
        contains_body_method = self.method.lower() in ('post', 'patch', 'put', 'delete')
        is_location_body = location == 'body'
        default_request_schema = request_schema if is_location_body and contains_body_method else None

        # No valid cornice validator was found
        # but request_schema exists. In this case,
        # return the nested match schema
        maybe_nested = request_schema._declared_fields.get(location, None)
        return maybe_nested.nested if maybe_nested else default_request_schema

    def to_dict(self):
        self._add_tags()
        self._add_summary()
        self._add_description()
        self._generate_request_body()
        self._generate_parameters()
        self._generate_responses()
        return self.view_operations

    def _generate_responses(self):
        if self.response_schemas:
            responses_dict = {}
            for status_code in self.response_schemas:
                schema = self.response_schemas[status_code]
                schema_name = get_schema_name(schema)
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
                responses_dict.update(status_code_dict)
            # Update current method dict in Operation
            self._add_responses(responses_dict)

    def _generate_parameters(self):

        def _observed_name(key):
            field = schema._declared_fields[key]
            return getattr(field, "load_from", None) or key

        parameter_list = []
        for parameter_in in ['querystring', 'headers']:
            schema = self.find_schema_for(parameter_in)
            if schema:
                parameter_list += [
                    {
                        'name': _observed_name(key),
                        'in': VALIDATOR_FOR_OPEN_API.get(parameter_in, parameter_in),
                        'required': schema._declared_fields[key].required,
                        'schema': self.get_type_from_field(schema._declared_fields[key]),
                        'description': schema.__doc__ or ""
                    }
                    for key in schema._declared_fields
                ]
        if parameter_list:
            self._add_parameter(parameter_list)

    def _generate_request_body(self):
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
            self._add_request_body(request_body_dict)

    def _add_request_body(self, request_body_dict):
        self.view_operations[self.method.lower()].update({'requestBody': request_body_dict})

    def _add_parameter(self, parameter_list):
        found_parameter_list = self.view_operations[self.method.lower()].get('parameters', [])
        for parameter in parameter_list:
            found_parameter_list.append(parameter)
        self.view_operations[self.method.lower()].update({'parameters': found_parameter_list})

    def _add_responses(self, responses_dict):
        self.view_operations[self.method.lower()].update({'responses': responses_dict})

    def _add_tags(self):
        if self.tags:
            self.view_operations[self.method.lower()].update({'tags': self.tags})

    def _add_summary(self):
        if self.summary:
            self.view_operations[self.method.lower()].update({'summary': self.summary})

    def _add_description(self):
        if self.description:
            self.view_operations[self.method.lower()].update({'description': self.description})

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
