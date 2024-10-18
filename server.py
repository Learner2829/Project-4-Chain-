import socket
import threading
import tkinter as tk
from tkinter import scrolledtext

# Global variables to control the server state and store client connections
server_running = True
server_socket = None
clients = []

def handle_client(client_socket, address, text_area):
    text_area.insert(tk.END, f"Connection from {address}\n")
    text_area.see(tk.END)
    clients.append(client_socket)
    broadcast(f"User {address} joined the chat.")
    update_user_count(text_area)

    while server_running:
        try:
            message = client_socket.recv(1024).decode('utf-8')
            if not message:
                text_area.insert(tk.END, f"Client {address} disconnected.\n")
                text_area.see(tk.END)
                clients.remove(client_socket)
                broadcast(f"User {address} left the chat.")
                update_user_count(text_area)
                break
            text_area.insert(tk.END, f"Message from {address}: {message}\n")
            text_area.see(tk.END)
            broadcast(f"Message from {address}: {message}")
        except Exception as e:
            text_area.insert(tk.END, f"Error receiving message from {address}: {e}\n")
            text_area.insert(tk.END, f"Client {address} disconnected.\n")
            text_area.see(tk.END)
            clients.remove(client_socket)
            broadcast(f"User {address} left the chat.")
            update_user_count(text_area)
            break

    client_socket.close()

def broadcast(message):
    for client in clients:
        try:
            client.send(message.encode('utf-8'))
        except Exception as e:
            print(f"Error sending message to client: {e}")

def update_user_count(text_area):
    online_count = len(clients)
    text_area.insert(tk.END, f"Online users: {online_count}\n")
    text_area.see(tk.END)

def start_server(text_area):
    global server_socket
    server_socket = socket.socket()
    
    ip_address = '127.0.0.1'
    server_socket.bind((ip_address, 9999))
    server_socket.listen(5)
    text_area.insert(tk.END, "Server is listening...\n")
    text_area.see(tk.END)

    while server_running:
        try:
            client_socket, address = server_socket.accept()
            client_handler = threading.Thread(target=handle_client, args=(client_socket, address, text_area))
            client_handler.start()
        except Exception as e:
            if server_running:
                text_area.insert(tk.END, f"Error accepting connection: {e}\n")
                text_area.see(tk.END)

    text_area.insert(tk.END, "Server stopped.\n")
    text_area.see(tk.END)
    server_socket.close()

def start_server_thread(text_area):
    global server_running
    server_running = True
    server_thread = threading.Thread(target=start_server, args=(text_area,))
    server_thread.daemon = True
    server_thread.start()

def stop_server(text_area):
    global server_running, server_socket
    server_running = False
    if server_socket:
        server_socket.close()
    text_area.insert(tk.END, "Stopping server...\n")
    text_area.see(tk.END)

def send_message_to_clients(message, text_area, message_entry):
    if message:
        broadcast(f"Server: {message}")
        text_area.insert(tk.END, f"Server: {message}\n")
        text_area.see(tk.END)
        message_entry.delete(0, tk.END)

def toggle_theme(window, text_area, message_entry, current_theme):
    if current_theme[0] == 'light':
        window.config(bg='black')
        text_area.config(bg='black', fg='white', insertbackground='white')
        message_entry.config(bg='black', fg='white', insertbackground='white')
        current_theme[0] = 'dark'
    else:
        window.config(bg='white')
        text_area.config(bg='white', fg='black', insertbackground='black')
        message_entry.config(bg='white', fg='black', insertbackground='black')
        current_theme[0] = 'light'

def create_gui():
    window = tk.Tk()
    window.title("Server")
    window.geometry("700x500")

    current_theme = ['light']

    text_area = scrolledtext.ScrolledText(window, wrap=tk.WORD)
    text_area.pack(expand=True, fill='both', padx=10, pady=10)

    message_entry = tk.Entry(window, width=50)
    message_entry.pack(side=tk.LEFT, padx=10, pady=10)

    send_button = tk.Button(window, text="Send Message", command=lambda: send_message_to_clients(message_entry.get(), text_area, message_entry))
    send_button.pack(side=tk.LEFT, padx=10, pady=10)

    start_button = tk.Button(window, text="Start Server", command=lambda: start_server_thread(text_area))
    start_button.pack(side=tk.LEFT, padx=10, pady=10)

    stop_button = tk.Button(window, text="Stop Server", command=lambda: stop_server(text_area))
    stop_button.pack(side=tk.RIGHT, padx=10, pady=10)

    theme_button = tk.Button(window, text="Toggle Theme", command=lambda: toggle_theme(window, text_area, message_entry, current_theme))
    theme_button.pack(side=tk.RIGHT, padx=10, pady=10)

    window.mainloop()

if __name__ == "__main__":
    create_gui()
