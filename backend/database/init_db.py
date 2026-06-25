from db import get_db_connection


def init_db():

    connection = get_db_connection()

    if connection is None:

        print("Database connection failed")

        return

    cursor = connection.cursor()

    try:

        with open("database/schema.sql", "r") as file:

            sql_script = file.read()

        queries = sql_script.split(";")

        for query in queries:

            query = query.strip()

            if query:

                cursor.execute(query)

        connection.commit()

        print("Database initialized successfully")

    except Exception as e:

        print("Database initialization error:", e)

    finally:

        cursor.close()

        connection.close()


if __name__ == "__main__":
    init_db()