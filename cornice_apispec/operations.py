from apispec.exceptions import DuplicateComponentNameError
from apispec.yaml_utils import load_operations_from_docstring, load_yaml_from_docstring
from cornice_apispec.autodoc import AutoDoc
from pyramid_apispec.helpers import ALL_METHODS, is_string


def get_operations(spec, view, operations, show_head, show_options, autodoc=True):
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
            for method in methods:
                auto_doc = AutoDoc(method, view)
                request_schema = auto_doc.find_schema_for('body')
                if request_schema:
                    try:
                        spec.components.schema(request_schema.__name__, schema=request_schema)
                    except DuplicateComponentNameError:
                        pass
                view_operations = auto_doc.to_dict()

    operations.update(view_operations)

    return operations
