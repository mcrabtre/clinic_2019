# -*- coding: utf-8 -*-
"""
Created on Sat Mar 30 10:47:30 2019

@author: mcrabtre
"""

import numpy as np
import types
import AccTest
import aggr_client_v1_3 as aggr_client
import aggr_server
import nodeDetection
import med_avg
import time
import matplotlib.pyplot as plt

'''
    The run of the system. It will initialize conditions and detect available nodes and 
    assumes that all devices connected to the router are ready to act as a node.
    Then it will enter a loop to perform K global updates.
    It will send a data packet to each node
    then it will wait to receive from each node. 
    Once it has data from each node it will process the w vectors (based on avc) and store the loss functions
    It also runs an accuracy test to show progress
    Once the loop is finished it plots the functions and returns the w vector, loss functions, and averages
'''


def run(K=5, tau=10, avc=0, d=4, shuff=2, pad_value=1, graph=False):
    # K = global iterations
    # tau = local iterations
    # avc = w vector processing (see line 84)
    # d = number of data points per node (must be a multiple of 4 for coded multicast)
    # shuff = number of data shuffles per global iteration, (performs tau iterations after each shuffle)
    # pad_value = pads training data sent by a factor of pad_value, for testing purposes
    # graph = boolean to display loss function graph after completing training cycle

    router_ip = '192.168.0.1'
    not5 = True
    while not5:
        host, iplist = nodeDetection.run(router_ip)  # host is agg ip address
        # finds other nodes connected to router and gives its TCP ip address
        # may ditch this to implement full multicast including agg
        print('waiting for 5 nodes')
        not5 = (iplist.__len__() != 5)
        time.sleep(1.0)
    tinit = time.time()
    node_dict = {}
# assign node numbers
    print('assigning nodes')
    n = 0
    for ind in iplist:
        node_dict[ind] = n
        n += 1
    N = n
# initialize data size d, iterations tau, and matrices for w, averages, and loss functions.
    print('initializing data')
    if tau == 0:
        tau = N
    w = np.zeros(784)
    fnfn = np.zeros(shape=(K*tau, 5))
    accs = np.zeros(K)
    print('starting global updates')

# Start global updates
    for k in range(0, K): # aggregator as client, k global iterations
        # send global update information to nodes
        # Currently using the same dataset throughout. change k=k to refresh data
        # d is number of data points per node work file (each node actually stores 2*d
        data = types.SimpleNamespace(w=w, k=k, K=K, host=host, pad_value=pad_value, node_dict=node_dict, d=d, tau=tau, shuff=shuff)#data_pts=data_pts) #data on nodes

        # Send Data
        # mcast_send.send(data) # alternative to sending to nodes one at a time.
        for i in range(0,N):  # Send to each node
            aggr_client.client(iplist[i], data)
        
        # aggregator as server; get ws from nodes 
        result = aggr_server.aggr_server(host, N)
        ww = result.w
        # average loss function across all nodes
        for j in range(0, tau):
            fnfn[j + k * (tau - 1), 0] = result.fn[j]
            fnfn[j + k * (tau - 1), 1] = result.fn[j + (tau - 1)]
            fnfn[j + k * (tau - 1), 2] = result.fn[j + 2 * (tau - 1)]
            fnfn[j + k * (tau - 1), 3] = result.fn[j + 3 * (tau - 1)]
            fnfn[j + k * (tau - 1), 4] = result.fn[j + 4 * (tau - 1)]

        # Process the w
        if avc == 1:
            w = med_avg.med(ww)
        elif avc == 2:
            w = med_avg.med_avg(ww)
        else:
            w = med_avg.mean(ww)
        data.w = w  # update w in data

        accs[k] = AccTest.AccTest(w)
    tfin = time.time()
    t_total = tfin-tinit

    # Graph the loss functions
    if graph:
        plt.plot(fnfn)
        plt.title('Loss Functions for each Node')
        plt.show()
    print(accs)
    return t_total


""" this is the limits test it runs the main loop multiple times changing the input parameters each iteration. 
Also available is the ability run each input point multiple times and take an average. After running over the input
parameters stored in dt. the application then pauses and asks for the user to press enter. this is to allow the user
to change the running application on each node, and then rerun the test for the other application. After the loop is
finished the time values of each application is stored and plotted.
"""
dt = list(range(1, 10, 1))  # range(start_incl, end_excl, increment)
# dt.reverse()  # allows to run the test from highest to lowest values
time_u = np.zeros(shape=(len(dt)))
time_m = np.zeros(shape=(len(dt)))
for i in range(len(dt)):
    times = 0.0
    for j in range(1):  # change in range value to take an average time value
        print('App 1 running... ', dt[i], ' X data padding, ', j + 1, ' of 1 iterations')
        tim = run(pad_value=dt[i])  # change input parameter for different limits tests
        times = times + tim
    time_u[i] = times / 1  # change denominator for averaging
    print(time_u[i], ' seconds')
    time.sleep(30.0)
print('App 1 times are ', time_u)
input('please press enter to continue:')

for i in range(len(dt)):
    times = 0.0
    for j in range(1):
        print('App 2 running... ', dt[i], ' X data padding, ', j + 1, ' of 1 iterations')
        tim = run(pad_value=dt[i])
        times = times + tim
    time_m[i] = times / 1
    print(time_m[i], ' seconds')
    time.sleep(30.0)
print('App 2 times are ', time_m)
plot_times = np.array([time_u, time_m]).T
plot_data_pts = np.array(dt)
plt.plot(plot_data_pts, plot_times)
plt.title('Average training times for App 1 vs App 2')
plt.legend(('App 1', 'App 2'))
plt.xlabel('Data Padding Factor')
plt.ylabel('Completion Time (seconds)')
plt.show()
