import unittest, json, sys, boto.dynamodb
sys.path.insert(0, '..')
from auth import generate_key, hash_password
from request import Request
from resource import timestamp

class TestBase(unittest.TestCase):
    def setUp(self):
        self.userid = generate_key()
        self.username = 'thisisatestuser'
        self.email = 'thisisatestemail@example.com'
        self.password = 'thisisatestpassword'
        self.sessionid = None
        
        connection =  boto.dynamodb.connect_to_region('eu-west-1')
        
        try:
            username_item = connection.get_table('username').get_item(hash_key=self.username)
            connection.get_table('user').get_item(hash_key=username_item['user']).delete()
            username_item.delete()
            # XXX scan these test user tags and delete them
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
        
        self.sessionid = generate_key()
        connection.get_table('session').new_item(
            hash_key=self.sessionid,
            attrs={
                'user': self.userid,
                'email': self.email,
                'username': self.username,
                'timestamp': timestamp()
                }
            ).put()        
        self.cookie = 'session_id=' + self.sessionid + ';'
        
    def tearDown(self):
        connection =  boto.dynamodb.connect_to_region('eu-west-1')
        
        try: connection.get_table('session').get_item(hash_key=self.sessionid).delete()
        except: pass
        
        try: connection.get_table('user').get_item(hash_key=self.userid).delete()
        except: pass
        
        try: connection.get_table('username').get_item(hash_key=self.username).delete()
        except: pass
        
        try: connection.get_table('email').get_item(hash_key=self.email).delete()
        except: pass
