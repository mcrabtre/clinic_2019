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


# cannot send more than 65k bytes at a time (at least to pis)
def send(node, stage, data):
    print("sending")
    if stage == 1:
        ip_switcher = {
            1: '224.3.29.71',
            2: '224.3.29.72',
            3: '224.3.29.73',
            4: '224.3.29.74',
            5: '224.3.29.75',
        }
        port_switcher = {
            1: 5001,
            2: 5002,
            3: 5003,
            4: 5004,
            5: 5005,
        }
    else:
        ip_switcher = {
            1: '224.3.29.76',
            2: '224.3.29.77',
            3: '224.3.29.78',
            4: '224.3.29.79',
            5: '224.3.29.80',
        }
        port_switcher = {
            1: 5006,
            2: 5007,
            3: 5008,
            4: 5009,
            5: 5010,
        }
    MCAST_GRP = ip_switcher.get(node, '0.0.0.0')
    MCAST_PORT = port_switcher.get(node, 0000)
    data = data  # data has properties .w .nodenum .tau .k
    #= b'0xff' + y
    #need to tune send buffers
    datasend = pickle.dumps(data) #will ditch pickle later, its garbage
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 1)
    buff = 1472

    if len(datasend) > buff:  # break large send data into buff sized pieces to send individually
        pcs = int(datasend.__len__()/buff)
        for i in range(pcs):
            sock.sendto(datasend[i*buff:(i+1)*buff], (MCAST_GRP, MCAST_PORT))
        sock.sendto(datasend[pcs*buff:datasend.__len__()], (MCAST_GRP, MCAST_PORT))
    else:
        sock.sendto(datasend, (MCAST_GRP, MCAST_PORT))
    print("sent stage ", stage)
    sock.close()



#source: https://stackoverflow.com/questions/603852/how-do-you-udp-multicast-in-python


