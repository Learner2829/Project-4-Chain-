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
        print(f"Database_Error: {e}")
        return False

def create_user(connection,g_id, u_name):
    try:
        cursor = connection.cursor()

        # SQL query to insert a new user
        insert_query = """
        INSERT INTO user_data (g_id, u_name)
        VALUES (%s, %s)
        """
        
        # Execute the query with the provided arguments
        cursor.execute(insert_query, (g_id, u_name))

        # Commit the transaction
        connection.commit()

        # print(f"User {u_name} created successfully.")

    except Error as e:
        print(f"Create_User_Error: {e}")

def create_group(connection, g_name, ex_token):
    try:
        # Create a cursor object
        cursor = connection.cursor()

        # SQL query to insert a new group
        insert_query = """
        INSERT INTO group_data (g_name, ex_token)
        VALUES (%s, %s)
        """
        
        # Execute the query with the provided arguments
        cursor.execute(insert_query, (g_name, ex_token))
        
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
        return 1

    except Error as e:
        print(f"Create_group_Error: {e}")
        return 0

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
        print(f"Delete_group_Error: {e}")


def entry_message(connection, u_name, message, g_id):
    try:
        cursor = connection.cursor()

        # Retrieve u_id based on u_name and g_id
        cursor.execute("SELECT u_id FROM user_data WHERE u_name = %s AND g_id = %s", (u_name, g_id))
        user = cursor.fetchone()
        
        if user is None:
            print(f"No user found with name {u_name} and group ID {g_id}.")
            return

        u_id = user[0]  # Get u_id from the result

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
        # print(f"Message from user {u_name} added successfully to group {g_name}.")

    except Error as e:
        print(f"Message_Error: {e}")

# def entry_message(connection, u_id, message, g_id):
#     try:
#         cursor = connection.cursor()

#         # Retrieve the group name based on g_id to determine the message table
#         cursor.execute("SELECT g_name FROM group_data WHERE g_id = %s", (g_id,))
#         group = cursor.fetchone()

#         if group is None:
#             print(f"No group found with ID {g_id}.")
#             return
        
#         g_name = group[0]
#         message_table_name = f"{g_name}_message"

#         # SQL query to insert a new message
#         insert_query = f"""
#         INSERT INTO `{message_table_name}` (u_id, message, g_id)
#         VALUES (%s, %s, %s)
#         """

#         # Execute the query with the provided arguments
#         cursor.execute(insert_query, (u_id, message, g_id))

#         # Commit the transaction
#         connection.commit()
#         print(f"Message from user {u_id} added successfully to group {g_name}.")

#     except Error as e:
#         print(f"Error: {e}")

def get_all_groups(connection):
    try:
        cursor = connection.cursor()
        
        # SQL query to fetch all group names from the groups table
        fetch_query = "SELECT g_name FROM group_data"
        cursor.execute(fetch_query)
        
        # Fetch all group names
        groups = cursor.fetchall()
        
        # Convert the group names to a single string separated by '|'
        group_string = '|'.join([group[0] for group in groups])
        
        return group_string

    except Error as e:
        print(f"Groups_name_Error: {e}")
        return None
    finally:
        cursor.close()

def is_user_present(connection, u_name, g_id):
    try:
        cursor = connection.cursor()

        # SQL query to check if the user exists with the specified g_id
        select_query = """
        SELECT COUNT(*) FROM user_data WHERE u_name = %s AND g_id = %s
        """
        
        # Execute the query with the provided username and group ID
        cursor.execute(select_query, (u_name, g_id))
        
        # Fetch result
        result = cursor.fetchone()[0]
        
        # Always close the cursor after you're done
        cursor.close()
        
        # Check if the user exists
        if result > 0:
            # User with the given u_name and g_id exists
            return True
        else:
            # User with the given u_name and g_id does not exist
            return False

    except Error as e:
        print(f"User_check_error_Error: {e}")
        return False



def get_group_id(connection, g_name):
    try:
        cursor = connection.cursor()

        # SQL query to retrieve g_id based on g_name
        select_query = """
        SELECT g_id FROM group_data WHERE g_name = %s
        """
        
        # Execute the query with the provided group name
        cursor.execute(select_query, (g_name,))
        
        # Fetch the result
        result = cursor.fetchone()
        
        # Check if a result was found
        if result:
            g_id = result[0]
            # print(f"Group ID for {g_name} is {g_id}.")
            return g_id
        else:
            # print(f"No group found with the name {g_name}.")
            return None

    except Error as e:
        print(f"group_id_Error: {e}")
        return None

# Example usage of entry_message
# connection = check_database_connection()
# print(get_group_id(connection,"KS"))
# print(is_user_present(connection,"Aku",104))
# str= get_all_groups(connection)
# print(str)
# create_user(connection,2, 102, 'Doe')
# create_group(connection,103,'LD',0)
# delete_group(connection,103,'KS')
# entry_message(connection, 'Roy', "Hello, this is a test message!", 103)

