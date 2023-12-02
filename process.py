import socket
import os
import time

REQUEST_ID = '1'
GRANT_ID = '2'
RELEASE_ID = '3'

HOST = 'localhost'
PORT = 9999
BUFFER_SIZE = 1024

INTERVAL_TIME = 10
LOOP_RANGE = 3
FILENAME = 'resultado.txt'

class Helper:
    @staticmethod
    def get_milliseconds_current_time():
        return time.time()
    
    @staticmethod
    def format_message(message_id: str, process_id: str, size=10, separator='|'):
        message = f"{message_id}{separator}{process_id}{separator}"
        message += '0' * (size - len(message))
        return message[:size]

    @staticmethod
    def parse_message(message: str, separator='|'):
        message_id, process_id, filler = message.split(separator)
        return message_id, process_id
    
    @staticmethod
    def format_timestamp_with_milliseconds(timestamp: float):
        timestamp = 1701557732.966179
        milliseconds = int((timestamp - int(timestamp)) * 1e6)
        time_struct = time.gmtime(timestamp)
        formatted_time = time.strftime('%Y-%m-%d %H:%M:%S', time_struct)
        formatted_time_with_microseconds = f"{formatted_time}.{milliseconds:06d}"
        return formatted_time_with_microseconds
    
class Process:
    def get_PID(self):
        pid = os.getpid()
        message_length = 10
        message_id_length = 1
        pid_length_threshold = message_length - message_id_length
        return str(pid)[-pid_length_threshold:]

    def _simulate_long_running_process(self, process_id):
        print(f"Processo \033[92m{process_id}\033[0m iniciou um processo longo ({INTERVAL_TIME} secs).")
        time.sleep(INTERVAL_TIME)

    def _write_in_critical_section(self, process_id, current_time, step):
        with open(FILENAME, 'a') as file:
            file.write(f'{process_id} | {current_time} | {step+1}/{LOOP_RANGE}\n')
        print(f"Processo \033[92m{process_id}\033[0m escreveu no arquivo.")
    
    def _send_release(self, process_id, client_socket, coordinator_address):
        message = Helper.format_message(RELEASE_ID, process_id)
        client_socket.sendto(message.encode(), coordinator_address)
        print(f"Processo \033[92m{process_id}\033[0m enviou uma mensagem de release ao coordenador.")

    def send_request(self, process_id, iteration):
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        coordinator_address = (HOST, PORT)

        message = Helper.format_message(REQUEST_ID, process_id)
        client_socket.sendto(message.encode(), coordinator_address)
        print(f"Processo \033[92m{process_id}\033[0m enviou uma requisição ao coordenador.")

        data, address = client_socket.recvfrom(BUFFER_SIZE)
        message = data.decode()
        print(f"Processo \033[92m{process_id}\033[0m recebeu uma mensagem do coordenador: {message}.")

        message_id, process_id = Helper.parse_message(message)

        if message_id == GRANT_ID:
            current_time = Helper.format_timestamp_with_milliseconds(Helper.get_milliseconds_current_time())
            self._write_in_critical_section(process_id, current_time, iteration)
            self._simulate_long_running_process(process_id)
            self._send_release(process_id, client_socket, coordinator_address)

def main():
    process = Process()
    process_id = process.get_PID()
    print(f"Processo \033[92m{process_id}\033[0m inicializado.")
    for i in range(LOOP_RANGE):
        process.send_request(process_id, i)

if __name__ == "__main__":
    main()
    
