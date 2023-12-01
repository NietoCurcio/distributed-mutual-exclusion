import socket
import os

REQUEST_ID = '1'
HOST = 'localhost'
PORT = 9999

def _format_message(message_id: str, process_id: str, size=10, separator='|'):
    message = f"{message_id}{separator}{process_id}{separator}"
    message += '0' * (size - len(message))
    return message[:size]

def send_request(process_id):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    coordinator_address = (HOST, PORT)

    message = _format_message(REQUEST_ID, process_id)
    client_socket.sendto(message.encode(), coordinator_address)
    print(f"Processo {process_id} enviou uma requisição ao coordenador.")

def _get_PID():
    pid = os.getpid()
    message_length = 10
    message_id_length = 1
    pid_length_threshold = message_length - message_id_length
    return str(pid)[-pid_length_threshold:]


if __name__ == "__main__":
    process_id = _get_PID()
    send_request(process_id)
