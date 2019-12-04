import encode_manager as e
import numpy as np


def test(size, iterations):
    nodes = [1,2,3,4,5]
    itr = 1
    e.create_workspace(1, 'train.csv', size)
    e.create_workspace(2, 'train.csv', size)
    e.create_workspace(3, 'train.csv', size)
    e.create_workspace(4, 'train.csv', size)
    e.create_workspace(5, 'train.csv', size)
    while itr <= iterations:
        print('starting iteration ', itr)
        e.itr = itr
        stage1s = [0,0,0,0,0]
        stage2s = [0,0,0,0,0]
        #fill stage 1s and 2s
        for i in nodes:
            e.node = i
            stage1s[i-1] = e.stage1_send()
            stage2s[i-1] = e.stage2_send()
        curWf = [0,0,0,0,0]
        #fill current work files
        for i in nodes:
            e.node = i
            curWf[i-1] = e.get_work_file()
        nextWf = [0,0,0,0,0]
        #fill next work files
        for i in nodes:
            if e.itr != itr:
                e.itr = itr
            e.node = i
            (s1m, s1M, s2) = e.node_tracker()
            e.recv(stage1s[s1m-1], stage1s[s1M-1], stage2s[s2-1])
            nextWf[i - 1] = e.get_work_file()
            e.itr = itr
        #check integrity of files
        for i in nodes:
            e.node = i
            if not np.array_equal(curWf[i-1],nextWf[e.cycle5(i-1)-1]):
                print('problem with node ', i, ' at iteration ', itr)
                #print('work file is ', nextWf[e.cycle5(i-1)-1],' should be ', curWf[i-1])
        itr = itr + 1


    print("End of Test")






