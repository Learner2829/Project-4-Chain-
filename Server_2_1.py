import socket
import threading
import tkinter as tk
from tkinter import simpledialog
from tkinter import scrolledtext
import db
from datetime import datetime
import time
from datetime import datetime, timedelta 

# Global variables to control the server state and store client connections
server_running = True
server_socket = None
clients = []
client_groups = {}  # Dictionary to track clients by group {group_name: [client_socket, ...]}

def start_stopwatch(text_area):
    """
    Starts a stopwatch that updates the text_area every second.
    This function runs until the server is stopped.
    """
    start_time = time.time()  # Get the start time

    def update_stopwatch():
        while server_running:
            try:
                elapsed_time = time.time() - start_time  # Time elapsed since start
                minutes, seconds = divmod(elapsed_time, 60)  # Divide by 60 to get minutes and seconds
                hours, minutes = divmod(minutes, 60)  # Divide by 60 again to get hours

                # Format time as hh:mm:ss
                formatted_time = f"{int(hours):02}:{int(minutes):02}:{int(seconds):02}"

                # Update the text_area with the formatted time
                text_area.delete(1.0, tk.END)  # Clear previous time
                text_area.insert(tk.END, f"Stopwatch: {formatted_time}\n")  # Insert new time
                text_area.see(tk.END)  # Scroll to the latest entry
            except Exception as e:
                print(f"Error updating stopwatch: {e}")
            time.sleep(1)  # Update every second

    # Start the stopwatch in a separate thread to avoid blocking the main GUI
    stopwatch_thread = threading.Thread(target=update_stopwatch)
    stopwatch_thread.daemon = True
    stopwatch_thread.start()

def schedule_message_cleanup():
    """
    Automatically deletes messages older than 10 minutes from the database.
    This function runs in a loop and executes every 10 minutes.
    """
    while server_running:
        try:
            current_time = datetime.now()
            threshold_time = current_time - timedelta(minutes=10)
            connection = db.check_database_connection()
            
            # Call the cleanup function in db.py with the threshold time
            db.delete_old_messages(connection, threshold_time)
            print(f"Cleaned up messages older than {threshold_time}")
        except Exception as e:
            print(f"Error in message cleanup: {e}")
        
        # Sleep for 10 minutes before running the cleanup again
        time.sleep(600)  # 600 seconds = 10 minutes

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
                
                # Remove the client from all groups they may be part of
                for group, group_clients in client_groups.items():
                    if client_socket in group_clients:
                        group_clients.remove(client_socket)
                update_user_count(text_area)
                break
            
            if message.startswith("FETCH_ROOM_LIST"):
                _, u_id, u_name = message.split("|")
                text_area.insert(tk.END, f"Received room list request from user {u_name} ({u_id}).\n")
                text_area.see(tk.END)
                send_room_list(client_socket)
                  # Send room list to this client
            else:
                # Extract room, user details, and optionally timestamp from the message
                parts = message.split(":", 3)
                
                if len(parts) == 3:
                    # Handle the case where the timestamp is not provided
                    room, u_name, t_message = parts
                    timestamp = None  # No timestamp provided
                elif len(parts) == 4:
                    # Handle the case where the timestamp is provided
                    room, u_name, t_message, timestamp = parts
                else:
                    # Invalid message format
                    text_area.insert(tk.END, f"Invalid message format from {address}: {message}\n")
                    text_area.see(tk.END)
                    continue

                # Log the message
                if timestamp:
                    text_area.insert(tk.END, f"[ {u_name} ]  [{timestamp}] : {t_message}\n")
                else:
                    text_area.insert(tk.END, f"[ {u_name} ]: {t_message}\n")

                # Ensure the room exists in client_groups
                if room not in client_groups:
                    client_groups[room] = []
                
                # Add the client to the group if not already added
                if client_socket not in client_groups[room]:
                    client_groups[room].append(client_socket)
                
                # Save the message to the database if user is present
                connection = db.check_database_connection()
                if db.is_user_present(connection, u_name, db.get_group_id(connection, room)):
                    db.entry_message(connection, u_name, t_message, db.get_group_id(connection, room), timestamp)
                else:
                    db.create_user(connection, db.get_group_id(connection, room), u_name)
                    db.entry_message(connection, u_name, t_message, db.get_group_id(connection, room), timestamp)

                # Broadcast message to the specified group
                broadcast(f"{room}:{u_name}:{t_message}:{timestamp}" if timestamp else f"{room}:{u_name}:{t_message}", room)
                
                text_area.see(tk.END)

        except Exception as e:
            text_area.insert(tk.END, f"Client {address} disconnected.\n")
            text_area.see(tk.END)
            clients.remove(client_socket)
            # Remove the client from all groups they may be part of
            for group, group_clients in client_groups.items():
                if client_socket in group_clients:
                    group_clients.remove(client_socket)
                    
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

