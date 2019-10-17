import delay
import threading
import queue
import random
import time


def run(itr=5):
    data_q = queue.PriorityQueue(3)
    icount = 1
    data = ['first', 'second', 'third']
    threads = {}
    for i in range(3):
        sec = random.randint(1, 3)
        threads[i] = threading.Thread(target=delay.delay, args=(sec, data_q, data[i], i + 1), daemon=False)
        threads[i].start()
        print('starting thread ', i)
        time_init = time.time()
    while icount <= itr:
        if data_q.full():
            for i in range(data_q.qsize()):
                print(data_q.get())
                icount = icount + 1
        if time.time() >= (time_init + 60):
            break
        else:
            print('queue not full', threading.active_count(), data_q.qsize())
    if not delay.get_kill():
        delay.kill = True
