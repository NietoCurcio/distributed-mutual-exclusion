import socket
import os
import time

REQUEST_ID = '1'

HOST = 'localhost'
PORT = 9999
BUFFER_SIZE = 1024

INTERVAL_TIME = 20
LOOP_RANGE = 5
FILENAME = 'resultado.txt'

def _format_message(message_id: str, process_id: str, size=10, separator='|'):
    message = f"{message_id}{separator}{process_id}{separator}"
    message += '0' * (size - len(message))
    return message[:size]

def send_request(process_id):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    coordinator_address = (HOST, PORT)

    message = _format_message(REQUEST_ID, process_id)
    client_socket.sendto(message.encode(), coordinator_address)
    print(f"Processo \033[92m{process_id}\033[0m enviou uma requisição ao coordenador.")

    data, address = client_socket.recvfrom(BUFFER_SIZE)
    message = data.decode()
    print(f"Processo \033[92m{process_id}\033[0m recebeu uma mensagem do coordenador: {message}.")

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
        send_request(process_id)
        time.sleep(INTERVAL_TIME)

"""
Ao obter acesso,
o processo abre o arquivo resultado.txt para escrita emmodo append,
obter a hora atual do sistema, escrever o seu identificador e a hora atual (incluindomilisegundos)
no final do arquivo, fechar o arquivo, e depois aguardar k segundos (usando a funçãosleep())
Isto finaliza a região crítica
"""

if __name__ == "__main__":
    main()
    
