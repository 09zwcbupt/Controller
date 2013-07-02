
import gevent
import random
import time

import Queue

taskqueue = Queue.Queue()

def task(pid):
    """
    Some non-deterministic task
    """
    sometime = random.randint(1,10)*0.01
    taskqueue.put([pid, sometime])
    gevent.sleep(sometime)
    print('Task', pid, 'done', 'in', sometime )

def synchronous():
    for i in range(0,10):
        task(i)

def asynchronous():
    threads = [gevent.spawn(task, i) for i in xrange(10)]
    gevent.joinall(threads)

print('Synchronous:')
a = time.time()
synchronous()
print time.time()-a

print('Asynchronous:')
b = time.time()
asynchronous()
print time.time()-b

while not taskqueue.empty():
  print taskqueue.get()
