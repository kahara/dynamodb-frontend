from multiprocessing import current_process
from response import HTTPResponse
import boto.dynamodb

class Resource(object):
    connection = None
    tables = {}
    methods = {
        'GET': 'do_get',
        'POST': 'do_post',
        'PUT': 'do_put',
        'DELETE': 'do_delete',
        }
    
    def __init__(self, request):
        self.request = request
        self.response = None

        self.pid = current_process().pid
        if not self.connection:
            self.connection =  boto.dynamodb.connect_to_region('eu-west-1')
        
        if not self.resource_name in self.tables:
            self.tables[self.resource_name] = self.connection.get_table('reader-dev-' + self.resource_name)
        
        getattr(self, self.methods[self.request.method.upper()])()
        
class UserResource(Resource):
    resource_name = 'user'
    
    def do_get(self):
        self.response = HTTPResponse(status=200, headers={'foo': 'bar', 'baz': 'quux'}, body='i am the walrus')
    
    def do_post(self):
        self.response = HTTPResponse(status=200, headers={'foo': 'bar', 'baz': 'quux'}, body='i am the walrus')
    
class SessionResource(Resource):
    resource_name = 'session'

    def do_get(self):
        self.response = HTTPResponse(status=200, headers={'foo': 'bar', 'baz': 'quux'}, body='i am the walrus')
    
    def do_post(self):
        self.response = HTTPResponse(status=200, headers={'foo': 'bar', 'baz': 'quux'}, body='i am the walrus')
