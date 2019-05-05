Cornice Swagger API
###################

Here you may find information about the Cornice Swagger internals and methods that
may be overwritten by applications.

Basic Generator
===============

.. py:module:: cornice_apispec

.. autoclass:: cornice_apispec.swagger.CorniceSwagger
    :members:
    :member-order: bysource

cornice_enable_openapi_view directive
=====================================

.. py:module:: cornice_apispec

.. autofunction:: cornice_apispec.cornice_enable_openapi_view


cornice_enable_openapi_explorer directive
=========================================

.. py:module:: cornice_apispec

.. autofunction:: cornice_apispec.cornice_enable_openapi_explorer


Generator Internals
===================

.. automethod:: cornice_apispec.swagger.CorniceSwagger._build_paths
.. automethod:: cornice_apispec.swagger.CorniceSwagger._extract_path_from_service
.. automethod:: cornice_apispec.swagger.CorniceSwagger._extract_operation_from_view

Section Handlers
================

Swagger definitions and parameters are handled in separate classes. You may overwrite
those if you want to change the converters behaviour.


.. autoclass:: cornice_apispec.swagger.DefinitionHandler
.. automethod:: cornice_apispec.swagger.DefinitionHandler.__init__
.. automethod:: cornice_apispec.swagger.DefinitionHandler.from_schema
.. automethod:: cornice_apispec.swagger.DefinitionHandler._ref_recursive

.. autoclass:: cornice_apispec.swagger.ParameterHandler
.. automethod:: cornice_apispec.swagger.ParameterHandler.__init__
.. automethod:: cornice_apispec.swagger.ParameterHandler.from_schema
.. automethod:: cornice_apispec.swagger.ParameterHandler.from_path
.. automethod:: cornice_apispec.swagger.ParameterHandler._ref

.. autoclass:: cornice_apispec.swagger.ResponseHandler
.. automethod:: cornice_apispec.swagger.ResponseHandler.__init__
.. automethod:: cornice_apispec.swagger.ResponseHandler.from_schema_mapping
.. automethod:: cornice_apispec.swagger.ResponseHandler._ref

Colander converters
===================

You may use the ``cornice_apispec.converters`` submodule to access the colander
to swagger request and schema converters. These may be also used without
``cornice_apispec`` generators.

.. automodule:: cornice_apispec.converters
.. autofunction:: cornice_apispec.converters.convert_schema
.. autofunction:: cornice_apispec.converters.convert_parameter
