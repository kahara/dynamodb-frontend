from multiprocessing import Queue

import time

def handler(is_running, request_q, response_q):
    
    requests = []
    responses = []
    
    body  = b'HTTP/1.0 200 OK\r\nDate: Mon, 1 Jan 1996 01:01:01 GMT\r\n'
    body += b'Content-Type: text/plain\r\nContent-Length: 13\r\n\r\n'
    body += b'Hello, world!'
    
    while True and is_running.value:
        try:
            # read incoming requests
            while True:
                try:
                    raw = request_q.get(block=False)

                    requests.append(raw)
                except:
                    break

            # process incoming requests and generate responses
            for x in range(10):
                try:
                    request = requests.pop(0)
                    responses.append({ 'id': request['id'], 'raw': body })
                except:
                    break

            # send responses
            while True:
                try:
                    response = responses.pop(0)
                    response_q.put(response)
                except:
                    break

            time.sleep(0.001)

        except KeyboardInterrupt:
            pass
