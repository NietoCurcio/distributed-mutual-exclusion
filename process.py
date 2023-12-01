import socket

def format_message(message_id, process_id, size, separator='|'):
    message = f"{message_id}{separator}{process_id}{separator}"
    message += '0' * (size - len(message))
    return message[:size]

def send_request(process_id):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    coordinator_address = ('localhost', 9999)

    message = format_message('1', process_id, 10)
    client_socket.sendto(message.encode(), coordinator_address)
    print(f"Processo {process_id} enviou uma requisição ao coordenador.")

if __name__ == "__main__":
    process_id = '5'
    send_request(process_id)
