from response import HTTPResponse

class Resource(object):
    def __init__(self, request):
        self.request = request
        self.response = None
        self.handle()
        
class UserResource(Resource):
    def handle(self):
        self.response = HTTPResponse(status=200, headers={'foo': 'bar', 'baz': 'quux'}, body='i am the walrus')
