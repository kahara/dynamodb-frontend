#!/usr/bin/env python

import socket, select
from multiprocessing import Process, Queue
from handler import handler

if __name__ == '__main__':

    request_q = Queue()
    response_q = Queue()
    request_handlers = [Process(target=handler, args=(request_q, response_q)).start() for x in range(10)]
    
    # derived: http://scotdoyle.com/python-epoll-howto.html#async-examples
    EOL1 = b'\n\n'
    EOL2 = b'\n\r\n'
    response  = b'HTTP/1.0 200 OK\r\nDate: Mon, 1 Jan 1996 01:01:01 GMT\r\n'
    response += b'Content-Type: text/plain\r\nContent-Length: 13\r\n\r\n'
    response += b'Hello, world!'
    
    serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serversocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    serversocket.bind(('0.0.0.0', 9000))
    serversocket.listen(500) # hm?
    serversocket.setblocking(0)
    
    epoll = select.epoll()
    epoll.register(serversocket.fileno(), select.EPOLLIN | select.EPOLLET)
    
    try:
        connections = {}
        requests = {}
        responses = {}
        while True:
            
            while True:
                try:
                    response = response_q.get(block=False)
                    epoll.modify(response['id'], select.EPOLLOUT | select.EPOLLET)
                    responses[response['id']] = response['raw']
                except:
                    break
                
            events = epoll.poll(0.001)
            for fileno, event in events:
                if fileno == serversocket.fileno():
                    try:
                        while True:
                            connection, address = serversocket.accept()
                            connection.setblocking(0)
                            epoll.register(connection.fileno(), select.EPOLLIN | select.EPOLLET)
                            connections[connection.fileno()] = connection
                            requests[connection.fileno()] = b''
                    except socket.error:
                        pass
                elif event & select.EPOLLIN:
                    try:
                        while True:
                            requests[fileno] += connections[fileno].recv(1024)
                    except socket.error:
                        pass
                    if EOL1 in requests[fileno] or EOL2 in requests[fileno]:
                        request_q.put({ 'id': fileno, 'raw': requests[fileno] })
                        #epoll.modify(fileno, select.EPOLLOUT | select.EPOLLET)
                        #print('-'*40 + '\n' + requests[fileno].decode()[:-2])
                elif event & select.EPOLLOUT:
                    try:
                        while len(responses[fileno]) > 0:
                            byteswritten = connections[fileno].send(responses[fileno])
                            responses[fileno] = responses[fileno][byteswritten:]
                    except socket.error:
                        pass
                    if len(responses[fileno]) == 0:
                        epoll.modify(fileno, select.EPOLLET)
                        connections[fileno].shutdown(socket.SHUT_RDWR)
                elif event & select.EPOLLHUP:
                    epoll.unregister(fileno)
                    connections[fileno].close()
                    del connections[fileno]
    finally:
        epoll.unregister(serversocket.fileno())
        epoll.close()
        serversocket.close()
