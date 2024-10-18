import mysql.connector
from mysql.connector import Error

def check_database_connection():
    try:
        # Establish the connection
        connection = mysql.connector.connect(
            host="localhost",
            user="root",      # Your MySQL username
            password="",      # Your MySQL password
            database="4-chain" # Your database name
        )
        
        # Check if the connection was successful
        if connection.is_connected():
            print("Connected to the database.")
            return connection

    except Error as e:
        print(f"Error: {e}")
        return False

def create_user(connection,u_id, g_id, u_name):
    try:
        cursor = connection.cursor()

        # SQL query to insert a new user
        insert_query = """
        INSERT INTO user_data (u_id, g_id, u_name)
        VALUES (%s, %s, %s)
        """
        
        # Execute the query with the provided arguments
        cursor.execute(insert_query, (u_id, g_id, u_name))

        # Commit the transaction
        connection.commit()

        print(f"User {u_name} created successfully.")

    except Error as e:
        print(f"Error: {e}")

def create_group(connection, g_id, g_name, ex_token):
    try:
        # Create a cursor object
        cursor = connection.cursor()

        # SQL query to insert a new group
        insert_query = """
        INSERT INTO group_data (g_id, g_name, ex_token)
        VALUES (%s, %s, %s)
        """
        
        # Execute the query with the provided arguments
        cursor.execute(insert_query, (g_id, g_name, ex_token))
        
        # Commit the transaction
        connection.commit()
        print(f"Group {g_name} created successfully.")

        # Create a new table for storing messages
        message_table_name = f"{g_name}_message"
        create_table_query = f"""
        CREATE TABLE IF NOT EXISTS `{message_table_name}` (
            m_id INT AUTO_INCREMENT PRIMARY KEY,
            u_id INT,
            message TEXT,
            g_id INT,
            FOREIGN KEY (g_id) REFERENCES group_data(g_id)
        )
        """
        
        # Execute the create table query
        cursor.execute(create_table_query)
        connection.commit()
        print(f"Message table {message_table_name} created successfully.")

    except Error as e:
        print(f"Error: {e}")


def delete_group(connection, g_id, g_name):
    try:
        # Create a cursor object
        cursor = connection.cursor()

        # SQL query to delete messages associated with the group
        message_table_name = f"{g_name}_message"
        delete_messages_query = f"""
        DELETE FROM `{message_table_name}` WHERE g_id = %s
        """
        
        # Execute the delete messages query
        cursor.execute(delete_messages_query, (g_id,))
        connection.commit()
        print(f"Messages for group {g_name} deleted successfully.")

        # SQL query to delete the group
        delete_group_query = """
        DELETE FROM group_data WHERE g_id = %s
        """
        
        # Execute the delete query
        cursor.execute(delete_group_query, (g_id,))
        connection.commit()
        print(f"Group with ID {g_id} deleted successfully.")

        # Drop the corresponding message table
        drop_table_query = f"DROP TABLE IF EXISTS `{message_table_name}`"
        
        # Execute the drop table query
        cursor.execute(drop_table_query)
        connection.commit()
        print(f"Message table {message_table_name} deleted successfully.")

    except Error as e:
        print(f"Error: {e}")


def entry_message(connection, u_id, message, g_id):
    try:
        cursor = connection.cursor()

        # Retrieve the group name based on g_id to determine the message table
        cursor.execute("SELECT g_name FROM group_data WHERE g_id = %s", (g_id,))
        group = cursor.fetchone()

        if group is None:
            print(f"No group found with ID {g_id}.")
            return
        
        g_name = group[0]
        message_table_name = f"{g_name}_message"

        # SQL query to insert a new message
        insert_query = f"""
        INSERT INTO `{message_table_name}` (u_id, message, g_id)
        VALUES (%s, %s, %s)
        """

        # Execute the query with the provided arguments
        cursor.execute(insert_query, (u_id, message, g_id))

        # Commit the transaction
        connection.commit()
        print(f"Message from user {u_id} added successfully to group {g_name}.")

    except Error as e:
        print(f"Error: {e}")

# Example usage of entry_message
    

    


# connection = check_database_connection()
# create_user(connection,2, 102, 'Doe')
# create_group(connection,103,'KS',0)
# delete_group(connection,103,'KS')
# entry_message(connection, 2, "Hello, this is a test message!", 103)

