import threading
import time

class A:
    def __init__(self):
        self.lock = threading.Lock()

    def anotherDecorator(f):
        def wrapper(*args, **kwargs):
            f(*args, **kwargs)
        return wrapper

    def someFn(f):
        def wrapper(*args, **kwargs):
            f(*args, **kwargs)
        return wrapper

    @anotherDecorator
    @someFn
    def fn(self):
        self.lock.acquire()
        print("ESTOU EM FN")
        time.sleep(5)
        self.lock.release()
    
    @anotherDecorator
    @someFn
    def fn2(self):
        self.lock.acquire()
        print("ESTOU EM FN2")
        self.lock.release()

    @anotherDecorator
    @someFn
    def fn3(self):
        print("ESTOU EM FN3")
    
a = A()
th = threading.Thread(target=a.fn, name='dale1')
th2 = threading.Thread(target=a.fn2, name='dale2')
th3 = threading.Thread(target=a.fn3, name='dale3')
th.start()
th2.start()
th3.start()

th.join()
th2.join()
th3.join()
