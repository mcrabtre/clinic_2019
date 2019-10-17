import time


def delay(seconds, data_que, job_que):
    a = job_que.get()
    time.sleep(seconds)
    data_que.put(a)
    job_que.task_done()
    job_que.put(a)
    return