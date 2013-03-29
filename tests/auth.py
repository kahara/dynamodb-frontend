#!/usr/bin/env python

import unittest
import sys
sys.path.insert(0, '..')
from auth import generate_key, hash_password, check_password, cookie

class TestAuth(unittest.TestCase):
    
    def setUp(self):
        self.correct = 'soylent green is made of people'
        self.incorrect = self.correct + 'x'
        
    def test_key_generation(self):
        key1 = generate_key()
        self.assertTrue(len(key1) > 0)
        
        key2 = generate_key()
        self.assertNotEqual(key1, key2)

    def test_password_hashing(self):
        correct = hash_password(self.correct)
        incorrect = hash_password(self.incorrect)
        
        self.assertFalse(check_password(self.incorrect, correct))
        self.assertTrue(check_password(self.correct, correct))
        self.assertFalse(check_password(self.correct, incorrect))
        
    def test_cookie(self):
        c = cookie()
        self.assertEqual(c, 'session_id=; Path=/; Expires=Tue, 31-Dec-2019 23:59:59 GMT')
        
        key = generate_key()
        c = cookie(key)
        self.assertEqual(c, 'session_id=%s; Path=/; Expires=Tue, 31-Dec-2019 23:59:59 GMT' % key)
        
if __name__ == '__main__':
    unittest.main()
