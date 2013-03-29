class Request(object):
    def __init__(self, raw):
        self.raw = raw
        self.method = None
        self.path = None
        self.version = None
        self.headers = {}
        self.session_id = None
        self.body = None
        self.is_valid = False
        
        self.parse()

    def parse(self):
        try:
            request_line, headers = self.raw.split('\r\n', 1)
            self.method, self.path, self.version = request_line.split(' ', 2)
            self.path = [x for x in self.path.split('/') if x]        
            headers, self.body = headers.split('\r\n\r\n', 1)
            for header in headers.split('\r\n'):
                key, value = header.split(':', 1)
                self.headers[key.strip()] = value.strip()

            if 'Cookie' in self.headers:
                key, value = self.headers['Cookie'].split(';')[0].split('=')
                if key == 'session_id' and value:
                    self.session_id = value
            
            self.is_valid = True
        except:
            self.is_valid = False
