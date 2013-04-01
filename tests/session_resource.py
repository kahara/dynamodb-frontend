#!/usr/bin/env python                                                                                                                                                   

import unittest, json, sys, boto.dynamodb
sys.path.insert(0, '..')
from request import Request
from session_resource import SessionResource
from auth import generate_key, hash_password

class TestSessionResource(unittest.TestCase):
    def setUp(self):
        self.userid = generate_key()
        self.username = 'thisisatestuser'
        self.email = 'thisisatestemail@example.com'
        self.password = 'thisisatestpassword'
        
        connection =  boto.dynamodb.connect_to_region('eu-west-1')
        
        try:
            username_item = connection.get_table('username').get_item(hash_key=self.username)
            connection.get_table('user').get_item(hash_key=username_item['user']).delete()
            username_item.delete()
        except: pass
        try: connection.get_table('email').get_item(hash_key=self.email).delete()
        except: pass
        
        connection.get_table('user').new_item(
            hash_key=self.userid,
            attrs={
                'username': self.username,
                'email': self.email,
                'password': hash_password(self.password),
                }
            ).put()
        
        connection.get_table('username').new_item(
            hash_key=self.username,
            attrs={
                'user': self.userid,
                }
            ).put()
        
        connection.get_table('email').new_item(
            hash_key=self.email,
            attrs={
                'user': self.userid,
                }
            ).put()
        
    def tearDown(self):
        connection =  boto.dynamodb.connect_to_region('eu-west-1')
        
        connection.get_table('user').get_item(hash_key=self.userid).delete()
        username_table = connection.get_table('username').get_item(hash_key=self.username).delete()
        email_table = connection.get_table('email').get_item(hash_key=self.email).delete()
        
    def test_session(self):
        
        body = json.dumps({'login': self.username, 'password': self.password})
        request = Request('POST /session/ HTTP/1.0\r\nAccept: application/json\r\n\r\n%s' % (body, ))
        resource = SessionResource(request)
        session_id = resource.response.headers['Set-Cookie'].split(' ')[0]
        
        request = Request('GET /session/ HTTP/1.0\r\nAccept: application/json\r\nCookie: %s\r\n\r\n' % (session_id, ))
        resource = SessionResource(request)
        body = json.loads(resource.response.body)
        
        self.assertEqual(body['username'], self.username)
        self.assertEqual(body['email'], self.email)
        
        request = Request('DELETE /session/ HTTP/1.0\r\nAccept: application/json\r\nCookie: %s\r\n\r\n' % (session_id, ))
        resource = SessionResource(request)
        
        self.assertEqual(resource.response.status, '204 No Content')
        self.assertEqual(resource.response.body, None)
        
if __name__ == '__main__':
    unittest.main()
