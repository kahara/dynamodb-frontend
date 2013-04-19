import json
from striptags import striptags

class Response(object):
    statuses = {
        'default': '500 Internal Server Error',
        200: '200 OK',
        201: '201 Created',
        204: '204 No Content',
        400: '400 Bad Request',
        401: '401 Unauthorized',
        403: '403 Forbidden',
        405: '405 Method Not Allowed',
        500: '500 Internal Server Error',
        }
    
    def __init__(self, version = 'HTTP/1.0', status = None, headers = None, body = None):
        
        self.version = version
        
        if status and status in self.statuses: self.status = self.statuses[status]
        else: self.status = self.statuses['default']
        
        if headers:
            self.headers = headers
        else:
            self.headers = {}
        
        if not 'Content-type' in self.headers:
            self.headers['Content-type'] = 'application/json'
        if body:
            try: self.body = json.dumps(striptags(body))
            except:
                self.body = None
                self.status = self.statuses[500]
                return
            self.headers['Content-length'] = len(self.body)
        else:
            self.body = None

    def raw(self):
        s = '%s %s\r\n' % (self.version, self.status)
        if self.headers:
            for key in self.headers:
                s += '%s: %s\r\n' % (key, self.headers[key])
        s+= '\r\n'
        if self.body: s += self.body
        
        return s
