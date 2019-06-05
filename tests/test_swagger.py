import unittest
import mock

from cornice.validators import marshmallow_validator, marshmallow_body_validator
from cornice.service import Service
from flex.core import validate

from cornice_apispec.swagger import CorniceSwagger
from cornice_apispec.exceptions import CorniceSwaggerException

from .support._marshmallow import GetRequestSchema, PutRequestSchema, HeaderSchema, BodySchema, response_schemas


class CorniceSwaggerGeneratorTest(unittest.TestCase):

    def setUp(self):
        service = Service("IceCream", "/icecream/{flavour}")

        class IceCream(object):
            @service.get(validators=(marshmallow_validator,),
                         schema=GetRequestSchema(),
                         response_schemas=response_schemas)
            def view_get(self, request):
                """Serve ice cream"""
                return self.request.validated

            @service.put(validators=(marshmallow_validator,), schema=PutRequestSchema())
            def view_put(self, request):
                """Add flavour"""
                return self.request.validated

        self.service = service
        CorniceSwagger.services = [self.service]
        CorniceSwagger.api_title = 'IceCreamAPI'
        CorniceSwagger.api_version = '4.2'
        self.swagger = CorniceSwagger()
        self.spec = self.swagger.generate()
        validate(self.spec)

    def test_path(self):
        self.assertIn('/icecream/{flavour}', self.spec['paths'])

    def test_path_methods(self):
        path = self.spec['paths']['/icecream/{flavour}']
        self.assertIn('get', path)
        self.assertIn('put', path)

    def test_summary_docstrings(self):
        self.swagger.summary_docstrings = True
        self.spec = self.swagger.generate()
        validate(self.spec)
        summary = self.spec['paths']['/icecream/{flavour}']['get']['summary']
        self.assertEquals(summary, 'Serve ice cream')

    def test_summary_docstrings_with_klass(self):
        class TemperatureCooler(object):
            def put_view(self):
                """Put it."""
                pass

        service = Service(
            "TemperatureCooler", "/freshair", klass=TemperatureCooler)
        service.add_view("put", "put_view")
        CorniceSwagger.services = [service]
        self.swagger = CorniceSwagger()
        self.spec = self.swagger.generate()
        validate(self.spec)

    def test_with_schema_ref(self):
        swagger = CorniceSwagger([self.service], def_ref_depth=1)
        spec = swagger.generate()
        validate(spec)
        self.assertIn('components', spec)

    def test_with_param_ref(self):
        swagger = CorniceSwagger([self.service], param_ref=True)
        spec = swagger.generate()
        validate(spec)
        self.assertIn('parameters', spec['components'])

    def test_with_resp_ref(self):
        swagger = CorniceSwagger([self.service], resp_ref=True)
        spec = swagger.generate()
        validate(spec)
        self.assertIn('responses', spec['components'])


class ExtractContentTypesTest(unittest.TestCase):

    def test_unkown_renderer(self):
        service = Service("IceCream", "/icecream/{flavour}")

        class IceCream(object):
            @service.get(renderer='')
            def view_get(self, request):
                return self.request.validated

        swagger = CorniceSwagger([service])
        spec = swagger.generate()
        self.assertNotIn('produces', spec['paths']['/icecream/{flavour}']['get'])

    def test_no_ctype_no_list_with_none(self):
        service = Service("IceCream", "/icecream/{flavour}")

        class IceCream(object):
            @service.put()
            def view_put(self, request):
                return self.request.validated

        swagger = CorniceSwagger([service])
        spec = swagger.generate()
        self.assertNotIn('consumes', spec['paths']['/icecream/{flavour}']['put'])

    def test_multiple_ctypes(self):
        service = Service("IceCream", "/icecream/{flavour}")

        class IceCream(object):
            @service.put(schema=BodySchema, content_type=('application/json', 'text/xml'))
            def view_put(self, request):
                return self.request.validated

        swagger = CorniceSwagger([service])
        spec = swagger.generate()
        self.assertEquals([k for k in spec['paths']['/icecream/{flavour}']['put']['requestBody']['content'].keys()],
                          ['application/json', 'text/xml'])


