#!/usr/bin/env python                                                                                                                                                   

import unittest
import json
import sys
sys.path.insert(0, '..')
from request import Request
from resource import SessionResource

class TestSessionResource(unittest.TestCase):
    def setUp(self):
        # XXX create test user account
        pass
    
    def tearDown(self):
        # XXX remove created test user account
        pass

    def test_post(self):
        body = json.dumps({'login': 'kahara', 'password': 'foo'})
        request = Request('POST /session/ HTTP/1.0\r\nAccept: application/json\r\n\r\n%s' % (body, ))
        resource = SessionResource(request)
        session_id = resource.response.headers['Set-Cookie'].split(' ')[0]
        
        request = Request('GET /session/ HTTP/1.0\r\nAccept: application/json\r\nCookie: %s\r\n\r\n' % (session_id, ))
        resource = SessionResource(request)
        body = json.loads(resource.response.body)
        
        self.assertEqual(body['username'], 'kahara')
        self.assertEqual(body['email'], 'joni.kahara@gmail.com')
        
if __name__ == '__main__':
    unittest.main()
