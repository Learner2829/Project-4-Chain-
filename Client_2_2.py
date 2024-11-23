import socket
import threading
import tkinter as tk
from tkinter import scrolledtext, simpledialog, messagebox
import uuid  
from datetime import datetime
import socks  # For using SOCKS5 proxy with Tor

def receive_messages(client_socket, text_area):
    while True:
        try:
            message = client_socket.recv(1024).decode('utf-8')
            if not message:
                break
            text_area.insert(tk.END, f"{message}\n")
            text_area.see(tk.END)
        except Exception as e:
            text_area.insert(tk.END, f"Server is Disconnected...\n")
            text_area.see(tk.END)
            break

def validate_message(message):
    forbidden_words = [":"]
    for word in forbidden_words:
        message = message.replace(word, "*")
    return message

def send_message(client_socket, message_entry, text_area, username, room_name):
    message = message_entry.get()
    if message:
        # Validate the message before sending
        message = validate_message(message)
        try:
            current_datetime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            full_message = f"{room_name}:{username}:{message}:{current_datetime}"
            client_socket.send(full_message.encode('utf-8'))
        except Exception as e:
            text_area.insert(tk.END, f"Server is Disconnected...\n")
            text_area.see(tk.END)
        message_entry.delete(0, tk.END)

def create_socks_proxy_socket():
    # Create a socket that connects via Tor's SOCKS5 proxy
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setproxy(socks.SOCKS5, "127.0.0.1", 9050)  # Tor's default SOCKS5 proxy
    return s

def connect_to_server(server_ip, server_port, text_area, username, room_name):
    # Use the SOCKS proxy to connect via Tor
    client_socket = create_socks_proxy_socket()  # Tor connection via SOCKS5
    try:
        message = "I Am Live"
        client_socket.connect((server_ip, server_port))  # Connect through Tor
        full_message = f"{room_name}:{username}:{message}"
        client_socket.send(full_message.encode('utf-8'))  # Send selected room name to the server
        text_area.insert(tk.END, f"Connected to the server as {username} in room '{room_name}'.\n")
        text_area.see(tk.END)
        
        receive_thread = threading.Thread(target=receive_messages, args=(client_socket, text_area))
        receive_thread.daemon = True
        receive_thread.start()
    except Exception as e:
        messagebox.showerror("Connection Error.....")
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

def fetch_room_list(server_ip, server_port, u_id, u_name, window):
    room_list = []
    try:
        # Create a temporary socket to fetch room list
        temp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        temp_socket.connect((server_ip, server_port))
        
        # Send user information and request for room list
        request_message = f"FETCH_ROOM_LIST|{u_id}|{u_name}"
        temp_socket.send(request_message.encode('utf-8'))
        
        # Receive the room list from the server
        room_data = temp_socket.recv(1024).decode('utf-8')
        room_list = room_data.split('|')  # Assuming server sends rooms separated by '|'
        temp_socket.close()
    except Exception as e:
        messagebox.showerror("Error", "The server is offline or not reachable.")
        window.destroy()  # Exit the application
        return room_list  # Return empty list
    
    return room_list

def choose_room_gui(window, server_ip, server_port, u_id, u_name, callback):
    room_window = tk.Toplevel(window)
    room_window.title("Choose Room")
    room_window.geometry("300x300")
    
    room_list = fetch_room_list(server_ip, server_port, u_id, u_name, window)

    if not room_list:
        return

    tk.Label(room_window, text="Choose a Room:", font=("Arial", 14)).pack(pady=10)

    for room in room_list:
        room_button = tk.Button(room_window, text=room, font=("Arial", 12),
                                command=lambda r=room: [callback(r), room_window.destroy()])
        room_button.pack(pady=5, fill='x', padx=20)

def create_client_gui():
    window = tk.Tk()
    window.title("4-Chain")
    window.geometry("600x600")

    current_theme = ['light']

    # Generate random user ID and get username
    u_id = str(uuid.uuid4())  # Automatically allocate a random user ID
    username = simpledialog.askstring("Username", "Enter your username:", parent=window)
    if not username:
        window.destroy()
        return
    
    # Room selection callback to start chat after choosing a room
    def start_chat_in_room(room_name):
        text_area = scrolledtext.ScrolledText(window, wrap=tk.WORD)
        text_area.pack(expand=True, fill='both')

        # Display username and room name at the top
        username_label = tk.Label(window, text=f"Connected as: {username} | Room: {room_name}", font=("Arial", 12))
        username_label.pack(pady=5)

        message_entry = tk.Entry(window)
        message_entry.pack(fill='x', padx=10, pady=5)

        server_ip = "147.185.221.24"
        server_port = 3535
        client_socket = connect_to_server(server_ip, server_port, text_area, username, room_name)

        send_button = tk.Button(window, text="Send", command=lambda: send_message(client_socket, message_entry, text_area, username, room_name))
        send_button.pack(pady=5)

        theme_button = tk.Button(window, text="Toggle Theme", command=lambda: toggle_theme(window, text_area, message_entry, current_theme))
        theme_button.pack(pady=5)

        window.protocol("WM_DELETE_WINDOW", lambda: on_closing(client_socket, window))

    # Open room selection window
    server_ip = "147.185.221.24"
    server_port = 3535
    choose_room_gui(window, server_ip, server_port, u_id, username, start_chat_in_room)

    window.mainloop()

if __name__ == "__main__":
    create_client_gui()
