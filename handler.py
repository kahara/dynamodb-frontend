from multiprocessing import Queue, current_process
from request import Request
from resource import UserResource, SessionResource

def handler(is_running, request_q, response_q):
    
    resource_map = {
        'user': UserResource,
        'session': SessionResource,
        }
    
    while True and is_running.value:
        try:
            # read one incoming request
            try:
                request = request_q.get(block=True, timeout=0.001)
            except:
                continue
            
            # process incoming request and generate response
            http_request = Request(request['raw'])
            resource = resource_map[http_request.path[0]](http_request)
            response = resource.response.raw()
            
            # send back response
            response_q.put({ 'id': request['id'], 'raw': response })
            
        except KeyboardInterrupt:
            pass
