from multiprocessing import current_process
from response import HTTPResponse
import boto.dynamodb

class Resource(object):
    connections = {}
    
    def __init__(self, request):
        self.request = request
        self.response = None

        self.pid = current_process().pid
        if not self.pid in self.connections:
            self.connections[self.pid] = {
                'connection': boto.dynamodb.connect_to_region('eu-west-1'),
                'tables': {}
                }
            
        self.handle()
            
class UserResource(Resource):
    def handle(self):
        if not 'user' in self.connections[self.pid]['tables']:
            self.connections[self.pid]['tables']['user'] = self.connections[self.pid]['connection'].get_table('reader-dev-user')
        
        self.response = HTTPResponse(status=200, headers={'foo': 'bar', 'baz': 'quux'}, body='i am the walrus')

class SessionResource(Resource):
    def handle(self):
        if not 'session' in self.connections[self.pid]['tables']:
            self.connections[self.pid]['tables']['session'] = self.connections[self.pid]['connection'].get_table('reader-dev-session')
        
        self.response = HTTPResponse(status=200, headers={'foo': 'bar', 'baz': 'quux'}, body='i am the walrus')
