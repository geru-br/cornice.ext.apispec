.. _quickstart:

Quickstart
##########

Installing
==========

You may install us with pip::

    $ pip install cornice_apispec


From an existing Cornice application, you may add this extension to your
Pyramid configurator after including cornice::

    from pyramid.config import Configurator

    def setup():
        config = Configurator()
        config.include('cornice')
        config.include('cornice_apispec')


You can than create your OpenAPI/Swagger JSON using::


    from cornice_apispec import CorniceSwagger
    from cornice.service import get_services

    my_generator = CorniceSwagger(get_services())
    my_spec = my_generator('MyAPI', '1.0.0')


Alternatively you can use a directive to set up OpenAPI/Swagger JSON and
serve API explorer on your application::


    config = Configurator()
    config.include('cornice')
    config.include('cornice_apispec')
    config.cornice_enable_openapi_view(
        api_path='/api-explorer/swagger.json',
        title='MyAPI',
        description="OpenAPI documentation",
        version='1.0.0'
    )
    config.cornice_enable_openapi_explorer(
        api_explorer_path='/api-explorer')

Then you will be able to access Swagger UI API explorer on url:

http://localhost:8000/api-explorer (in the example above)

Using a scaffold
================

TODO: Build a cookiecutter


Show me a minimalist useful example
===================================

.. literalinclude:: ../../examples/minimalist.py
    :language: python


The resulting `swagger.json` at `http://localhost:8000/__api__` is:

.. code-block:: json

    {
      "info": {
        "title": "MyAPI",
        "version": "1.0.0"
      },
      "paths": {
        "/api/v1/resource": {
          "post": {
            "description": null,
            "tags": [
              "resources"
            ],
            "requestBody": {
              "content": {
                "application/json": {
                  "schema": {
                    "$ref": "#/components/schemas/PostSchema"
                  }
                }
              }
            },
            "parameters": [

            ],
            "responses": {
              "200": {
                "$ref": "#/components/responses/default"
              }
            }
          }
        },
        "/api/v1/resource/{uuid}": {
          "get": {
            "description": null,
            "tags": [
              "resources"
            ],
            "parameters": [
              {
                "$ref": "#/components/parameters/uuid"
              }
            ],
            "responses": {
              "200": {
                "$ref": "#/components/responses/default"
              }
            }
          }
        }
      },
      "tags": [
        {
          "name": "resources",
          "description": null
        },
        {
          "name": "resources",
          "description": null
        }
      ],
      "openapi": "3.0.2",
      "components": {
        "schemas": {
          "PostSchema": {
            "type": "object",
            "properties": {
              "title": {
                "type": "string"
              },
              "id": {
                "type": "string",
                "readOnly": true
              }
            }
          }
        },
        "parameters": {
          "uuid": {
            "name": "uuid",
            "in": "path",
            "content": {
              "text/plain": {
                "schema": {
                  "type": "string"
                }
              }
            },
            "required": true
          }
        },
        "responses": {
          "default": {
            "description": "Default Response",
            "content": {
              "text/plain": {
                "schema": {
                  "type": "string"
                }
              }
            }
          }
        }
      }
    }