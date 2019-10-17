import delay
import threading
import queue

def run(itr=5,):
    job_q = queue.PriorityQueue()
    data_q = queue.PriorityQueue(3)
    job_q.put((1,'stage1m'))
    job_q.put((2,'stage1m'))
    job_q.put((3,'stage1m'))
    icount = 1
    while(icount <= 5):
