import boto.dynamodb
from boto.dynamodb.condition import *
from auth import generate_key, check_password, cookie
import sys, traceback
from resource import Resource, timestamp
from response import Response

class SessionResource(Resource):
    resource_name = 'session'
    
    # return username and email of this session
    def do_get(self):
        try:
            if self.session:
                self.response = Response(status=200, body={'username': self.session['username'], 'email': self.session['email'] })
                return
            else:
                self.response = Response(status=401)
                return
        except:
            self.response = Response(status=401)
            return

    # log in a user, creating a session
    def do_post(self): # log in user
        if self.session: # user already logged in
            self.response = Response(status=400)
            return
        
        try:
            credentials = self.request.body
            if not credentials['login'] or not credentials['password']: # malformed credential payload
                self.response = Response(status=400)
                return
        except: # malformed credential payload
            self.response = Response(status=400)
            return
        
        if '@' in credentials['login']: # log in with email address
            lookup = self.tables['email'].get_item(hash_key=credentials['login'])
        else: # log in with username
            lookup = self.tables['username'].get_item(hash_key=credentials['login'])
        user = self.tables['user'].get_item(hash_key=lookup['user'])
        
        if not user: # no such user
            self.response = Response(status=400)
            return
        
        if not check_password(credentials['password'], user['password']): # incorrect password
            self.response = Response(status=401)
            return
        
        # create session
        session_id = generate_key()
        attrs = { 'timestamp': timestamp(), 'user': user['id'], 'email': user['email'], 'username': user['username'] }
        session = self.tables['session'].new_item(hash_key=session_id, attrs=attrs)
        session.put()
        
        # return session id
        self.response = Response(status=200, headers={'Set-Cookie': cookie(session_id) })
    
    # log out, deleting session
    def do_delete(self):
        if not self.session:
            self.response = Response(status=400)
            return
                
        self.session.delete()
        
        # return empty session cookie
        self.response = Response(status=204, headers={'Set-Cookie': cookie() })
