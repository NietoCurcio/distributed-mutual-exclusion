import threading
import time
from collections import deque

FINAL_RESULT = []

INITIAL_LOCK_TIME = 20
INTERVAL_RELEASE_TIME = 10
SIMULATED_TIME = 5

POSSIBLE_ORDERS = {
    'order1': ['first-call', 'second-call', 'third-call'],
    'order2': ['second-call', 'first-call', 'third-call'],
    'order3': ['second-call', 'third-call', 'first-call'],
    'order4': ['third-call', 'second-call', 'first-call'],
    'order5': ['third-call', 'first-call', 'second-call'],
    'order6': ['first-call', 'third-call', 'second-call']
}
SELECTED_ORDER = 'order5'

order = deque()
selected_order = POSSIBLE_ORDERS[SELECTED_ORDER]
for item in selected_order:
    order.append(item)

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

class ThreadsStudy:
    def __init__(self):
        self.lock = threading.Lock()
        self.order_condition = threading.Condition()

    def setInterval(self, main_thread):
        if main_thread.is_alive():
            threading.Timer(INTERVAL_RELEASE_TIME, lambda:self.setInterval(main_thread)).start()
        if self.lock.locked():
            self.lock.release()
            print(f"{bcolors.HEADER}Released lock{bcolors.ENDC}")
    
    def lock_thread_for_time(self, initial_lock_time):
        with self.lock:
            print(f"{bcolors.HEADER}Initial locked for {initial_lock_time} secs\n{bcolors.ENDC}")
            time.sleep(initial_lock_time)

    def is_thread_turn(self, thread, order):
        return thread == order[0]

    def fn(self, thread, order):
        print(f"{bcolors.OKCYAN}TH: {thread}, Locked initially? {self.lock.locked()}{bcolors.ENDC}")

        with self.order_condition:
            """
            while not self.is_thread_turn(thread, order):
                 print(f"{bcolors.WARNING}TH: {thread} - order_condition.wait(){bcolors.ENDC}")
                 self.order_condition.wait()
            THIS COMMENTED CODE IS THE SAME AS THE wait_for version
            """
            self.order_condition.wait_for(lambda : self.is_thread_turn(thread, order))

            print(f"{bcolors.OKBLUE}TH: {thread}, current order: {order}{bcolors.ENDC}")
            print(f"{bcolors.OKGREEN}TH: {thread} - can execute (correct FIFO order) {bcolors.ENDC}")

            print(f"{bcolors.OKCYAN}TH: {thread} is locked? {self.lock.locked()}{bcolors.ENDC}")
            self.lock.acquire()
            print(f"fn: {thread} - simulating {SIMULATED_TIME} secs{bcolors.ENDC} of execution")
            time.sleep(SIMULATED_TIME)
            order.popleft()
            FINAL_RESULT.append(thread)
            self.order_condition.notify_all()

a = ThreadsStudy()

name_first = 'first-call'
name_second = 'second-call'
name_third = 'third-call'

main_thread = threading.current_thread()
th = threading.Thread(target=a.setInterval, args=(main_thread,), name='setInterval')
th.start()
th.join()

th0 = threading.Thread(target=a.lock_thread_for_time, args=(INITIAL_LOCK_TIME,), name='lock_thread')
th0.start()

th1 = threading.Thread(target=a.fn, args=(name_first, order), name=name_first)
th2 = threading.Thread(target=a.fn, args=(name_second, order), name=name_second)
th3 = threading.Thread(target=a.fn, args=(name_third, order), name=name_third)

th1.start()
th2.start()
th3.start()

th0.join()
th1.join()
th2.join()
th3.join()

print(f"Final result: {FINAL_RESULT}, FINAL_RESULT == selected_order? {FINAL_RESULT == selected_order}")