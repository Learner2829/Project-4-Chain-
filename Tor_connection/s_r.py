import socket

def start_server():
    host = '127.0.0.1'  # Localhost
    port = 9999     # Port for the server

    # Create a TCP/IP socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(5)
    print(f"Server listening on {host}:{port}")

    while True:
        # Wait for a connection
        client_socket, addr = server_socket.accept()
        print(f"Connection from {addr}")
        handle_client(client_socket)

def handle_client(client_socket):
    try:
        data = client_socket.recv(1024).decode()  # Receive data from client
        print(f"Received: {data}")
        client_socket.sendall("Message received!".encode())  # Send response back
    except Exception as e:
        print(f"Error: {e}")
    finally:
        client_socket.close()

start_server()
