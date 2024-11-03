import socket
import threading
import tkinter as tk
from tkinter import simpledialog
from tkinter import scrolledtext
import db

# Global variables to control the server state and store client connections
server_running = True
server_socket = None
clients = []


def handle_client(client_socket, address, text_area):
    text_area.insert(tk.END, f"Connection from {address}\n")
    text_area.see(tk.END)
    clients.append(client_socket)
    update_user_count(text_area)

    while server_running:
        try:
            message = client_socket.recv(1024).decode('utf-8')
            if not message:
                text_area.insert(tk.END, f"Client {address} disconnected.\n")
                text_area.see(tk.END)
                clients.remove(client_socket)
                update_user_count(text_area)
                break
            
            # Check if the message is a request for the room list
            if message.startswith("FETCH_ROOM_LIST"):
                _, u_id, u_name = message.split("|")
                text_area.insert(tk.END, f"Received room list request from user {u_name} ({u_id}).\n")
                text_area.see(tk.END)
                send_room_list(client_socket)  # Send room list to this client
            else:
                # Extract room, u_name from message
                parts = message.split(":", 2)
                if len(parts) == 3:
                    room = parts[0]
                    u_name = parts[1]
                    t_message = parts[2]
                    text_area.insert(tk.END, f"[ {u_name} ]:{t_message}\n")
                    
                    connection = db.check_database_connection()
                    if db.is_user_present(connection,u_name, db.get_group_id(connection, room)) == True:
                        db.entry_message(connection, u_name, t_message, db.get_group_id(connection, room))
                        # pass
                    else:
                        connection = db.check_database_connection()
                        db.create_user(connection, db.get_group_id(connection, room),u_name)
                        db.entry_message(connection, u_name, t_message, db.get_group_id(connection, room))
                    
                text_area.see(tk.END)
                broadcast(f"{message}")
        except Exception as e:
            text_area.insert(tk.END, f"Error receiving message from {address}: {e}\n")
            text_area.insert(tk.END, f"Client {address} disconnected.\n")
            text_area.see(tk.END)
            clients.remove(client_socket)
            update_user_count(text_area)
            break

    client_socket.close()


def send_room_list(client_socket):
    # Define a sample room list
    connection = db.check_database_connection()
    room_list = db.get_all_groups(connection)
    try:
        client_socket.send(room_list.encode('utf-8'))
    except Exception as e:
        print(f"Error sending room list to client: {e}")

def broadcast(message):
    for client in clients:
        try:
            if len(message) == 3:
                u_parts = message.split(":", 2)
                t_message = f"[{u_parts[1]}:{u_parts[2]}]"
                client.send(t_message.encode('utf-8'))
            else:
                u_parts = message.split(":", 2)
                t_message = f"[{u_parts[1]}]:{u_parts[2]}"
                client.send(t_message.encode('utf-8'))
        except Exception as e:
            print(f"Error sending message to client: {e}")

def update_user_count(text_area):
    online_count = len(clients)
    # text_area.insert(tk.END, f"Online users: {online_count}\n")
    # text_area.see(tk.END)

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
        message =f'Server:Server:{message}'
        broadcast(f"{message}")
        text_area.insert(tk.END, f"{message}\n")
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

def create_chat_room(text_area):
    # Prompt for the new chat room name
    room_name = simpledialog.askstring("New Chat Room", "Enter the name of the new chat room:")
    
    if room_name:
        # Here you would include the logic to create the chat room in your application
        # For example, adding the room to your database or server management
        connection = db.check_database_connection()
        if db.create_group(connection,room_name,0):
            text_area.insert(tk.END, f"Chat room '{room_name}' created successfully.\n")
            text_area.see(tk.END)
        else:
            text_area.insert(tk.END, f"Chat room '{room_name}' Not created!!!.\n")
            text_area.see(tk.END)


def create_gui():
    window = tk.Tk()
    window.title("Server")
    window.geometry("850x500")

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

    # Button to create a new chat room
    create_room_button = tk.Button(window, text="Create Chat Room", command=lambda: create_chat_room(text_area))
    create_room_button.pack(side=tk.LEFT, padx=10, pady=10)
    

    window.mainloop()

if __name__ == "__main__":
    create_gui()
