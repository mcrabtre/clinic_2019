#single client for aggregator

import socket
import errno
import pickle
import types
import numpy as np
#import NodeSvm


def client(host,data):
    host = host
    data = data # data has properties .w .nodenum .tau .k
    port = 65432
    datasend = pickle.dumps(data)
    print('bytes to send ', len(datasend))
    
    s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    server_addr = (host, port)
    s.connect(server_addr)
    print ('connected to ',host)
    #s.sendall(datasend)
    
    total_sent = 0 # alternate to s.sendall()
    while len(datasend):
        sent = s.send(datasend)
        total_sent += sent
        datasend = datasend[sent:]
        print('sending data')

    print('bytes sent ', total_sent)
    print('w sent')
    s.close()



 
##use:
##w = np.zeros(784)
#w = np.ones(784)
#N = 0
#tau = 2
##w,fn = NodeSvm.NodeSVM(w,N)
#host = '192.168.0.11'
##host = '127.0.0.1'
#data = types.SimpleNamespace(w=w,nodenum=N,tau=tau) 
#client(host,data)

    #        except s.error, e:
    #            if e.errno != errno.EAGAIN:
    #                raise e
    #            yield(s) #https://github.com/vaidik/nonblocking-io-examples
    #/blob/master/part1/example1.4-client.py
