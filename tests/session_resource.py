#!/usr/bin/env python                                                                                                                                                   

import unittest, json, sys, boto.dynamodb
from testbase import TestBase
sys.path.insert(0, '..')
from request import Request
from session_resource import SessionResource

class TestSessionResource(TestBase):
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
