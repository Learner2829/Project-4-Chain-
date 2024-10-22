import socket
import threading
import tkinter as tk
from tkinter import scrolledtext, simpledialog, messagebox

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

def send_message(client_socket, message_entry, text_area, username):
    message = message_entry.get()
    if message:
        try:
            full_message = f"{username}: {message}"
            client_socket.send(full_message.encode('utf-8'))
        except Exception as e:
            text_area.insert(tk.END, f"Error sending message: {e}\n")
            text_area.see(tk.END)
        message_entry.delete(0, tk.END)

def connect_to_server(server_ip, server_port, text_area, username):
    client_socket = socket.socket()
    try:
        client_socket.connect((server_ip, server_port))
        text_area.insert(tk.END, f"Connected to the server as {username}.\n")
        text_area.see(tk.END)
        
        receive_thread = threading.Thread(target=receive_messages, args=(client_socket, text_area))
        receive_thread.daemon = True
        receive_thread.start()
    except Exception as e:
        messagebox.showerror("Connection Error", str(e))
        client_socket.close()
        return None
    
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

def on_closing(client_socket, window):
    if client_socket:
        client_socket.close()
    window.destroy()

def create_client_gui():
    window = tk.Tk()
    window.title("Client")
    window.geometry("600x600")

    current_theme = ['light']

    username = simpledialog.askstring("Username", "Enter your username:", parent=window)
    if not username:
        window.destroy()
        return

    text_area = scrolledtext.ScrolledText(window, wrap=tk.WORD)
    text_area.pack(expand=True, fill='both')

    # Display username at the top
    username_label = tk.Label(window, text=f"Connected as: {username}", font=("Arial", 12))
    username_label.pack(pady=5)

    message_entry = tk.Entry(window)
    message_entry.pack(fill='x', padx=10, pady=5)

    server_ip = '127.0.0.1'
    server_port = 9999
    client_socket = connect_to_server(server_ip, server_port, text_area, username)

    send_button = tk.Button(window, text="Send", command=lambda: send_message(client_socket, message_entry, text_area, username))
    send_button.pack(pady=5)

    theme_button = tk.Button(window, text="Toggle Theme", command=lambda: toggle_theme(window, text_area, message_entry, current_theme))
    theme_button.pack(pady=5)

    window.protocol("WM_DELETE_WINDOW", lambda: on_closing(client_socket, window))
    window.mainloop()

if __name__ == "__main__":
    create_client_gui()
