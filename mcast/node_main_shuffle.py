# -*- coding: utf-8 -*-
"""
Created on Sat Mar 30 13:13:17 2019

@author: hokis
"""
import numpy as np
import pandas as pd
import socket
import queue
import types
import SVM
import Read
import node_client
import node_server
import os
import encode_manager as e
import threading
import time
import mcast_recv1
import mcast_send
'''
    Main for the nodes. Starts and waits for data from agg. once received it unpacks data and runs the svm.
    It then sends the w vector and loss functions back to the agg.
'''


def run():
    while True:

        # node detection: determine IP address
        #nodeIP = socket.gethostbyname_ex("raspberrypi.local")#[-1]
        os.system('hostname -I > output.txt') #these 6 commands reads ip address from linux OS
        ip_file = open('output.txt', 'r')
        n_ip = ip_file.readline()
        nodeIP = n_ip.rstrip(' \n')
        ip_file.close()
        os.remove('output.txt')
        #nodeIP = '192.168.0.106' '''Currently unable to detect own ip do to identical names. Must be changed for each node'''

        print('I am ', nodeIP)
        print('Waiting for Agg')
        # listen for info from aggregator.
        # determine node number (n) and total number of nodes (Num) from agg Xmission
        # N is list of node
        # win,tau,k,d,N,aggIP = node_server.server(node_ip)
        info = node_server.server(nodeIP) 
        
        n = info.node_dict[nodeIP] + 1  # node number (1,2,3,4,5)
        print('I am node number ', n)
        Num = len(info.node_dict)  # total number of nodes (should be 5)
        d = info.d  # number data points/node
        tau = info.tau  # number of local iterations
        k = info.k  # global iteration number
        host = info.host  # aggregator IP
        shuff = info.shuff  # number of shuffles per global iteration
        
        # these can be pulled from the agg if desired 
        weight = 1
        eta = .01
        lam = 1
        
        # pull data_pts for global update
        w = info.w
        D = d*Num# Total data points 
        filepath = r"train.csv"
        e.create_workspace(n, filepath, D)  # initialization of the workspace file
        cache_q = queue.Queue()  # use of the fifo queue structure ensures safe exchange of data between threads
        icount = 1  # compare to iterations
        threads = {}
        # this variable keeps track of which data part is needed next for receive, there are 3 needed for each recv
        cpart = 1
        time_init = time.time()
        ans_data = [(0, 'no data'), (0, 'no data'), (0, 'no data')]
        recv_nodes = e.node_tracker()
        recv_stages = (1, 1, 2)

        for i in range(3):
            # create and start separate threads to receive from different nodes (node, stage, q, priority):
            threads[i] = threading.Thread(target=mcast_recv1.m_recv, args=(recv_nodes[i], recv_stages[i], cache_q, i + 1), daemon=False)
            threads[i].start()
            print('starting thread ', i + 1)

        while icount <= shuff:  # main coded shuffling running loop (for shuff iterations)
            mcast_send.send(n, 1, e.stage1_send())  # send stage1 partition
            mcast_send.send(n, 2, e.stage2_send())  # send stage2 partition
            data_pts = e.get_work_file()  # data points for current iteration to use for training
            w, fn = SVM.svm(w, data_pts, eta, lam, tau, d, weight, shuff=0, N=Num, n=n - 1) #train on tau iterations data_pts d
            while cpart < 4:
                cp = cpart  # need this to ensure queue is completely cycled before searching for the next part
                for i in range(cache_q.qsize()):  # cycle through the queue for receive data
                    a = cache_q.get()  # tuple in form (part integer, DATA)
                    if a[0] == cp:  # if it is the part needed adds part to ans_data and increments to next part
                        cp = 'disabled'
                        ans_data[cpart - 1] = a
                        cpart = cpart + 1
                    else:
                        cache_q.put(a)
                if time.time() >= (time_init + 60):  # times out 60s of not receiving all 3 pieces of data
                    print("Error: threads timed out")
                    break

            if cpart >= 4:  # receive condition triggers when all data is ready
                e.recv(ans_data[0][1], ans_data[1][1], ans_data[2][1])
                cpart = 1
                time_init = time.time()
                icount = icount + 1
            else:  # condition met if previous loop timed out
                break
        if not mcast_recv1.kill:  # kills threads by ending underlying function(s)
            mcast_recv1.kill = True
            print('Threads killed')

        # send w to agg
        node_client.client(w, fn, host)
        
run()
