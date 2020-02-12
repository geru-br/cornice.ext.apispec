import inspect


def get_schema_name(schema):

    if inspect.isclass(schema):
        return schema.__name__
    else:
        return schema.__class__.__name__