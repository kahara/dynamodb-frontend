import boto.dynamodb
from boto.dynamodb.condition import *
import sys, traceback
from resource import Resource, timestamp
from response import Response

class TagResource(Resource):
    resource_name = 'tag'
    
    def do_post(self):
        if not self.session or len(self.request.path) > 1:
            self.response = Response(status=400)
            return

        body = self.request.body

        if 'tag' in body:
            tag = body['tag']
        else:        
            self.response = Response(status=400)
            return

        try:
            user = self.session['user']
            tag_item = self.tables['tag'].get_item(hash_key=user + ':' + tag)
            if tag_item:
                self.response = Response(status=400)
                return
        except:
            pass
        
        try:
            attrs = {}
            
            if 'tags' in body:
                attrs['tags'] = set(body['tags'])

            if 'subscriptions' in body:
                # XXX look up subscriptions ("subscription id:subscription title")
                attrs['subscriptions'] = set(body['subscriptions'])

            tag_item = self.tables['tag'].new_item(hash_key=user + ':' + tag, attrs=attrs)
            tag_item.put()
            
        except:
            self.response = Response(status=400)
            return
        
        self.response = Response(status=201, body=self.get_tag_tree(tag))
        return
    
    def do_put(self):
        if not self.session or len(self.request.path) != 2:
            self.response = Response(status=400)
            return
                
        try:
            user = self.session['user']
            tag = self.request.path[1]
            
            tag_item = self.tables['tag'].get_item(hash_key=user + ':' + tag)
            if not tag_item:
                self.response = Response(status=400)
                return

            body = self.request.body
            
            if 'tags' in body:
                tag_item['tags'] = set(body['tags'])
            
            if 'subscriptions' in body:
                # XXX look up subscriptions ("subscription id:subscription title")
                tag_item['subscriptions'] = set(body['subscriptions'])
            
            tag_item.put()
            
            self.response = Response(status=200, body={'tags': list(tag_item['tags']), 'subscriptions': list(tag_item['subscriptions'])})
            return
        
        except:
            self.response = Response(status=400)
            return
      
    def do_delete(self):
        if not self.session or len(self.request.path) != 2:
            self.response = Response(status=400)
            return

        try:
            user = self.session['user']
            tag = self.request.path[1]
            
            tag_item = self.tables['tag'].get_item(hash_key=user + ':' + tag)
            if not tag_item:
                self.response = Response(status=400)
                return
            
            tag_item.delete()
            
            self.response = Response(status=204)
            return
            
        except:
            self.response = Response(status=400)
            return
        
        
        
    def do_get(self):
        if not self.session or len(self.request.path) > 2:
            self.response = Response(status=400)
            return
        
        elif len(self.request.path) == 1: # return complete tag tree starting from root
            tag_tree = self.get_tag_tree()
            
        elif len(self.request.path) == 2: # return a branch of tag tree
            tag_tree = self.get_tag_tree(self.request.path[1])
        
        if not tag_tree:
            self.response = Response(status=400)
            return
        
        self.response = Response(status=200, body=tag_tree)
        return

    def get_tag_tree(self, tag=''):
        user = self.session['user']
        
        # XXX detect circular references
        
        data = {'tags': {}, 'subscriptions': {}}
        try:
            item = self.tables['tag'].get_item(hash_key=user + ':' + tag)
        except:
            return None
        
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
