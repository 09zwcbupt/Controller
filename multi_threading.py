import threading
import datetime
import time
        
class ThreadClass(threading.Thread):
    def run(self):
        now = datetime.datetime.now()
        print "%s says Hello World at time: %s" %(self.getName(), now)
        time.sleep(1)
        print "%s says Hello World at time: %s" %(self.getName(), now)
    def test_handler(self):
        time.sleep(3)
        print "test_handler"

for i in range(3):
    t = ThreadClass()
    t.start()