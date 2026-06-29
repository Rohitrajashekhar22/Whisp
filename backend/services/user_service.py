import bcrypt

from database.db import (
    get_db_connection,
    execute_query,
    commit_changes,
    close_connection
)


# =====================================================
# PASSWORD HASHING
# =====================================================

def hash_password(password: str) -> str:

    salt = bcrypt.gensalt()

    hashed = bcrypt.hashpw(
        password.encode("utf-8"),
        salt
    )

    return hashed.decode("utf-8")


def verify_password(
    password: str,
    password_hash: str
) -> bool:

    return bcrypt.checkpw(
        password.encode("utf-8"),
        password_hash.encode("utf-8")
    )


# =====================================================
# FIND USER BY EMAIL
# =====================================================

def find_user_by_email(email: str):

    connection = get_db_connection()

    if connection is None:
        return None

    cursor = None

    try:

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

        if cursor is None:
            return None

        return cursor.fetchone()

    finally:

        if cursor:
            cursor.close()

        close_connection(connection)


# =====================================================
# FIND USER BY ID
# =====================================================

def find_user_by_id(user_id: int):

    connection = get_db_connection()

    if connection is None:
        return None

    cursor = None

    try:

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

        if cursor is None:
            return None

        return cursor.fetchone()

    finally:

        if cursor:
            cursor.close()

        close_connection(connection)


# =====================================================
# CHECK DUPLICATE EMAIL
# =====================================================

def is_email_duplicate(email: str) -> bool:

    connection = get_db_connection()

    if connection is None:
        return False

    cursor = None

    try:

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

        if cursor is None:
            return False

        result = cursor.fetchone()

        return result["count"] > 0

    finally:

        if cursor:
            cursor.close()

        close_connection(connection)


# =====================================================
# REGISTER USER
# =====================================================

def register_user(
    name: str,
    email: str,
    password: str
):

    if is_email_duplicate(email):

        return {
            "success": False,
            "message": "Email already exists"
        }

    connection = get_db_connection()

    if connection is None:

        return {
            "success": False,
            "message": "Database connection failed"
        }

    cursor = None

    try:

        password_hash = hash_password(password)

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

        cursor = execute_query(
            connection,
            query,
            (
                name,
                email,
                password_hash
            )
        )

        if cursor is None:
            raise Exception("Failed to execute query")

        commit_changes(connection)

        return {
            "success": True,
            "message": "User registered successfully"
        }

    except Exception as e:

        connection.rollback()

        return {
            "success": False,
            "message": str(e)
        }

    finally:

        if cursor:
            cursor.close()

        close_connection(connection)