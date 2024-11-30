from torpy import TorClient
import socket

def send_message(message):
    with TorClient() as tor_client:
        with tor_client as session:
            try:
                # Torpy provides a SOCKS5 proxy (127.0.0.1:9050) for Tor network access.
                proxy_host = '147.185.221.24'
                proxy_port = 11199  # Tor's default SOCKS5 proxy port
                
                # Set up a socket to connect to the server via the Tor proxy
                client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                client_socket.connect((proxy_host, proxy_port))  # Connect to Tor's SOCKS5 proxy
                
                # Connect to the server through the Tor network (localhost:5000)
                client_socket.sendall(message.encode())  # Send message
                response = client_socket.recv(1024).decode()  # Get response from the server
                print(f"Response from server: {response}")

                client_socket.close()
            except Exception as e:
                print(f"Failed to connect: {e}")

send_message("hi")
