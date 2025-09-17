import socket
import threading

broadcast_port = 5678
tcp_port = 1234
clients = []
clients_info = {}

def handle_client(client_socket, address):
    nickname = client_socket.recv(1024).decode('utf-8')
    clients_info[client_socket] = nickname
    print(f"{nickname} has joined the chat!")
    welcome_message = f"{nickname} has joined the chat!"
    udp_broadcast(welcome_message.encode('utf-8'), sender=client_socket)

    while True:
        try:
            msg = client_socket.recv(1024)
            if not msg:
                break
            udp_broadcast(msg, sender=client_socket)
        except:
            break
    client_socket.close()
    clients.remove(client_socket)
    del clients_info[client_socket]
    leave_message = f"{nickname} has left the chat."
    print(f"{nickname} has left the chat.")
    udp_broadcast(leave_message.encode('utf-8'), sender=client_socket)

def udp_broadcast(msg, sender):
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    for client in clients:
        if client != sender:
            udp_socket.sendto(msg, ('<broadcast>', broadcast_port))
            break
    udp_socket.close()

def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('127.0.0.1', tcp_port))
    server.listen(5)
    print(f"Server started on port {tcp_port}")

    while True:
        client_socket, addr = server.accept()
        clients.append(client_socket)
        client_thread = threading.Thread(target=handle_client, args=(client_socket, addr))
        client_thread.start()

if __name__ == "__main__":
    start_server()
