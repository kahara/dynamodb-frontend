#!/usr/bin/env python                                                                                                                                                   

import unittest, json, sys, boto.dynamodb
sys.path.insert(0, '..')
from request import Request
from tag_resource import TagResource

class TestTagResource(unittest.TestCase):
    def test_tag(self):
        pass

if __name__ == '__main__':
    unittest.main()
