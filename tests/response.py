#!/usr/bin/env python

import unittest
import sys
sys.path.insert(0, '..')
from response import Response

class TestResponse(unittest.TestCase):
    
    def setUp(self):
        self.response_template = \
            'HTTP/1.0 %s\r\n' \
            '%s\r\n\r\n' \
            '%s'
    
    def test_200_response(self):
        body = 'test response body'
        headers = {'Content-length': str(len(body)), 'Foo': 'bar', 'Baz': 'Quux'}
        headers_string = '\r\n'.join([': '.join([header, headers[header]]) for header in headers])
        response = Response(status=200, headers=headers, body=body)
        
        self.assertEqual(response.raw(), self.response_template % ('200 OK', headers_string, body))
    
if __name__ == '__main__':
    unittest.main()
