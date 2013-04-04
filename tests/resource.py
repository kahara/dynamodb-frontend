#!/usr/bin/env python                                                                                                                                                   

import unittest
import sys
sys.path.insert(0, '..')
from resource import Resource
from request import Request

class TestResource(unittest.TestCase):

    def setUp(self):
        request_template = \
            '%s %s %s\r\n' \
            'User-Agent: test user agent\r\n' \
            'Host: testhost.com\r\n' \
            'Accept: test/mimetype\r\n\r\n' \
            '%s'
        
        request = Request(request_template % ('GET', '/', 'HTTP/1.0', ''))
        self.resource = Resource(request)
        
    def test_tables(self):
        for table_name in ['user', 'email', 'username', 'reset', 'activation', 'session', 'feed', 'feeditem', 'subscription', 'subscriptionitem']:
            self.assertEqual(str(self.resource.tables[table_name]), 'Table(%s)' % table_name)
    
if __name__ == '__main__':
    unittest.main()
