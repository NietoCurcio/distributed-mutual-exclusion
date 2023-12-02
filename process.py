import socket
import os
import time

REQUEST_ID = '1'
GRANT_ID = '2'
RELEASE_ID = '3'

HOST = 'localhost'
PORT = 9999
BUFFER_SIZE = 1024

INTERVAL_TIME = 1
LOOP_RANGE = 3
FILENAME = 'resultado.txt'

"""TODO: improve the cleaness of this code"""

def simulate_long_running_process(process_id):
    print(f"Processo \033[92m{process_id}\033[0m iniciou um processo longo ({INTERVAL_TIME} secs).")
    time.sleep(INTERVAL_TIME)

def _get_milliseconds_current_time():
    return time.time()

def write_in_critical_section(process_id, current_time, step):
    with open(FILENAME, 'a') as file:
        file.write(f'PID={process_id} | TIMESTAMP={current_time} | STEP={step+1}/{LOOP_RANGE}\n')
    print(f"Processo \033[92m{process_id}\033[0m escreveu no arquivo.")
    
def send_release(process_id, client_socket, coordinator_address):
    message = _format_message(RELEASE_ID, process_id)
    client_socket.sendto(message.encode(), coordinator_address)
    print(f"Processo \033[92m{process_id}\033[0m enviou uma mensagem de release ao coordenador.")

def _format_message(message_id: str, process_id: str, size=10, separator='|'):
    message = f"{message_id}{separator}{process_id}{separator}"
    message += '0' * (size - len(message))
    return message[:size]

def _parse_message(message: str, separator='|'):
    message_id, process_id, filler = message.split(separator)
    return message_id, process_id

def send_request(process_id, iteration):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    coordinator_address = (HOST, PORT)

    message = _format_message(REQUEST_ID, process_id)
    client_socket.sendto(message.encode(), coordinator_address)
    print(f"Processo \033[92m{process_id}\033[0m enviou uma requisição ao coordenador.")

    data, address = client_socket.recvfrom(BUFFER_SIZE)
    message = data.decode()
    print(f"Processo \033[92m{process_id}\033[0m recebeu uma mensagem do coordenador: {message}.")

    message_id, process_id = _parse_message(message)

    if message_id == GRANT_ID:
        current_time = _get_milliseconds_current_time()
        write_in_critical_section(process_id, current_time, iteration)
        simulate_long_running_process(process_id)
        send_release(process_id, client_socket, coordinator_address)

def _get_PID():
    pid = os.getpid()
    message_length = 10
    message_id_length = 1
    pid_length_threshold = message_length - message_id_length
    return str(pid)[-pid_length_threshold:]

def main():
    process_id = _get_PID()
    print(f"Processo \033[92m{process_id}\033[0m inicializado.")
    for i in range(LOOP_RANGE):
        send_request(process_id, i)

if __name__ == "__main__":
    main()
    
