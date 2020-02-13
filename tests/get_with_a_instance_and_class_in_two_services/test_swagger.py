

def test_api(app):

    response = app.get('/users-1', status=200)
    assert response.text == '{"name": "Name"}'


def test_swagger(app):

    response = app.get('/api-info')

    expected = {'paths': {'/users-1': {'get': {'responses': {'200': {'description': '', 'content': {'text/plain': {'schema': {'$ref': '#/components/schemas/Schema'}}}}}}}, '/users-2': {'get': {'responses': {'200': {'description': '', 'content': {'text/plain': {'schema': {'$ref': '#/components/schemas/Schema-2'}}}}}}}}, 'info': {'title': 'My API', 'version': '1.0.0', 'description': 'Main description for API'}, 'tags': [{'tag': 'My Tag', 'description': 'Tag description'}], 'openapi': '3.0.2', 'components': {'schemas': {'Schema': {'type': 'object', 'properties': {'age': {'type': 'string'}, 'name': {'type': 'string'}}, 'required': ['age', 'name']}, 'Schema-2': {'type': 'object', 'properties': {'name': {'type': 'string'}}, 'required': ['name']}}}, 'servers': [{'url': 'http://localhost:80'}]}
    assert response.json == expected
