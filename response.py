class HTTPResponse(object):
    statuses = {
        'default': '400 Bad Request',
        200: '200 OK',
        }
    def __init__(self, version = 'HTTP/1.0', status = None, headers = None, body = None):
        
        self.version = version
        if status and status in self.statuses: self.status = self.statuses[status]
        else: self.status = self.statuses['default']
        self.headers = headers
        if body:
            self.body = body
            self.headers['Content-length'] = len(self.body)

    def raw(self):
        s = '%s %s\r\n' % (self.version, self.status)
        if self.headers:
            for key in self.headers:
                s += '%s: %s\r\n' % (key, self.headers[key])
        s+= '\r\n'
        if self.body: s += self.body
        
        return s