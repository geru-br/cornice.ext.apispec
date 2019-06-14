class SwaggerResponseSchemasPredicate(object):
    def __init__(self, val, config):
        self.val = val

    def text(self):
        return 'response_schemas = %s' % (self.val,)

    phash = text

    def __call__(self, context, request):
        return True


class SwaggerTagsPredicate(object):
    def __init__(self, val, config):
        self.val = val

    def text(self):
        return 'swagger_tags = %s' % (self.val,)

    phash = text

    def __call__(self, context, request):
        return True


class SwaggerSummaryPredicate(object):
    def __init__(self, val, config):
        self.val = val

    def text(self):
        return 'swagger_summary = %s' % (self.val,)

    phash = text

    def __call__(self, context, request):
        return True


class SwaggerDescriptionPredicate(object):
    def __init__(self, val, config):
        self.val = val

    def text(self):
        return 'swagger_description = %s' % (self.val,)

    phash = text

    def __call__(self, context, request):
        return True


class SwaggerShowInPredicate(object):
    def __init__(self, val, config):
        self.val = val

    def text(self):
        return 'swagger_show_in = %s' % (self.val,)

    phash = text

    def __call__(self, context, request):
        return True


class SwaggerValidateForPredicate(object):
    def __init__(self, val, config):
        self.val = val

    def text(self):
        return 'swagger_validate_for = %s' % (self.val,)

    phash = text

    def __call__(self, context, request):
        return True
