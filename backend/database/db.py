import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv
import os

load_dotenv()


def get_db_connection():
    try:
        return mysql.connector.connect(
            host="localhost",
            user="root",
            password="Rohit@444",
            database="ai_meeting_assistant"
        )
    except Error as e:
        print("Database connection error:", e)
        return None

        return connection

    except Error as e:

        print("Database connection error:", e)

        return None


# EXECUTE QUERY
def execute_query(connection, query, values=None):

    try:

        cursor = connection.cursor(dictionary=True)

        if values:
            cursor.execute(query, values)
        else:
            cursor.execute(query)

        return cursor

    except Error as e:

        print("Query execution error:", e)

        return None


# COMMIT CHANGES
def commit_changes(connection):

    try:

        connection.commit()

    except Error as e:

        print("Commit error:", e)


# CLOSE CONNECTION
def close_connection(connection):

    try:

        if connection and connection.is_connected():

            connection.close()

    except Error as e:

        print("Close connection error:", e)