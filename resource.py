from response import Response
import boto.dynamodb
from boto.dynamodb.condition import *
import boto.ses
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
