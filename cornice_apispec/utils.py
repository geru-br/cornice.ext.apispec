from collections import OrderedDict

def get_schema_cls(schema):
    # TODO Find a better way probably using dispatch to work with diferent serializers
    if hasattr(schema, '__name__'):
        # Is a class
        return schema
    else:
        # Is a instance
        return schema.__class__


def get_schema_name(schema):
    """
    Instances dont have __name__ attribute
    :param schema:
    :return:
    """
    return get_schema_cls(schema).__name__


def remove_duplicates(l):
    """
    Remove duplicate items from list keeping the order
    """
    return list(OrderedDict.fromkeys(l))

