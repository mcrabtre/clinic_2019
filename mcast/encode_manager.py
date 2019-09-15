"""
Created 15AUG2019 by mcrabtre
"""
import pandas as pd
import numpy as np
import os
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
    encodes two partitions and sends it, eventually this will be received by two other nodes.  
'''
data_size = 20
node = 0
itr = 1


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
    otherNodes = [1,2,3,4,5]
    otherNodes.remove(nodeNum)
    fileSize = int(totalDataSize/5)
    f = pd.read_csv(filePath, dtype='uint8', skiprows=int((nodeNum - 1) * fileSize), nrows=fileSize).values # write working file from traning data into ndarray f
    for x in otherNodes: #get partitions of other nodes files
        if x < nodeNum:
            p = pd.read_csv(filePath, dtype='uint8', skiprows=int(((x-1)*fileSize)+((nodeNum-2)/4)*fileSize), nrows=fileSize/4).values
        else:
            p = pd.read_csv(filePath, dtype='uint8', skiprows=int(((x-1)*fileSize)+((nodeNum-1)/4)*fileSize), nrows=fileSize/4).values
        f = np.concatenate((f, p), axis=0, out=None)

    np.savetxt("work.csv", f, '%i', delimiter=",") #creates, and saves f into work.csv (in same directory as encode_manager.py)


def get_work_file(): #returns current training data for the node. (dependant on shuffle iteration)
    global data_size
    file_size = data_size/5
    return pd.read_csv('work.csv', header=None, dtype='uint8', skiprows=0, nrows=file_size).values


def stage1_send(): #returns a tuple containing nodes to receive from, and the encoded data to send
    global data_size
    global node
    global itr
    recv_nodes = (cycle5(node+1),cycle5(node+2))
    part_mutation = [4,1,2,3,4]
    file_mutation = [3,4,1,2,3]
    for i in range(1,itr):
        part_mutation.insert(4, part_mutation.pop(0))
        file_mutation[cycle5(5-(i-1))-1] = cycle4(file_mutation[cycle5(5-(i-1))-1]-1)
    part_size = int(data_size/20)
    p1 = pd.read_csv('work.csv', header=None, dtype='uint8', skiprows=(file_mutation[node-1]-1)*part_size, nrows=part_size).values
    p2 = pd.read_csv('work.csv', header=None, dtype='uint8', skiprows=4*part_size + (part_mutation[node-1]-1)*part_size, nrows=part_size).values
    data_send = encode(p1,p2)
    return recv_nodes, data_send


def stage2_send(): #returns data to send for stage 2
    global data_size
    global node
    global itr
    file_mutation = [2,3,4,1,2]
    for i in range(1,itr):
        file_mutation[cycle5(5-(i-1))-1] = cycle4(file_mutation[cycle5(5-(i-1))-1]-1)
    part_size = int(data_size / 20)
    p1 = pd.read_csv('work.csv', header=None, dtype='uint8', skiprows=(file_mutation[node-1]-1)*part_size, nrows=part_size).values
    return p1


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


def encode(part1, part2): #bitwise XOR encode
    #newPart = np.zeros(shape= part1.shape, dtype= np.uint8)
    if part1.shape != part2.shape:
        raise Exception('Error... both partitions must be of equal dimensions')
    newPart = part1 ^ part2
    return newPart


def decode(key, part): #partitions are decoded in the same way they are encoded
    new = encode(key, part)
    return new


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
