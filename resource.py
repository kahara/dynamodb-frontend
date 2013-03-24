from response import HTTPResponse
import boto.dynamodb

class Resource(object):
    connection = None
    tables = {}
    
    def __init__(self, request):
        self.request = request
        self.response = None
        
        if not self.connection:
            self.connection =  boto.dynamodb.connect_to_region('eu-west-1')
        
        if not self.resource_name in self.tables:
            self.tables[self.resource_name] = self.connection.get_table('reader-dev-' + self.resource_name)
        
        getattr(self, {
                'GET': 'do_get',
                'POST': 'do_post',
                'PUT': 'do_put',
                'DELETE': 'do_delete',
                }[self.request.method.upper()])()
        
class UserResource(Resource):
    resource_name = 'user'
    
    def do_get(self):
        self.response = HTTPResponse(status=200, headers={'foo': 'bar', 'baz': 'quux'}, body='GET user')
    
    def do_post(self):
        self.response = HTTPResponse(status=200, headers={'foo': 'bar', 'baz': 'quux'}, body='POST user')
    
class SessionResource(Resource):
    resource_name = 'session'

    def do_get(self):
        self.response = HTTPResponse(status=200, headers={'foo': 'bar', 'baz': 'quux'}, body='GET session')
    
    def do_post(self):
        self.response = HTTPResponse(status=200, headers={'foo': 'bar', 'baz': 'quux'}, body='POST session')
