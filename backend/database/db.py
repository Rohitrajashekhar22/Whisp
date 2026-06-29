import os
import mysql.connector
from dotenv import load_dotenv

load_dotenv()

def get_db_connection():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME")
    )


def execute_query(conn, query, params=None, fetchone=False, fetchall=False):
    cursor = conn.cursor(dictionary=True)

    cursor.execute(query, params or ())

    result = None

    if fetchone:
        result = cursor.fetchone()
    elif fetchall:
        result = cursor.fetchall()

    cursor.close()
    return result


def commit_changes(conn):
    conn.commit()


def close_connection(conn):
    conn.close()