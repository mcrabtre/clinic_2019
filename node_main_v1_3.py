# -*- coding: utf-8 -*-
"""
Created on Thu Oct 11 11:33:38 2018
@author: fog
"""

import node_server_v1_3
print('imported Server')
#import SVMfake
import NodeSvm
print('imported svm')
import node_client_v1_3
print('imported client')

#def main(host,port):
def run(host):
    done = False
    print('made it to run')
    done = 0
    while True: # just to prevent endless loop, will be removed for use in pis
        node_ip = '192.168.1.3'
        #w,tau,nodenum,recvd = server(host)
        win,tau,N,k = node_server_v1_3.server(node_ip) # listen for w in, node #, tau
        print ('node #: ', N) # got info from aggregator

        wout, fn = NodeSvm.NodeSVM(win,N,tau) # run SVM on node
            
        node_client_v1_3.client(wout,fn,host)   # send w,fn    
        print ('w sent')
        done += 1
        
        if done == k:
            break    
    
    return wout,fn
 
               
##host = '192.168.0.11'
host = '192.168.1.5' # aggr ip
w, fn = run(host)
#
## tau is # iterations for SVM
## fn is loss function value after one SVM iteration



