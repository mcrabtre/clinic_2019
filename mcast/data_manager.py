"""
Created 15AUG2019 by mcrabtre
"""
import pandas as pd
import numpy as np

'''
    **data partitions**
    This module manages data partitions and subpartitions for encoded shuffling including 5 nodes.
    Total data size must be some multiple of 20 data pts. The data set is divided into 5 distinct files. 
    each node has 1 file in addition to 1/4 of each other nodes file to make a total of 2 file sizes
    per node. This data is stored in a work.csv file in the encode_manager directory, which is routinely 
    read from and rewritten as data shuffling occurs. 
    
    **encoding/decoding**
    encoding is a bitwise XOR operation on two file partitions, this results in an encoded partition 
    decoded is a bitwise XOR operation on the encoded partition and one of its original file partitions.
    This enables the data of both partitions to be contained within the encoded, a partitions data is 
    recovered using the other partition it was encoded to.
    
    **shuffling stages**
    shuffling takes place in two stages, the encode send stage, and the cleanup stage. The encode send stage 
    encodes two partitions and sends it, eventually this will be received by two other nodes. Stage 2 is a 
    single non-coded partition. These two stages were necessary for the entire data set to be shuffled among the nodes
    each iteration. 
    
    **receiving**
    this manager completely automates the receiving process, it takes in 3 different partitions. Stage1_m is the 
    partition received from the minor node, or the node wih the next successive node number.
'''
data_size = 20
node = 0
itr = 1
set_flag = False

def create_workspace(nodeNum,filePath,totalDataSize): #creates a headerless workspace file containing working file and partitions
    if(totalDataSize % 20) != 0: #check that total data size is a multiple of 20
        if totalDataSize < 20:
            totalDataSize = 20
        else:
            totalDataSize = totalDataSize - (totalDataSize % 20)

    global data_size #assign to global variables for use by other functions
    data_size = totalDataSize
    global node
    node = nodeNum
    global itr
    itr = 1
    global set_flag
    set_flag = True
    fileSize = int(totalDataSize/5)
    f = pd.read_csv(filePath, dtype='uint8', skiprows=int((nodeNum - 1) * fileSize), nrows=fileSize).values # write working file from traning data into ndarray f
    np.savetxt("work.csv", f, '%i', delimiter=",") #creates, and saves f into work.csv (in same directory as data_manager.py)
    #return f


def get_work_file(): #returns current training data for the node. (dependant on shuffle iteration)
    global data_size
    file_size = data_size/5
    return pd.read_csv('work.csv', header=None, dtype='uint8', skiprows=0, nrows=file_size).values


def get_itr(): #returns current iteration
    global itr
    return itr


def recv(wf):
    global data_size
    global node
    global itr
    np.savetxt("work.csv", wf, '%i', delimiter=",")  # saves new wf into work.csv
    itr = itr + 1
    #return wf


def node_tracker():
    global node
    recv_node = cycle5(node+1)
    return recv_node


def cycle5(value): # for ease of iterative counting
    if value > 0:
        if value <= 5:
            return value
        else:
            return cycle5(value-5)
    else:
        return cycle5(value+5)


def cycle4(value): # for ease of iterative counting
    if value > 0:
        if value <= 4:
            return value
        else:
            return cycle5(value-4)
    else:
        return cycle5(value+4)



#create_workspace(1,'test.csv',20)
'''
# misc testing code
create_workspace(4, 'test.csv', 40)
print(cycle5(27))
p1 = pd.read_csv('test.csv', dtype='uint8', skiprows=15, nrows=2).values
print('p1 is ',p1)

p2 = pd.read_csv('test.csv', dtype='uint8', skiprows=0, nrows=2).values
print('p2 is ',p2)

enc = encode(p1,p2)
print('enc is ',enc)
dec1 = decode(p2,enc)
print('dec1 is ',dec1)
print('enc is ',enc)
print('p1 is ',p1)
print('p2 is ',p2)


dec2 = decode(p1,enc)
print('dec2 is ',dec2)
print('enc is ',enc)
print('p1 is ',p1)
print('p2 is ',p2)

wf = get_work_file()
print('wf is ',wf)

print('dec1 = p1 is ', (dec1 == p1))
print('dec2 = p2 is ', (dec2 == p2))
'''
