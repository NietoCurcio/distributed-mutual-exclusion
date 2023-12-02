import socket
import os
import time
from process import REQUEST_ID, GRANT_ID, RELEASE_ID
from process import HOST, PORT, BUFFER_SIZE
from process import INTERVAL_TIME, LOOP_RANGE
from process import FILENAME
from process import Helper
from process import Process


class BadProcess(Process):
    def send_request(self, process_id, iteration):
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        coordinator_address = (HOST, PORT)

        # send_release before request makes it a bad process
        self._send_release(process_id, client_socket, coordinator_address)

        message = Helper.format_message(REQUEST_ID, process_id)
        client_socket.sendto(message.encode(), coordinator_address)
        print(f"Processo \033[92m{process_id}\033[0m enviou uma requisição ao coordenador.")

        data, address = client_socket.recvfrom(BUFFER_SIZE)
        message = data.decode()
        print(f"Processo \033[92m{process_id}\033[0m recebeu uma mensagem do coordenador: {message}.")

        message_id, process_id = Helper.parse_message(message)

        if message_id == GRANT_ID:
            current_time = Helper.get_milliseconds_current_time()
            self._write_in_critical_section(process_id, current_time, iteration)
            self._simulate_long_running_process(process_id)
            self._send_release(process_id, client_socket, coordinator_address)


def main():
    process = BadProcess()
    process_id = process.get_PID()
    print(f"Processo \033[92m{process_id}\033[0m inicializado.")
    for i in range(LOOP_RANGE):
        process.send_request(process_id, i)

if __name__ == "__main__":
    main()
    
