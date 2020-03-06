import re

from apispec.yaml_utils import load_operations_from_docstring, load_yaml_from_docstring
from pyramid_apispec.helpers import ALL_METHODS, is_string

from cornice_apispec.autodoc import AutoDoc
from cornice_apispec.utils import add_schema_in_spec


def get_operations(spec, uri_pattern, view, operations, show_head, show_options, cornice_service, autodoc=True):
    if operations is not None:
        return operations

    operations = {}

    # views can be class based
    if view.get("attr"):
        global_meta = load_operations_from_docstring(view["callable"].__doc__)
        if global_meta:
            operations.update(global_meta)
        f_view = getattr(view["callable"], view["attr"])
    # or just function callables
    else:
        f_view = view.get("callable")

    methods = view.get("request_methods")
    view_operations = load_operations_from_docstring(f_view.__doc__)
    if not view_operations:
        view_operations = {}
        if is_string(methods):
            methods = [methods]
        if not methods:
            methods = ALL_METHODS[:]
        if 'HEAD' in methods and not show_head:
            methods.remove('HEAD')
        if 'OPTIONS' in methods and not show_options:
            methods.remove('OPTIONS')
        operation = load_yaml_from_docstring(f_view.__doc__)
        if operation:
            for method in methods:
                view_operations[method.lower()] = operation
        elif autodoc:
            path_parameters = get_uri_placeholders(uri_pattern)
            for method in methods:
                auto_doc = AutoDoc(method, view, cornice_service)
                if path_parameters:
                    auto_doc.add_path_parameter(path_parameters)
                request_schema = auto_doc.find_schema_for('body')
                if request_schema:
                    add_schema_in_spec(spec, request_schema)
                view_operations = auto_doc.to_dict()

    operations.update(view_operations)

    return operations


def get_uri_placeholders(uri_pattern):
    """pattern: {any}"""
    return re.findall('\{(.*?)\}', uri_pattern)
