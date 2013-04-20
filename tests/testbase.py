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
        
        self.connection =  boto.dynamodb.connect_to_region('eu-west-1')
        
        try:
            username_item = self.connection.get_table('username').get_item(hash_key=self.username)
            self.connection.get_table('user').get_item(hash_key=username_item['user']).delete()
            username_item.delete()
            # XXX scan these test user tags and delete them
        except: pass
        try: self.connection.get_table('email').get_item(hash_key=self.email).delete()
        except: pass
        
        self.connection.get_table('user').new_item(
            hash_key=self.userid,
            attrs={
                'username': self.username,
                'email': self.email,
                'password': hash_password(self.password),
                }
            ).put()
        
        self.connection.get_table('username').new_item(
            hash_key=self.username,
            attrs={
                'user': self.userid,
                }
            ).put()
        
        self.connection.get_table('email').new_item(
            hash_key=self.email,
            attrs={
                'user': self.userid,
                }
            ).put()
        
        self.sessionid = generate_key()
        self.connection.get_table('session').new_item(
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
        self.connection = boto.dynamodb.connect_to_region('eu-west-1')
        
        try: self.connection.get_table('session').get_item(hash_key=self.sessionid).delete()
        except: pass
        
        try: self.connection.get_table('user').get_item(hash_key=self.userid).delete()
        except: pass
        
        try: self.connection.get_table('username').get_item(hash_key=self.username).delete()
        except: pass
        
        try: self.connection.get_table('email').get_item(hash_key=self.email).delete()
        except: pass
