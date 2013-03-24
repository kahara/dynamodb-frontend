from response import HTTPResponse
import boto.dynamodb
from boto.dynamodb.condition import *
from auth import hash, generate_key, salt_string, check_salted
import json
import sys, traceback

class Resource(object):
    connection = None
    tables = {}
    
    def __init__(self, request):
        self.request = request
        self.response = None
        
        if not self.connection:
            self.connection =  boto.dynamodb.connect_to_region('eu-west-1')
        
        if not self.tables:
            for resource_name in ['user', 'session']:
                self.tables[resource_name] = self.connection.get_table('reader-dev-' + resource_name)
        
        try:
            getattr(self, {
                    'GET': 'do_get',
                    'POST': 'do_post',
                    'PUT': 'do_put',
                    'DELETE': 'do_delete',
                    }[self.request.method.upper()])()
        except:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            print traceback.format_exception(exc_type, exc_value, exc_traceback)
            
            self.response = HTTPResponse(status=405)

class UserResource(Resource):
    resource_name = 'user'
    
    def do_get(self):        
        self.response = HTTPResponse(status=200, headers={'foo': 'bar', 'baz': 'quux'}, body='GET user')
    
    def do_post(self):
        self.response = HTTPResponse(status=200, headers={'foo': 'bar', 'baz': 'quux'}, body='POST user')
    
class SessionResource(Resource):
    resource_name = 'session'
    
    def do_get(self):
        print self.request.session_id
        session = self.tables['session'].get_item(hash_key=self.request.session_id)
        print session
        self.response = HTTPResponse(status=200, headers={'foo': 'bar', 'baz': 'quux'}, body='GET session')
    
    def do_post(self):
        credentials = json.loads(self.request.body)
        
        user = self.tables['user'].get_item(hash_key=credentials['username'])
        if not check_salted(credentials['password'], user['password']):
            self.response = HTTPResponse(status=401)
            return
        
        session_id = generate_key()
        attrs = { 'user': user['id'] }
        session = self.tables['session'].new_item(hash_key=session_id, attrs=attrs)
        session.put()
        
        cookie = 'session_id=%s; Expires=Tue, 31-Dec-2019 23:59:59 GMT' % (session_id, )
        self.response = HTTPResponse(status=200, headers={'Set-Cookie': cookie }, body='POST session')
