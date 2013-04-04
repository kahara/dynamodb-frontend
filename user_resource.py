import boto.dynamodb
from boto.dynamodb.condition import *
import boto.ses
from auth import generate_key, hash_password, check_password
import json, sys, traceback
from resource import Resource, timestamp
from response import Response

class UserResource(Resource):
    resource_name = 'user'
    
    def do_post(self):
        # /user/                    request new account
        # /user/activation/<token>/ confirm new account
        # /user/reset/              request account password reset
        # /user/reset/<token>/      reset account password
        
        if len(self.request.path) == 1:
            self.request_new_account()

        elif len(self.request.path) == 3 and self.request.path[1] == 'activation':
            self.confirm_new_account()
            
        elif len(self.request.path) == 2 and self.request.path[1] == 'reset':
            self.request_password_reset()

        elif len(self.request.path) == 3 and self.request.path[1] == 'reset':
            self.reset_password()            
                        
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

    def request_new_account(self):
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
    
    def confirm_new_account(self):
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

    def request_password_reset(self):
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
    
    def reset_password(self):
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
