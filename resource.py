from multiprocessing import current_process
from response import HTTPResponse
import boto.dynamodb

class Resource(object):
    connection = None
    tables = {}
    
    def __init__(self, request):
        self.request = request
        self.response = None

        self.pid = current_process().pid
        if not self.connection:
            self.connection =  boto.dynamodb.connect_to_region('eu-west-1')
        
        if not self.resource_name in self.tables:
            self.tables[self.resource_name] = self.connection.get_table('reader-dev-' + self.resource_name)
        
        self.handle()
            
class UserResource(Resource):
    resource_name = 'user'
    def handle(self):
        print self.pid
        print self.connection
        print self.tables
        self.response = HTTPResponse(status=200, headers={'foo': 'bar', 'baz': 'quux'}, body='i am the walrus')

class SessionResource(Resource):
    resource_name = 'session'
    def handle(self):
        print self.pid
        print self.connection
        print self.tables
        self.response = HTTPResponse(status=200, headers={'foo': 'bar', 'baz': 'quux'}, body='i am the walrus')
