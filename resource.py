from response import Response
import boto.dynamodb
from boto.dynamodb.condition import *
import boto.ses
from auth import generate_key, hash_password, check_password, cookie
import json, sys, traceback
from datetime import datetime
from time import mktime
from random import randint

def timestamp():
    return int(mktime(datetime.utcnow().timetuple()))

class Resource(object):
    connection = None
    tables = {}
    
    def __init__(self, request):
        self.request = request
        self.response = None
        self.session = None
        
        # set up DynamoDB
        if not self.connection:
            self.connection =  boto.dynamodb.connect_to_region('eu-west-1')        
        if not self.tables:
            for table_name in ['user', 'email', 'username', 'reset', 'activation', 'session']:
                self.tables[table_name] = self.connection.get_table(table_name)
        
        # fetch session if exists
        if self.request.session_id:
            try:
                self.session = self.tables['session'].get_item(hash_key=self.request.session_id)
                if not randint(1, 10) % 10: 
                    self.session['timestamp'] = timestamp()
                    self.session.put()
            except:
                self.response = Response(status=400)
                return
        
        # call the requested method
        try:
            getattr(self, {
                    'GET': 'do_get',
                    'POST': 'do_post',
                    'PUT': 'do_put',
                    'DELETE': 'do_delete',
                    }[self.request.method.upper()])()
        except Exception, e:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            print traceback.format_exception(exc_type, exc_value, exc_traceback)            
            self.response = Response(status=405)
            return

class UserResource(Resource):
    resource_name = 'user'
    
    def do_post(self):
        # /user/                    request new account
        # /user/activation/<token>/ confirm new account
        # /user/reset/              request account password reset
        # /user/reset/<token>/      reset account password
        
        if len(self.request.path) == 1:
            # request creation of new user account
            try:
                body = json.loads(self.request.body)
                
                try: email_item = self.tables['email'].get_item(hash_key=body['email'])
                except: email_item = None
                try: username_item = self.tables['username'].get_item(hash_key=body['username'])
                except: username_item = None
                if email_item or username_item: # such a user already exists
                    self.response = Response(status=400, body='Username and/or email already registered')
                    return
                
                attrs = {
                    'email': body['email'],
                    'username': body['username'],
                    'password': hash_password(body['password']),
                    'timestamp': timestamp(),
                    }
                
                token = generate_key()
                activation_item = self.tables['activation'].new_item(hash_key=token, attrs=attrs)
                activation_item.put()
                
                # send email with activation token to given address
                conn = boto.ses.connect_to_region('us-east-1')
                msg_subject = 'XXX Service Name Here new user account creation requested'
                msg_body = '' \
                    'You requested that we create a new XXX Service Name Here user account for you. ' \
                    'To activate your account, please click the following link, or copy and paste it to your web browser:\n\n' \
                    'http://xxxservicedomain/user/activation/%s\n\n' \
                    'The link is valid until XXXX-XX-XX XX:XX:XX\n\n' \
                    '\tYours, &c.\n\tXXX Service Name Here' % token
                conn.send_email('noreply@async.fi', msg_subject, msg_body, [body['email']])
                
                self.response = Response(status=204)
                return

            except:
                exc_type, exc_value, exc_traceback = sys.exc_info()
                print traceback.format_exception(exc_type, exc_value, exc_traceback)            
                self.response = Response(status=400)
                return
        
        elif len(self.request.path) == 3 and self.request.path[1] == 'activation':
            # confirm new user account
            try:
                token = self.request.path[2]
                activation_item = self.tables['activation'].get_item(hash_key=token)
                if (timestamp() - activation_item['timestamp']) > (15 * 60):
                    self.response = Response(status=400)
                    return
                
                user_id = generate_key()
                
                user_item = self.tables['user'].new_item(hash_key=user_id, attrs={'email': activation_item['email'], 'username': activation_item['username'], 'password': activation_item['password']})
                user_item.put()
                
                email_item = self.tables['email'].new_item(hash_key=activation_item['email'], attrs={'user': user_id})
                email_item.put()
                
                username_item = self.tables['username'].new_item(hash_key=activation_item['username'], attrs={'user': user_id})
                username_item.put()
                
                activation_item.delete()
                
                self.response = Response(status=201)
                return
            
            except:
                exc_type, exc_value, exc_traceback = sys.exc_info()
                print traceback.format_exception(exc_type, exc_value, exc_traceback)
                self.response = Response(status=400)
                return
            
        elif len(self.request.path) == 2 and self.request.path[1] == 'reset':
            # request password reset
            try:
                # create new item in reset table
                body = json.loads(self.request.body)
                token = generate_key()
                reset_item = self.tables['reset'].new_item(hash_key=token, attrs={'email': body['email'], 'timestamp': timestamp()})
                reset_item.put()
                
                # send email with reset token to given address
                conn = boto.ses.connect_to_region('us-east-1')
                msg_subject = 'XXX Service Name Here password reset requested'
                msg_body = '' \
                    'You requested that we reset your XXX Service Name Here password. ' \
                    'To do so, please click the following link, or copy and paste it to your web browser:\n\n' \
                    'http://xxxservicedomain/user/reset/%s\n\n' \
                    'The link is valid until XXXX-XX-XX XX:XX:XX\n\n' \
                    '\tYours, &c.\n\tXXX Service Name Here' % token
                conn.send_email('noreply@async.fi', msg_subject, msg_body, [body['email']])

                self.response = Response(status=204)
                return

            except:
                exc_type, exc_value, exc_traceback = sys.exc_info()
                print traceback.format_exception(exc_type, exc_value, exc_traceback)
                self.response = Response(status=400)
                return
        
        elif len(self.request.path) == 3 and self.request.path[1] == 'reset':
            # process password reset request
            try:
                token = self.request.path[2]
                body = json.loads(self.request.body)
                password = body['password']
                
                reset_item = self.tables['reset'].get_item(hash_key=token)
                if (timestamp() - reset_item['timestamp']) > (15 * 60):
                    self.response = Response(status=400)
                    return
                
                email_item = self.tables['email'].get_item(hash_key=reset_item['email'])
                user_item = self.tables['user'].get_item(hash_key=email_item['user'])
                
                user_item['password'] = hash_password(password)
                user_item.put()
                
                reset_item.delete()
                
                self.response = Response(status=204)
                return
                
            except:
                exc_type, exc_value, exc_traceback = sys.exc_info()
                print traceback.format_exception(exc_type, exc_value, exc_traceback)
                self.response = Response(status=400)
                return
                        
    # change user's details; for now, only password can be changed
    def do_put(self):
        try:
            if self.session:
                body = json.loads(self.request.body)
                if not 'password' in body: # malformed payload
                    self.response = Response(status=400)
                    return
                user = self.tables['user'].get_item(hash_key=self.session['user'])
                user['password'] = hash_password(body['password'])
                self.response = Response(status=204)
                return
            else:
                self.response = Response(status=401)
                return
        except:
            self.response = Response(status=400)
            return
        
class SessionResource(Resource):
    resource_name = 'session'
    
    # return username and email of this session
    def do_get(self):
        try:
            if self.session:
                self.response = Response(status=200, body=json.dumps({'username': self.session['username'], 'email': self.session['email'] }))
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
            credentials = json.loads(self.request.body)
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
