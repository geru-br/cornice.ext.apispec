import inspect
import hashlib


def get_schema_name(schema):

    if inspect.isclass(schema):
        return schema.__name__
    else:

        if hasattr(schema, '__apispec__') and schema.__apispec__.get('model'):
            return schema.__apispec__.get('model')

        if 'exclude' in schema.__dict__:
            key = "{}".format(schema.__dict__.get('exclude')).encode()

            return "{}-{}".format(schema.__class__.__name__, hashlib.sha256(key).hexdigest()[:5])
        else:
            return schema.__class__.__name__
