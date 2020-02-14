# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function, unicode_literals

def test_api(app):

    response = app.get('/', status=200)
    assert response.text == '{"name": "Name"}'


def test_swagger(app):

    response = app.get('/api-info')

    expected = {'paths': {'/': {'get': {'responses': {'200': {'description': '', 'content': {'text/plain': {'schema': {'$ref': '#/components/schemas/Schema-d7517'}}}}}}}}, 'info': {'title': 'My API', 'version': '1.0.0', 'description': 'Main description for API'}, 'tags': [{'tag': 'My Tag', 'description': 'Tag description'}], 'openapi': '3.0.2', 'components': {'schemas': {'Schema-d7517': {'type': 'object', 'properties': {'name': {'type': 'string'}}, 'required': ['name']}}}, 'servers': [{'url': 'http://localhost:80'}]}

    assert response.json == expected
