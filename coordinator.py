import textwrap
import time
import socket
import threading
from queue import Queue
from collections import defaultdict
import logging
from typing import Generic, TypeVar

def get_logger():
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s:%(name)s:%(message)s')
    file_handler = logging.FileHandler('coordinator.log')
    file_handler.setFormatter(formatter)
    sh_handler = logging.StreamHandler()
    sh_handler.setFormatter(formatter)
    logger.addHandler(sh_handler)
    logger.addHandler(file_handler)
    return logger

class Typings:
    type process_id = str
    type counter = int

class Coordinator:
    REQUEST_ID: str = '1'
    GRANT_ID: str = '2'
    RELEASE_ID: str = '3'
    SIMULATED_WAIT_TIME: int = 5
    HOST: str = 'localhost'
    PORT: int = 9999
    BUFFER_SIZE: int = 1024

    def __init__(self):
        self.queue = Queue()
        self.process_count : dict[Typings.process_id, Typings.counter]= defaultdict(int)
        self.lock = threading.Lock()
        self.exit_flag = threading.Event()

    def _format_message(self, message_id: str, process_id: str, size: int = 10, separator = '|'):
        message = f"{message_id}{separator}{process_id}{separator}"
        message += '0' * (size - len(message))
        return message[:size]
    
    def _parse_message(self, message: str, separator = '|'):
        message_id, process_id, filler = message.split(separator)
        return message_id, process_id

    def _create_socket(self):
        # socket.AF_INET = IPv4 # socket.SOCK_DGRAM = UDP
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        server_socket.bind((self.HOST, self.PORT))
        server_socket.settimeout(0.1)
        return server_socket
    
    def receive_requests(self):
        server_socket = self._create_socket()
        print("Coordenador aguardando conexões...")
        while not self.exit_flag.is_set():
            try:
                data, address = server_socket.recvfrom(self.BUFFER_SIZE)
                message = data.decode()
                message_id, process_id = self._parse_message(message)
                with self.lock:
                    if message_id == self.REQUEST_ID:
                        formatted_message = self._format_message(self.GRANT_ID, process_id)
                        server_socket.sendto(formatted_message.encode(), address)
                        self.queue.put(process_id)
            except socket.timeout:
                pass
        print(f"Thread: {threading.current_thread().name} encerrada")

    def process_requests(self):
        while not self.exit_flag.is_set():
            if not self.queue.empty():
                with self.lock:
                    process_id = self.queue.get()
                    self.process_count[process_id] += 1
                    print(f"Processo {process_id} acessou a região crítica.")
                    time.sleep(self.SIMULATED_WAIT_TIME)
        print(f"Thread: {threading.current_thread().name} encerrada")

    def command_interface(self):
        while not self.exit_flag.is_set():
            input_msg = textwrap.dedent(
                """
                Digite o comando:
                1 - imprimir fila
                2 - imprimir contador
                3 - encerrar coordenador
                """
            )
            command = input(input_msg)
            if command == '1':
                with self.lock:
                    print(list(self.queue.queue))
            elif command == '2':
                with self.lock:
                    print(self.process_count)
            elif command == '3':
                print("Encerrando o coordenador...")
                self.exit_flag.set()
                break
        print(f"Thread: {threading.current_thread().name} encerrada")

    def start(self):
        request_thread = threading.Thread(target=self.receive_requests, name="request_thread")
        process_thread = threading.Thread(target=self.process_requests, name="process_thread")
        interface_thread = threading.Thread(target=self.command_interface, name="command_interface_thread")

        request_thread.start()
        process_thread.start()
        interface_thread.start()

        print(f'\033[92m \nThreads running:\n{[thread.name for thread in threading.enumerate()]} \033[0m')

        request_thread.join()
        process_thread.join()
        interface_thread.join()

        print(f"Coordenador encerrado (Thread name: {threading.current_thread().name})")

if __name__ == "__main__":
    coordinator = Coordinator()
    coordinator.start()
