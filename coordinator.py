import textwrap
import socket
import threading
from queue import Queue
from collections import defaultdict
import logging

def get_logger(name):
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(levelname)s | %(asctime)s | %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    file_handler = logging.FileHandler('coordinator.log')
    file_handler.setFormatter(formatter)
    sh_handler = logging.StreamHandler()
    sh_handler.setFormatter(formatter)
    logger.addHandler(sh_handler)
    logger.addHandler(file_handler)
    return logger

logger = get_logger(__name__)

class Typings:
    type process_id = str
    type message_id = str
    type counter = int
    type host = str
    type pid = int
    type address = tuple[host, pid]

class Coordinator:
    REQUEST_ID: str = '1'
    GRANT_ID: str = '2'
    RELEASE_ID: str = '3'
    HOST: str = 'localhost'
    PORT: int = 9999
    BUFFER_SIZE: int = 1024

    def __init__(self):
        self.queue: Queue[tuple[Typings.process_id, Typings.message_id, Typings.address]] = Queue()
        self.process_count : dict[Typings.process_id, Typings.counter] = defaultdict(int)
        self.exit_flag = threading.Event()
        
        self.queue_lock = threading.Lock()
        self.critical_section_lock = threading.Lock()
        self.lock_owner: Typings.process_id | None = None

        self.server_socket: socket.socket | None = None

    def log_exitting_info(thread_fn):
        def wrapper(*args, **kwargs):
            thread_fn(*args, **kwargs)
            logger.info(f"Thread {threading.current_thread().name} encerrada")
        return wrapper

    def _format_message(self, message_id: str, process_id: str, size: int = 10, separator = '|'):
        message = f"{message_id}{separator}{process_id}{separator}"
        message += '0' * (size - len(message))
        return message[:size]
    
    def _parse_message(self, message: str, separator = '|'):
        message_id, process_id, filler = message.split(separator)
        return message_id, process_id

    def _initialize_socket(self):
        IP_V4_ADDRESS_FAMILY = socket.AF_INET
        UDP_PROTOCOL = socket.SOCK_DGRAM
        server_socket = socket.socket(IP_V4_ADDRESS_FAMILY, UDP_PROTOCOL)
        server_socket.bind((self.HOST, self.PORT))
        server_socket.settimeout(0.1)
        self.server_socket = server_socket
    
    @log_exitting_info
    def receive_requests(self):
        self._initialize_socket()
        logger.info(f"{threading.current_thread().name}: Coordenador aguardando conexoes...")
        while not self.exit_flag.is_set():
            try:
                data, address = self.server_socket.recvfrom(self.BUFFER_SIZE)
                message = data.decode()

                logger.info(
                    f"{threading.current_thread().name}: Mensagem recebida: {message} de {address}"
                )
                message_id, process_id = self._parse_message(message)

                if message_id != self.REQUEST_ID and message_id != self.RELEASE_ID:
                    logger.error(f"{threading.current_thread().name}: Mensagem inválida: {message}")
                    continue
                
                with self.queue_lock:
                    self.queue.put((process_id, message_id, address))
            except socket.timeout:
                pass

    def _process_release(self, process_id: str, address: Typings.address):
        if not self.critical_section_lock.locked():
            logger.error(
                f"{threading.current_thread().name}: Processo {process_id} tentou liberar o recurso sem o recurso estar ocupado"
            )
            return
        
        if self.lock_owner != process_id:
            logger.error(
                f"{threading.current_thread().name}: Processo {process_id} tentou liberar o recurso, mas ele nao eh o dono do recurso atualmente"
            )
            return

        self.lock_owner = None
        self.critical_section_lock.release()
        logger.info(
            f"{threading.current_thread().name}: Processo {process_id} liberou o recurso"
        )
        self.process_count[process_id] += 1

    def _process_acquire(self, process_id: str, address: Typings.address):
        if self.critical_section_lock.locked():
            # logger.info(
            #     f"{threading.current_thread().name}: Processo {process_id} requisitou o recurso, mas ele está ocupado, então ele foi colocado na fila"
            # )
            """
            TODO: fix process_requests, _process_acquire
            so that when a process that was put back in the queue
            does not keep calling _process_acquire again and again, it should call just once
            """
            with self.queue_lock:
                self.queue.put((process_id, self.REQUEST_ID, address))
            return
        
        self.critical_section_lock.acquire()
        self.lock_owner = process_id
        logger.info(
            f"{threading.current_thread().name}: Processo {process_id} requisitou o recurso"
        )
        formatted_message = self._format_message(self.GRANT_ID, process_id)
        self.server_socket.sendto(formatted_message.encode(), address)

    @log_exitting_info
    def process_requests(self):
        while not self.exit_flag.is_set():
            if self.queue.empty():
                continue

            with self.queue_lock:
                process_id, message_id, address = self.queue.get()

            if message_id == self.RELEASE_ID:
                self._process_release(process_id, address)

            if message_id == self.REQUEST_ID:
                self._process_acquire(process_id, address)

    @log_exitting_info
    def command_interface(self):
        input_msg = textwrap.dedent(
            """
            Digite o comando:
            1 - imprimir fila
            2 - imprimir contador
            3 - encerrar coordenador
            """
        )
        while not self.exit_flag.is_set():
            command = input(input_msg)
            if command == '1':
                with self.queue_lock:
                    print(list(self.queue.queue))
            elif command == '2':
                with self.queue_lock:
                    print(self.process_count)
            elif command == '3':
                logger.info("Encerrando o coordenador...")
                self.exit_flag.set()

    def start(self):
        request_thread = threading.Thread(target=self.receive_requests, name="request_thread")
        process_thread = threading.Thread(target=self.process_requests, name="process_thread")
        interface_thread = threading.Thread(target=self.command_interface, name="command_interface_thread")

        request_thread.start()
        process_thread.start()
        interface_thread.start()

        print(f'\033[92m \nThreads running:\n{[thread.name for thread in threading.enumerate()]} \033[0m\n')

        request_thread.join()
        process_thread.join()
        interface_thread.join()

        logger.info(f"Coordenador encerrado (Thread name: {threading.current_thread().name})")

if __name__ == "__main__":
    coordinator = Coordinator()
    coordinator.start()
