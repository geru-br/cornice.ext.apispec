"""
This module handles the conversion between colander object schemas and swagger
object schemas.
"""

from cornice_apispec.converters.schema import TypeConversionDispatcher
from cornice_apispec.converters.parameters import ParameterConversionDispatcher


def convert_schema(schema_node):

    dispatcher = TypeConversionDispatcher()
    converted = dispatcher(schema_node)

    return converted


def convert_parameter(location, schema_node, definition_handler=convert_schema):

    dispatcher = ParameterConversionDispatcher(definition_handler)
    converted = dispatcher(location, schema_node)

    return converted
