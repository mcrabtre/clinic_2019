# -*- coding: utf-8 -*-
"""
Created on Sun Oct 14 12:10:07 2018

@author: fog
"""
#import sys
import numpy as np
import types
import aggr_server_v1_2
import aggr_client_v1_2
#import SVMfake
import averager
import NodeSvm
import time

starttime = time.time()

# pass in initial w, ip addresses, and # global iterations
def run(host,node_ip,k,tau,win):
    numcon = len(node_ip) # number of nodes
    w = win
    
    data = types.SimpleNamespace(w=w,nodenum=0,tau=tau, k=k) #client(host,data)
    for y in range (0,k): # aggregator as client, k global iterations       
        for x in range (0,numcon): # iterate through the ips of the nodes
            data.nodenum = x #types.SimpleNamespace(w=w,nodenum=x,tau=tau) 
            aggr_client_v1_2.client(node_ip[x],data)
            print('sent to node ', x)
    
        ww, fnfn = aggr_server_v1_2.aggr_server(host,numcon) # aggregator as server; get ws from nodes        
        # NodeSVM(w, N, tau=10, D=100, eta=.01, lam=1)
        N = len(node_ip) + 1
        wagg, fnagg = NodeSvm.NodeSVM(w,N,tau) # run SVM on aggregator
        ww = np.append(ww,wagg)
        fnfn = np.append(fnfn, fnagg)
        print('have all ws')
        
        num_nodes = numcon + 1 # number of machines calculating the loss fn(including aggregator)
        w = averager.averager(ww, num_nodes)        
        print('averaged')
        
    return w,fnfn
 
# host = '192.168.0.14'  # '127.0.0.1' # aggregator ip for use in server
host = '192.168.1.2'  # '127.0.0.1' # aggregator ip for use in server
# node_ip ['192.168.0.11','192.168.0.10']#,'192.168.0.13','192.168.0.14','192.168.0.16']
node_ip = ['192.168.1.4', '192.168.1.3', '192.168.1.5']#, '192.168.1.6']
# ['127.0.0.1'] # node ips; len(node_ip) = 1;
k =  5 # number of global updates
tau = 11 # number of local iterations
#win = [1,2,3,4] # initial vector
win = np.zeros(784)
w,fn = run(host,node_ip,k,tau,win)
print('done')
print(time.time() - starttime)
 

