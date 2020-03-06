import inspect
import hashlib


def get_schema_name(schema):

    if inspect.isclass(schema):
        return schema.__name__
    else:

        if hasattr(schema, '__apispec__') and schema.__apispec__.get('model'):
            return schema.__apispec__.get('model')

        if 'exclude' in schema.__dict__:
            key = "{}".format(list(schema.__dict__.get('exclude'))).encode('utf-8')

            return "{}-{}".format(schema.__class__.__name__, hashlib.md5(key).hexdigest()[:5])
        else:
            return schema.__class__.__name__


def add_schema_in_spec(spec, schema):
    from apispec.exceptions import DuplicateComponentNameError
    try:
        spec.components.schema(get_schema_name(schema), schema=schema)
    except DuplicateComponentNameError:
        pass
