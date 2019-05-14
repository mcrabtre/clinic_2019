# -*- coding: utf-8 -*-
"""
Created on Fri Oct 12 12:50:36 2018

@author: fog
"""

import selectors
import socket
import pickle
import numpy as np


def aggr_server(host,num_con):  # add num_con as input (number of nodes)
    global numconn, w, fn, keep_running, sel, num
    num = num_con # number of nodes to listen for
    numconn = 0 # number times has been connected to and recieved a vector
    sel = selectors.DefaultSelector()
    keep_running = True
    
    w = []
    fn = []
    host = host
    port = 65432
    
    server_addr = (host, port)       
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Avoid bind() exception: OSERROR: [Errno 48] Address already in use
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.setblocking(False)
    server.bind(server_addr)
    server.listen()
    print('listening on', (host, port))
    
    sel.register(server, selectors.EVENT_READ, accept) # call accept()
    
    while keep_running:
        print('waiting for I/O')
        event = sel.select()
        for key, mask in event:
            callback = key.data # .data = accept() or read()
            #print(callback)
            callback(key.fileobj, mask) # .fileobj is socket, 
     
    print('closing server')
    sel.close()
    return w,fn


def accept(sock, mask):
    conn, addr = sock.accept()  # Should be ready
    print('accepted connection from', addr)
    conn.setblocking(1)
    sel.register(conn, selectors.EVENT_READ, read) # call read

def read(conn, mask):
    global keep_running, numconn, w, fn
    
    datain = b''  # initialize
    dataRecvd = conn.recv(1024)
    while dataRecvd:
        datain += dataRecvd
        #print('received ',len(datain),' bits')
        dataRecvd = conn.recv(1024)

    numconn += 1
    conn.setblocking(0)


    print('recieved ',len(datain),' bits')     
    arr = pickle.loads(datain)
    #print(arr.fn)
    w = np.append(w, arr.w)
    fn = np.append(fn, arr.fn)
    print('closing', numconn)
    sel.unregister(conn)
    conn.close()
    if numconn >= num: # if numconn == num_con # number of times w recieved = number nodes
        keep_running = False
 

#host = '192.168.0.14' # aggregator ip
#num_con =  2 # number nodes to collect from 
#w,fn = aggr_server(host,num_con)
###print(w)    



