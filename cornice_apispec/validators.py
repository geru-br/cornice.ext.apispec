from cornice.validators import colander_body_validator, colander_headers_validator, colander_path_validator, \
    colander_querystring_validator, colander_validator, marshmallow_body_validator, marshmallow_headers_validator, \
    marshmallow_path_validator, marshmallow_querystring_validator, marshmallow_validator

apispec_marshmallow_validator = marshmallow_validator
setattr(apispec_marshmallow_validator, 'location', 'all')

apispec_marshmallow_body_validator = marshmallow_body_validator
setattr(apispec_marshmallow_body_validator, 'location', 'body')

apispec_marshmallow_headers_validator = marshmallow_headers_validator
setattr(apispec_marshmallow_headers_validator, 'location', 'headers')

apispec_marshmallow_path_validator = marshmallow_path_validator
setattr(apispec_marshmallow_path_validator, 'location', 'path')

apispec_marshmallow_querystring_validator = marshmallow_querystring_validator
setattr(apispec_marshmallow_querystring_validator, 'location', 'querystring')

apispec_colander_validator = colander_validator
setattr(apispec_colander_validator, 'location', 'all')

apispec_colander_body_validator = colander_body_validator
setattr(apispec_colander_body_validator, 'location', 'body')

apispec_colander_headers_validator = colander_headers_validator
setattr(apispec_colander_headers_validator, 'location', 'headers')

apispec_colander_path_validator = colander_path_validator
setattr(apispec_colander_path_validator, 'location', 'path')

apispec_colander_querystring_validator = colander_querystring_validator
setattr(apispec_colander_querystring_validator, 'location', 'querystring')
