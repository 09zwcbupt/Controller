import multiprocessing
import time
from pprint import pprint

e = multiprocessing.Event()
quit = multiprocessing.Event()

def func(msg):
    try:
        e.wait()
        while not quit.is_set():
            print msg
            time.sleep(1)    
        e.clear()
    except KeyboardInterrupt:
        print "quit process"
 
if __name__ == "__main__":
    timeout = 0
    p = multiprocessing.Process(target=func, args=("p-hello", ))
    q = multiprocessing.Process(target=func, args=("q-hello", ))
    #pprint(p.__dict__)
    try:
        p.start()
        q.start()
        print "Trigger event e"
        e.set()
        quit.wait()
    except KeyboardInterrupt:
        quit.set()
        p.join(timeout)
        q.join(timeout)
        print "Sub-process done."
