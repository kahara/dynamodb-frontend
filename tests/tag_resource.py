#!/usr/bin/env python                                                                                                                                                   

import unittest, json, sys, boto.dynamodb
sys.path.insert(0, '..')
from auth import generate_key, hash_password
from request import Request
from tag_resource import TagResource
from session_resource import SessionResource

class TestTagResource(unittest.TestCase):
    def setUp(self):
        self.userid = generate_key()
        self.username = 'thisisatestuser'
        self.email = 'thisisatestemail@example.com'
        self.password = 'thisisatestpassword'
        self.session_id = None
        
        connection =  boto.dynamodb.connect_to_region('eu-west-1')
        
        try:
            username_item = connection.get_table('username').get_item(hash_key=self.username)
            connection.get_table('user').get_item(hash_key=username_item['user']).delete()
            username_item.delete()
            # XXX scan test user tags and delete them
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
        
        body = json.dumps({'login': self.username, 'password': self.password})
        request = Request('POST /session/ HTTP/1.0\r\nAccept: application/json\r\n\r\n%s' % (body, ))
        resource = SessionResource(request)
        self.session_id = resource.response.headers['Set-Cookie'].split(' ')[0]
        
    def tearDown(self):
        request = Request('DELETE /session/ HTTP/1.0\r\nAccept: application/json\r\nCookie: %s\r\n\r\n' % (self.session_id, ))
        resource = TagResource(request)
        
        connection =  boto.dynamodb.connect_to_region('eu-west-1')        
        connection.get_table('user').get_item(hash_key=self.userid).delete()
        connection.get_table('username').get_item(hash_key=self.username).delete()
        connection.get_table('email').get_item(hash_key=self.email).delete()

    def test_tag(self):
        
        body = json.dumps({'tag': 'test tag', 'tags': ['foo', 'bar'], 'subscriptions': ['1234']})
        request = Request('POST /tag/ HTTP/1.0\r\nAccept: application/json\r\nCookie: %s\r\n\r\n%s' % (self.session_id, body))
        resource = TagResource(request)
        
        expected = '{"tags": {"foo": {"tags": {}, "subscriptions": {}}, "bar": {"tags": {}, "subscriptions": {}}}, "subscriptions": ["1234"]}'
        
        self.assertEqual(resource.response.body, expected)
        
        request = Request('GET /tag/test%%20tag HTTP/1.0\r\nAccept: application/json\r\nCookie: %s\r\n\r\n' % (self.session_id, ))
        resource = TagResource(request)
        
        self.assertEqual(resource.response.body, expected)
        
        request = Request('DELETE /tag/test%%20tag HTTP/1.0\r\nAccept: application/json\r\nCookie: %s\r\n\r\n' % (self.session_id, ))
        resource = TagResource(request)
        
        print resource.response.status
        
        request = Request('GET /tag/test%%20tag HTTP/1.0\r\nAccept: application/json\r\nCookie: %s\r\n\r\n' % (self.session_id, ))
        resource = TagResource(request)
        
        self.assertEqual(resource.response.status, '400 Bad Request')
        
if __name__ == '__main__':
    unittest.main()
