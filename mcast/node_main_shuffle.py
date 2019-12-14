# -*- coding: utf-8 -*-
"""
Created 15OCT2019 by mcrabtre
"""

import queue
import SVM
import node_client
import node_server
import os
import data_manager as e
import threading
import time
import mcast_recv1
import mcast_send
'''
    Main for the nodes. Starts and waits for data from agg. once received it unpacks data and runs the coded shuffle
    svm. It then sends the w vector and loss functions back to the agg.
'''


def run():
    os.system('hostname -I > output.txt')  # these 6 commands reads ip address from linux OS
    ip_file = open('output.txt', 'r')
    n_ip = ip_file.readline()
    nodeIP = n_ip.rstrip(' \n')
    os.remove('output.txt')

    mcast_recv1.kill = False
    n = e.cycle5(int(nodeIP[-1]) + 1)
    e.node = n
    recv_nodes = e.node_tracker()
    recv_stages = 1
    threads = {}
    cache_q = queue.Queue()  # use of the fifo queue structure ensures safe exchange of data between threads
    k = 1  # global counter
    K = 5  # will be changed by data received from agg (global iterations)
    for i in range(1):
        # create and start separate threads to receive from different nodes (node, stage, q, priority):
        threads[i] = threading.Thread(target=mcast_recv1.m_recv, args=(recv_nodes[i], recv_stages[i], cache_q, i + 1), daemon=False)
        threads[i].start()
        print('starting thread ', i + 1)

    while k < K:  # main running loop


        print('I am ', nodeIP)
        print('Waiting for Agg')
        # listen for info from aggregator.
        # determine node number (n) and total number of nodes (Num) from agg Xmission
        # N is list of node
        # win,tau,k,d,N,aggIP = node_server.server(node_ip)
        info = node_server.server(nodeIP) 
        
        #n = info.node_dict[nodeIP] + 1  # node number (1,2,3,4,5)
        print('My node number is ', n)
        Num = len(info.node_dict)  # total number of nodes (should be 5)
        d = info.d  # number data points/node
        tau = info.tau  # number of local iterations
        K = info.K  # global iteration number
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
        if not e.set_flag:
            e.create_workspace(n, filepath, D)  # initialization of the workspace file
        shuffcount = 1  # compare to iterations
        # this variable keeps track of which data part is needed next for receive, there are 3 needed for each recv
        time_init = time.time()
        # wait for other nodes to start receiving
        # time.sleep(0.1*(5-n))

        while shuffcount <= shuff:  # main coded shuffling running loop (for shuff iterations)
            mcast_send.send(n, 1, e.get_work_file())  # send data to other node
            data_pts = e.get_work_file()  # data points for current iteration to use for training
            print('training')
            w, fn = SVM.svm(w, data_pts, eta, lam, tau, d, weight, shuff=0, N=Num, n=n - 1) #train on tau iterations data_pts d
            if not cache_q.qsize() == 0:
                a = cache_q.get()  # tuple in form (priority integer, DATA)
                e.recv(a[1])
                time_init = time.time()
                shuffcount = shuffcount + 1
            else:
                print('Resending could not assert data')

            if time.time() >= (time_init + 60):  # times out 60s of not receiving data
                print("Error: threads timed out")
                break
        # send w to agg
        node_client.client(w, fn, host)
        k = k+1

    if not mcast_recv1.kill:  # kills threads by ending underlying function(s)
        mcast_recv1.kill = True
        print('Threads killed')


run()
