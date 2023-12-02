import threading
import time

WAIT_TIME = 5

class A:
    def __init__(self):
        self.lock = threading.Lock()

    def fn(self, text):
        print(f"FN: {text} - LOCKED? {self.lock.locked()}" )
        self.lock.acquire()
        print(F"fn: {text} - waiting {WAIT_TIME} secs")
        time.sleep(WAIT_TIME)
        self.lock.release()

a = A()
th = threading.Thread(target=a.fn, args=('first-call',), name='first-call')
th2 = threading.Thread(target=a.fn, args=('second-call',), name='second-call')
th3 = threading.Thread(target=a.fn, args=('third-call',), name='third-call')

th.start()
th3.start()
th2.start()

th.join()
th2.join()
th3.join()
