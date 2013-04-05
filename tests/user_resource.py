#!/usr/bin/env python                                                                                                                                                   

import unittest, json, sys, boto.dynamodb
from boto.dynamodb.condition import *
sys.path.insert(0, '..')
from request import Request
from user_resource import UserResource
from auth import generate_key, hash_password

class TestUserResource(unittest.TestCase):
    def setUp(self):
        self.username = 'thisisatestuser'
        self.email = 'joni.kahara+thisisansestestemail@gmail.com'
        self.password = 'thisisatestpassword'
        
        self.connection =  boto.dynamodb.connect_to_region('eu-west-1')
        
        try:
            username_item = self.connection.get_table('username').get_item(hash_key=self.username)
            self.connection.get_table('user').get_item(hash_key=username_item['user']).delete()
            username_item.delete()
        except: pass
        try: self.connection.get_table('email').get_item(hash_key=self.email).delete()
        except: pass
    
    def tearDown(self):
        try:
            username_item = self.connection.get_table('username').get_item(hash_key=self.username)
            self.connection.get_table('user').get_item(hash_key=username_item['user']).delete()
            username_item.delete()
        except: pass
        try: self.connection.get_table('email').get_item(hash_key=self.email).delete()
        except: pass
        
        try: list(self.connection.get_table('activation').scan(scan_filter={'email': EQ(self.email)}))[0].delete()
        except: pass
        
        try: list(self.connection.get_table('reset').scan(scan_filter={'email': EQ(self.email)}))[0].delete()
        except: pass
        
    def test_user(self):
        
        # test account activation
        body = json.dumps({'username': self.username, 'email': self.email, 'password': self.password})
        request = Request('POST /user/ HTTP/1.0\r\nAccept: application/json\r\n\r\n%s' % (body, ))
        resource = UserResource(request)
        
        activation_item = list(self.connection.get_table('activation').scan(scan_filter={'email': EQ(self.email)}))[0]

        self.assertEqual(activation_item['email'], self.email)
        self.assertEqual(activation_item['username'], self.username)
        
        activation_id = activation_item['id']
        request = Request('POST /user/activation/%s HTTP/1.0\r\nAccept: application/json\r\n\r\n' % (activation_id, ))
        resource = UserResource(request)
        
        username_item = self.connection.get_table('username').get_item(hash_key=self.username)
        user_item = self.connection.get_table('user').get_item(hash_key=username_item['user'])
        self.assertEqual(user_item['email'], self.email)
        self.assertEqual(user_item['username'], self.username)
        self.assertTrue(self.password, user_item['password'])
        
        # test password reset
        body = json.dumps({'email': self.email})
        request = Request('POST /user/reset/ HTTP/1.0\r\nAccept: application/json\r\n\r\n%s' % (body, ))
        resource = UserResource(request)
        
        self.password = self.password + '1234'
        
        body = json.dumps({'password': self.password})
        reset_item = list(self.connection.get_table('reset').scan(scan_filter={'email': EQ(self.email)}))[0]
        reset_id = reset_item['id']
        request = Request('POST /user/reset/%s HTTP/1.0\r\nAccept: application/json\r\n\r\n%s' % (reset_id, body))
        resource = UserResource(request)
        
        user_item = self.connection.get_table('user').get_item(hash_key=username_item['user'])
        self.assertEqual(user_item['email'], self.email)
        self.assertEqual(user_item['username'], self.username)
        self.assertTrue(self.password, user_item['password'])
        
if __name__ == '__main__':
    unittest.main()