class ExtractTagsTest(unittest.TestCase):

    def test_service_defined_tags(self):
        service = Service("IceCream", "/icecream/{flavour}", tags=['yum'])

        class IceCream(object):
            @service.get()
            def view_get(self, request):
                return service

        swagger = CorniceSwagger([service])
        spec = swagger.generate()
        validate(spec)
        tags = spec['paths']['/icecream/{flavour}']['get']['tags']
        self.assertEquals(tags, ['yum'])

    def test_view_defined_tags(self):
        service = Service("IceCream", "/icecream/{flavour}")

        class IceCream(object):
            @service.get(tags=['cold', 'foo'])
            def view_get(self, request):
                return service

        swagger = CorniceSwagger([service])
        spec = swagger.generate()
        validate(spec)
        tags = spec['paths']['/icecream/{flavour}']['get']['tags']
        self.assertEquals(tags, ['cold', 'foo'])

    def test_both_defined_tags(self):
        service = Service("IceCream", "/icecream/{flavour}", tags=['yum'])

        class IceCream(object):
            @service.get(tags=['cold', 'foo'])
            def view_get(self, request):
                return service

        swagger = CorniceSwagger([service])
        spec = swagger.generate()
        validate(spec)
        tags = spec['paths']['/icecream/{flavour}']['get']['tags']
        self.assertEquals(tags, ['yum', 'cold', 'foo'])

    def test_invalid_view_tag_raises_exception(self):
        service = Service("IceCream", "/icecream/{flavour}")

        class IceCream(object):
            @service.get(tags='cold')
            def view_get(self, request):
                return service

        swagger = CorniceSwagger([service])
        self.assertRaises(CorniceSwaggerException, swagger.generate)

    def test_invalid_service_tag_raises_exception(self):
        service = Service("IceCream", "/icecream/{flavour}", tags='cold')

        class IceCream(object):
            @service.get()
            def view_get(self, request):
                return service

        swagger = CorniceSwagger([service])
        self.assertRaises(CorniceSwaggerException, swagger.generate)


class ExtractOperationIdTest(unittest.TestCase):

    def test_view_defined_operation_id(self):
        service = Service("IceCream", "/icecream/{flavour}")

        @service.get(operation_id='serve_icecream')
        def view_get(self, request):
            return service

        swagger = CorniceSwagger([service])
        spec = swagger.generate()
        validate(spec)
        op_id = spec['paths']['/icecream/{flavour}']['get']['operationId']
        self.assertEquals(op_id, 'serve_icecream')

    def test_default_operation_ids(self):
        service = Service("IceCream", "/icecream/{flavour}")

        @service.get()
        def view_get(self, request):
            return service

        @service.put()
        def view_put(self, request):
            return service

        def op_id_generator(service, method):
            return '%s_%s' % (method.lower(), service.path.split('/')[-2])

        swagger = CorniceSwagger([service])
        swagger.default_op_ids = op_id_generator
        spec = swagger.generate()
        validate(spec)
        op_id = spec['paths']['/icecream/{flavour}']['get']['operationId']
        self.assertEquals(op_id, 'get_icecream')
        op_id = spec['paths']['/icecream/{flavour}']['put']['operationId']
        self.assertEquals(op_id, 'put_icecream')

    def test_invalid_default_opid_raises_exception(self):
        service = Service("IceCream", "/icecream/{flavour}")

        @service.get()
        def view_get(self, request):
            return service

        swagger = CorniceSwagger([service])
        swagger.default_op_ids = "foo"
        self.assertRaises(CorniceSwaggerException, swagger.generate)


class NotInstantiatedSchemaTest(unittest.TestCase):

    def test_not_instantiated(self):
        service = Service("IceCream", "/icecream/{flavour}")

        class IceCream(object):
            """
            Ice cream service
            """

            # Use GetRequestSchema and ResponseSchemas classes instead of objects
            @service.get(validators=(marshmallow_validator,),
                         schema=GetRequestSchema)
            def view_get(self, request):
                """Serve icecream"""
                return self.request.validated

            @service.put(validators=(marshmallow_validator,), schema=PutRequestSchema())
            def view_put(self, request):
                """Add flavour"""
                return self.request.validated

        self.service = service
        self.swagger = CorniceSwagger([self.service])
        self.spec = self.swagger.generate()
        validate(self.spec)
