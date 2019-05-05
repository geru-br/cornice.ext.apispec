"""Cornice Swagger 2.0 documentor helpers"""

def get_parameter_from_path(path):
    path_components = path.split('/')
    param_names = [comp[1:-1] for comp in path_components
                   if comp.startswith('{') and comp.endswith('}')]

    params = []
    for name in param_names:

        params.append(name)

    return params


class SchemasHelper(object):
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

    @property
    def path(self):
        if self._has_cornice_base_validator(self.args.get('validators', [])):
            return self.args.get('schema')().fields['path'].schema.__class__

    def headers(self):
        return []


class ResponseHelper(object):

    def __init__(self, args):
        self.args = args

    @property
    def responses(self):
        ret = []
        for status_code, schema in self.args.get('response_schemas', {}).items():
            component_id = '{}_{}'.format(status_code, schema.__name__)
            ret.append((component_id, status_code, schema,))
        else:
            ret.append(('default', 200, None,))
        return ret