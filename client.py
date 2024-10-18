import socket
import threading
import tkinter as tk
from tkinter import scrolledtext

def receive_messages(client_socket, text_area):
    while True:
        try:
            message = client_socket.recv(1024).decode('utf-8')
            if not message:
                break
            text_area.insert(tk.END, f"Server: {message}\n")
            text_area.see(tk.END)
        except Exception as e:
            text_area.insert(tk.END, f"Error: {e}\n")
            text_area.see(tk.END)
            break

def send_message(client_socket, message_entry, text_area):
    message = message_entry.get()
    if message:
        client_socket.send(message.encode('utf-8'))
        # text_area.insert(tk.END, f"You: {message}\n")
        # text_area.see(tk.END)
        message_entry.delete(0, tk.END)

def connect_to_server(server_ip, server_port, text_area):
    client_socket = socket.socket()
    client_socket.connect((server_ip, server_port))
    text_area.insert(tk.END, "Connected to the server.\n")
    text_area.see(tk.END)
    
    receive_thread = threading.Thread(target=receive_messages, args=(client_socket, text_area))
    receive_thread.daemon = True
    receive_thread.start()
    
    return client_socket

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

def create_client_gui():
    window = tk.Tk()
    window.title("Client")
    window.geometry("600x500")

    current_theme = ['light']

    text_area = scrolledtext.ScrolledText(window, wrap=tk.WORD)
    text_area.pack(expand=True, fill='both')

    message_entry = tk.Entry(window)
    message_entry.pack(fill='x', padx=10, pady=5)

    host_name = socket.gethostname()
    #server_ip = socket.gethostbyname(host_name)
    server_ip = '127.0.0.1'
    server_port = 9999
    client_socket = connect_to_server(server_ip, server_port, text_area)

    send_button = tk.Button(window, text="Send", command=lambda: send_message(client_socket, message_entry, text_area))
    send_button.pack(pady=5)

    theme_button = tk.Button(window, text="Toggle Theme", command=lambda: toggle_theme(window, text_area, message_entry, current_theme))
    theme_button.pack(pady=5)

    window.mainloop()

if __name__ == "__main__":
    create_client_gui()
