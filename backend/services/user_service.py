import bcrypt
from database.db import get_db_connection, execute_query, commit_changes, close_connection
#hash password
def hash_password(password):

    salt = bcrypt.gensalt()

    hashed = bcrypt.hashpw(
        password.encode("utf-8"),
        salt
    )

    return hashed.decode("utf-8")

def verify_password(password, password_hash):

    return bcrypt.checkpw(
        password.encode("utf-8"),
        password_hash.encode("utf-8")
    )
#find user by email
def find_user_by_email(email):

    connection = get_db_connection()

    query = """
    SELECT *
    FROM users
    WHERE email = %s
    """

    cursor = execute_query(
        connection,
        query,
        (email,)
    )

    user = cursor.fetchone()

    close_connection(connection)

    return user
#find by id
def find_user_by_id(user_id):

    connection = get_db_connection()

    query = """
    SELECT *
    FROM users
    WHERE id = %s
    """

    cursor = execute_query(
        connection,
        query,
        (user_id,)
    )

    user = cursor.fetchone()

    close_connection(connection)

    return user
#check duplicate email
def is_email_duplicate(email):

    connection = get_db_connection()

    query = """
    SELECT COUNT(*) AS count
    FROM users
    WHERE email = %s
    """

    cursor = execute_query(
        connection,
        query,
        (email,)
    )

    result = cursor.fetchone()

    close_connection(connection)

    return result["count"] > 0
#register user

def register_user(name, email, password):

    if is_email_duplicate(email):

        return {
            "success": False,
            "message": "Email already exists"
        }


    password_hash = hash_password(password)


    connection = get_db_connection()


    if connection is None:

        return {
            "success": False,
            "message": "Database connection failed"
        }


    query = """
    INSERT INTO users
    (
        username,
        email,
        password_hash
    )
    VALUES
    (
        %s,
        %s,
        %s
    )
    """


    execute_query(
        connection,
        query,
        (
            name,
            email,
            password_hash
        )
    )


    commit_changes(connection)

    close_connection(connection)


    return {
        "success": True,
        "message": "User registered successfully"
    }