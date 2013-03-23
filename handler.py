from multiprocessing import Queue, current_process
from request import HTTPRequest
#form resource import UserResource

def handler(is_running, request_q, response_q):
    
    body  = b'HTTP/1.0 200 OK\r\nDate: Mon, 1 Jan 1996 01:01:01 GMT\r\n'
    body += b'Content-Type: text/plain\r\nContent-Length: 13\r\n\r\n'
    body += b'Hello, world!'
    
    # resource_map = {
    #     'user': UserResource,
    #     }
    
    while True and is_running.value:
        try:
            # read one incoming request
            try:
                request = request_q.get(block=True, timeout=0.001)
            except:
                continue
            
            # process incoming request and generate response
            http_request = HTTPRequest(request['raw'])
            
            response = { 'id': request['id'], 'raw': body }
            
            # send response
            response_q.put(response)
            
        except KeyboardInterrupt:
            pass

