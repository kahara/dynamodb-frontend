import boto.dynamodb
from boto.dynamodb.condition import *
import sys, traceback
from resource import Resource, timestamp
from response import Response

class TagResource(Resource):
    resource_name = 'tag'
    
    def do_post(self):
        pass
    
    def do_put(self):
        pass
    
    def do_get(self):
        if not self.session or len(self.request.path) > 2:
            self.response = Response(status=400)
            return
        
        elif len(self.request.path) == 1: # return complete tag tree starting from root
            tag_tree = self.get_tag_tree()
            
        elif len(self.request.path) == 2: # return a branch of tag tree
            tag_tree = self.get_tag_tree(self.request.path[1])
        
        self.response = Response(status=200, body=tag_tree)
        return

    def get_tag_tree(self, tag=''):
        user = self.session['user']
        
        data = {'tags': {}, 'subscriptions': {}}
        try:
            item = self.tables['tag'].get_item(hash_key=user + ':' + tag)
        except:
            return data
        
        try:
            tags = list(item['tags'])
        except:
            tags = []
        
        for tag in tags:
            data['tags'][tag] = self.get_tag_tree(tag)
        
        try:
            data['subscriptions'] = list(item['subscriptions'])
        except:
            data['subscriptions'] = []
        
        return data
