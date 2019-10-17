# -*- coding: utf-8 -*-
"""
Created on Sun Feb  3 09:59:11 2019

@author: hokis
"""


import socket
import types
import pickle
import numpy as np
#import pandas as pd

use = False 
use = True
# cannot send more than 65k bytes at a time (at least to pis)
def send(node, stage, data):
    print("sending")
    ip_switcher = {
        1: '224.3.29.71',
        2: '224.3.29.72',
        3: '224.3.29.73',
        4: '224.3.29.74',
        5: '224.3.29.75',
    }
    MCAST_GRP = ip_switcher.get(node, '0.0.0.0')
    port_switcher = {
        1: 5007,
        2: 5008,
    }
    MCAST_PORT = port_switcher.get(stage, 0000)
    
    data = data # data has properties .w .nodenum .tau .k
    #= b'0xff' + y
    #need to tune send buffers
    datasend = pickle.dumps(data) #will ditch pickle later, its garbage
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 1)
    
    sock.sendto(datasend, (MCAST_GRP, MCAST_PORT))
    print("sent")
    sock.close()


if use:
    #use:
    K = 1
    N = 1
    d = 10   
    w = "array of values"
    #w = np.ones(784)
    #filepath = r"train.csv"
    #data_pts = pd.read_csv(filepath, skiprows=0, nrows=(d*N)).values
    #w,fn = NodeSvm.NodeSVM(w,N)
    data = types.SimpleNamespace(w=w)#,data_pts=data_pts) 
    print("message is %s", data.w)
    send(data)
    #send(d)

#source: https://stackoverflow.com/questions/603852/how-do-you-udp-multicast-in-python