def broadcast(message, room=None):
    # Broadcast message only to clients in the specified room
    if room and room in client_groups:
        for client in client_groups[room]:
            try:
                # Safely split message into parts and ensure there are enough parts
                parts_b = message.split(":", 3)  # Allow splitting into 4 parts for the timestamp
                if len(parts_b) < 3:
                    print("Invalid message format. Expected format: room:username:message[:timestamp]")
                    continue

                # Extract message components
                sender = parts_b[1]
                content = parts_b[2]
                timestamp = parts_b[3] if len(parts_b) == 4 else None  # Check if timestamp is provided

                # Format the message for broadcasting
                if timestamp:
                    formatted_message = f"[{sender}] [{timestamp}]: {content}"
                else:
                    formatted_message = f"[{sender}]: {content}"

                # Send the formatted message to the client
                client.send(formatted_message.encode('utf-8'))
            except Exception as e:
                print(f"Error sending message to client in {room}: {e}")
# Global broadcast to all clients in all groups if room is "Server"
    if room == "Server":
        for group, group_clients in client_groups.items():
            for client in group_clients:
                try:
                    # Format the message to indicate it is from the server
                    parts_b = message.split(":", 2)  # Allow splitting into 4 parts for the timestamp
                    if len(parts_b) < 2:
                        print("Invalid message format. Expected format: room:username:message[:timestamp]")
                        continue

                    sender = parts_b[0]
                    content = parts_b[1]
                    timestamp = parts_b[2]   # Check if timestamp is provided

                    # Format the message for broadcasting
                    if timestamp:
                        formatted_message = f"[Server] [{timestamp}]: {content}"
                    else:
                        formatted_message = f"[Server]: {content}"

                    # Send the formatted message to the client
                    client.send(formatted_message.encode('utf-8'))
                except Exception as e:
                    print(f"Error sending message to client in group {group}: {e}")
        return  # Exit after global broadcasting
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

    # Start the cleanup scheduler thread
    cleanup_thread = threading.Thread(target=schedule_message_cleanup)
    cleanup_thread.daemon = True
    cleanup_thread.start()

def stop_server(text_area):
    global server_running, server_socket
    server_running = False
    if server_socket:
        server_socket.close()
    text_area.insert(tk.END, "Stopping server...\n")
    text_area.see(tk.END)

def send_message_to_clients(message, text_area, message_entry):
    if message:
        current_datetime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        message =f'Server:{message}:{current_datetime}'
        broadcast(f"{message}","Server")
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
    window.title("4-Chain Server Room")
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

    # Start the timer to update every 10 minutes
    # start_stopwatch(text_area)

    # Button to create a new chat room
    create_room_button = tk.Button(window, text="Create Chat Room", command=lambda: create_chat_room(text_area))
    create_room_button.pack(side=tk.LEFT, padx=10, pady=10)
    

    window.mainloop()

if __name__ == "__main__":
    create_gui()
