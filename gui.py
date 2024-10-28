import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QListWidget, QTextEdit, QMessageBox
)

# Username Window
class UsernameWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Enter Username")
        self.setGeometry(400, 300, 300, 150)

        # Layout and widgets
        layout = QVBoxLayout()
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Enter your username")
        layout.addWidget(QLabel("Username:"))
        layout.addWidget(self.username_input)

        # Next button
        self.next_button = QPushButton("Next")
        self.next_button.clicked.connect(self.go_to_chatrooms)
        layout.addWidget(self.next_button)

        # Central widget
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def go_to_chatrooms(self):
        username = self.username_input.text().strip()
        if username:
            self.chatroom_window = ChatroomWindow(username)
            self.chatroom_window.show()
            self.close()
        else:
            QMessageBox.warning(self, "Input Error", "Please enter a valid username.")

# Chatroom Selection Window
class ChatroomWindow(QMainWindow):
    def __init__(self, username):
        super().__init__()
        self.setWindowTitle("Select Chatroom")
        self.setGeometry(400, 300, 300, 400)
        self.username = username

        # Layout and widgets
        layout = QVBoxLayout()
        layout.addWidget(QLabel(f"Welcome, {self.username}! Choose a chatroom:"))

        # Chatroom list (sample rooms for now)
        self.chatroom_list = QListWidget()
        self.chatroom_list.addItems(["General", "Technology", "Gaming", "Music", "Movies","General", "Technology", "Gaming", "Music", "Movies"
                                     "General", "Technology", "Gaming", "Music", "Movies"
                                     "General", "Technology", "Gaming", "Music", "Movies"
                                     "General", "Technology", "Gaming", "Music", "Movies"])
        layout.addWidget(self.chatroom_list)

        # Enter room button
        self.enter_button = QPushButton("Enter Chatroom")
        self.enter_button.clicked.connect(self.enter_chatroom)
        layout.addWidget(self.enter_button)

        # Central widget
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def enter_chatroom(self):
        selected_room = self.chatroom_list.currentItem()
        if selected_room:
            room_name = selected_room.text()
            self.chat_window = ChatWindow(self.username, room_name)
            self.chat_window.show()
            self.close()
        else:
            QMessageBox.warning(self, "Selection Error", "Please select a chatroom.")

# Main Chat Window
class ChatWindow(QMainWindow):
    def __init__(self, username, room_name):
        super().__init__()
        self.setWindowTitle(f"Chat Room - {room_name}")
        self.setGeometry(400, 300, 400, 500)
        self.username = username
        self.room_name = room_name

        # Layout
        main_layout = QVBoxLayout()

        # Chat display area
        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        main_layout.addWidget(self.chat_display)

        # Input layout
        input_layout = QHBoxLayout()
        self.message_input = QLineEdit()
        self.message_input.setPlaceholderText("Type your message here...")
        input_layout.addWidget(self.message_input)

        # Send button
        self.send_button = QPushButton("Send")
        self.send_button.clicked.connect(self.send_message)
        input_layout.addWidget(self.send_button)

        main_layout.addLayout(input_layout)

        # Central widget
        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

    def send_message(self):
        message = self.message_input.text().strip()
        if message:
            self.chat_display.append(f"{self.username}: {message}")
            self.message_input.clear()
            # Add functionality to broadcast message to the room here

# Main application runner
if __name__ == "__main__":
    app = QApplication(sys.argv)
    username_window = UsernameWindow()
    username_window.show()
    sys.exit(app.exec_())
