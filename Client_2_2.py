import socket
import threading
import tkinter as tk
from tkinter import scrolledtext, simpledialog, messagebox
import uuid  
from datetime import datetime
from torpy import TorClient

def choose_room_gui(window, server_ip, server_port, u_id, u_name, callback):
    room_window = tk.Toplevel(window)
    room_window.title("Choose Room")
    room_window.geometry("300x300")
    
    room_list = fetch_room_list(server_ip, server_port, u_id, u_name, window)  # Fetch the room list from server

    if not room_list:
        # This case is already handled in fetch_room_list
        return

    tk.Label(room_window, text="Choose a Room:", font=("Arial", 14)).pack(pady=10)

    for room in room_list:
        room_button = tk.Button(room_window, text=room, font=("Arial", 12),
                                command=lambda r=room: [callback(r), room_window.destroy()])
        room_button.pack(pady=5, fill='x', padx=20)

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
    """
    Validates the user message by replacing forbidden words with "***". 
    Forbidden words: ":"
    
    Args:
        message (str): The user input message.
    
    Returns:
        str: The sanitized message.
    """
    # Replace forbidden words with "***"
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
            # Get the current timestamp in the desired format
            current_datetime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            # Combine room_name, username, message, and current datetime
            full_message = f"{room_name}:{username}:{message}:{current_datetime}"

            # Use Torpy for sending the message
            with TorClient() as tor_client:
                with tor_client.create_session() as session:
                    # Connect to the server through Tor network using SOCKS5 proxy (127.0.0.1:9050)
                    proxy_host = '127.0.0.1'
                    proxy_port = 9050  # Tor's SOCKS5 proxy port

                    # Create a socket to communicate with the server
                    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

                    # Connect to the Tor proxy
                    client_socket.connect((proxy_host, proxy_port))  # Connect to Tor's SOCKS5 proxy
                    client_socket.send(full_message.encode('utf-8'))  # Send the message to the server

                    # Receive the response from the server
                    response = client_socket.recv(1024).decode('utf-8')
                    print(f"Response from server: {response}")
                    text_area.insert(tk.END, f"Server response: {response}\n")
                    text_area.see(tk.END)

                    # Close the socket after sending the message
                    client_socket.close()

        except Exception as e:
            text_area.insert(tk.END, f"Server is Disconnected...\n")
            text_area.see(tk.END)

        # Clear the message entry field
        message_entry.delete(0, tk.END)

def connect_to_server(server_ip, server_port, text_area, username, room_name):
    try:
        message = "I Am Live"
        
        # Use Torpy to connect via the Tor network
        with TorClient() as tor_client:
            with tor_client.create_session() as session:
                # Create a socket to connect to the server via the Tor network (SOCKS5 proxy at 127.0.0.1:9050)
                client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                client_socket.connect((server_ip, server_port))  # Connect to the server via Tor

                # Send the room and username to the server
                full_message = f"{room_name}:{username}:{message}"
                client_socket.send(full_message.encode('utf-8'))  # Send room name and username to server

                text_area.insert(tk.END, f"Connected to the server as {username} in room '{room_name}'.\n")
                text_area.see(tk.END)

                # Start a thread to listen for incoming messages
                receive_thread = threading.Thread(target=receive_messages, args=(client_socket, text_area))
                receive_thread.daemon = True
                receive_thread.start()

                return client_socket

    except Exception as e:
        messagebox.showerror("Connection Error", "Could not connect to the server via Tor.")
        return None

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
    window.title("4-Chain")
    window.geometry("600x600")

    current_theme = ['light']

    # Define server details
    server_ip = "147.185.221.24"  # Example server IP
    server_port = 11199  # Example server port

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

        client_socket = connect_to_server(server_ip, server_port, text_area, username, room_name)

        send_button = tk.Button(window, text="Send", command=lambda: send_message(client_socket, message_entry, text_area, username, room_name))
        send_button.pack(pady=5)

        theme_button = tk.Button(window, text="Toggle Theme", command=lambda: toggle_theme(window, text_area, message_entry, current_theme))
        theme_button.pack(pady=5)

        window.protocol("WM_DELETE_WINDOW", lambda: on_closing(client_socket, window))

    # Open room selection window
    choose_room_gui(window, server_ip, server_port, u_id, username, start_chat_in_room)

    window.mainloop()

if __name__ == "__main__":
    create_client_gui()
