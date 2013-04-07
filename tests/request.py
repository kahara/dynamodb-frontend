#!/usr/bin/env python

import unittest
import sys, json
sys.path.insert(0, '..')
from request import Request

class TestRequest(unittest.TestCase):
    
    def setUp(self):
        self.request_template = \
            '%s %s %s\r\n' \
            'User-Agent: test user agent\r\n' \
            'Host: testhost.com\r\n' \
            'Accept: test/mimetype\r\n\r\n' \
            '%s'
    
    def test_get(self):
        request = Request(self.request_template % ('GET', '/', 'HTTP/1.0', ''))
        
        self.assertTrue(request.is_valid)
        self.assertEqual(request.method, 'GET')
        self.assertEqual(request.path, [])
        self.assertEqual(request.version, 'HTTP/1.0')
        self.assertEqual(request.headers['User-Agent'], 'test user agent')
        self.assertEqual(request.headers['Host'], 'testhost.com')
        self.assertEqual(request.headers['Accept'], 'test/mimetype')
        self.assertEqual(request.body, None)
    
    def test_get_invalid(self):
        request = Request('GET ///// HTTP/2.0\r\n\r\ni am the walrus')
        self.assertFalse(request.is_valid)

    def test_get_specific(self):
        request = Request(self.request_template % ('GET', '//foobar//1234//', 'HTTP/1.0', ''))
        
        self.assertTrue(request.is_valid)
        self.assertEqual(request.method, 'GET')
        self.assertEqual(request.path, ['foobar', '1234'])
        
    def test_post(self):
        request = Request(self.request_template % ('POST', '/foobar/', 'HTTP/1.0', '["test request body"]'))
        
        self.assertTrue(request.is_valid)
        self.assertEqual(request.method, 'POST')
        self.assertEqual(request.path, ['foobar'])
        self.assertEqual(request.body, ['test request body'])
    
    def test_delete(self):
        request = Request(self.request_template % ('DELETE', '/foobar/1234/', 'HTTP/1.0', ''))
        
        self.assertTrue(request.is_valid)
        self.assertEqual(request.method, 'DELETE')
        self.assertEqual(request.path, ['foobar', '1234'])
    
if __name__ == '__main__':
    unittest.main()
