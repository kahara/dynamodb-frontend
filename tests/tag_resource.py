#!/usr/bin/env python                                                                                                                                                   
import unittest, json, sys, boto.dynamodb
from testbase import TestBase
sys.path.insert(0, '..')
from auth import generate_key
from request import Request
from tag_resource import TagResource

class TestTagResource(TestBase):
    def test_tag(self):
        body = json.dumps({'tag': 'test tag', 'tags': ['foo', 'bar'], 'subscriptions': ['1234']})
        request = Request('POST /tag/ HTTP/1.0\r\nAccept: application/json\r\nCookie: %s\r\n\r\n%s' % (self.cookie, body))
        resource = TagResource(request)
        
        self.assertEqual(resource.response.status, '201 Created')
        
        request = Request('GET /tag/test%%20tag HTTP/1.0\r\nAccept: application/json\r\nCookie: %s\r\n\r\n' % (self.cookie, ))
        expected = '{"tags": {"foo": {"tags": {}, "subscriptions": {}}, "bar": {"tags": {}, "subscriptions": {}}}, "subscriptions": ["1234"]}'
        self.assertEqual(resource.response.body, expected)
        
        request = Request('DELETE /tag/test%%20tag HTTP/1.0\r\nAccept: application/json\r\nCookie: %s\r\n\r\n' % (self.cookie, ))
        resource = TagResource(request)
        
        print resource.response.status
        
        request = Request('GET /tag/test%%20tag HTTP/1.0\r\nAccept: application/json\r\nCookie: %s\r\n\r\n' % (self.cookie, ))
        resource = TagResource(request)
        
        self.assertEqual(resource.response.status, '400 Bad Request')
        
if __name__ == '__main__':
    unittest.main()
