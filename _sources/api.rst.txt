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

.. automethod:: cornice_apispec.swagger.helpers.SchemasHelper
.. automethod:: cornice_apispec.swagger.helpers.ResponseHelper


Section Plugins
================

Swagger definitions and parameters are handled in separate classes. You may overwrite
those if you want to change the converters behaviour.


.. autoclass:: cornice_apispec.plugins.cornice.CornicePlugin
.. automethod:: cornice_apispec.plugins.cornice.CornicePlugin.__init__
.. automethod:: cornice_apispec.plugins.cornice.CornicePlugin.path_helper
.. automethod:: cornice_apispec.plugins.cornice.CornicePlugin.parameter_helper
.. automethod:: cornice_apispec.plugins.cornice.CornicePlugin.response_helper

