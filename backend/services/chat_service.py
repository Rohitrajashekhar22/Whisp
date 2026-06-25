from database.db import get_db_connection


# -------------------------
# SAVE CHAT MESSAGE
# -------------------------
def save_chat_message(meeting_id, user_id, sender, question, answer):

    db = get_db_connection()
    cursor = db.cursor()

    try:
        query = """
        INSERT INTO chat_messages (
            meeting_id,
            user_id,
            sender,
            question,
            answer
        )
        VALUES (%s, %s, %s, %s, %s)
        """

        cursor.execute(query, (
            meeting_id,
            user_id,
            sender,
            question,
            answer
        ))

        db.commit()

    finally:
        cursor.close()
        db.close()


# -------------------------
# GET CHAT HISTORY
# -------------------------
def get_chat_history(meeting_id, user_id):

    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    try:
        query = """
        SELECT *
        FROM chat_messages
        WHERE meeting_id = %s
        AND user_id = %s
        ORDER BY id ASC
        """

        cursor.execute(query, (meeting_id, user_id))
        return cursor.fetchall()

    finally:
        cursor.close()
        db.close()


# -------------------------
# DELETE CHAT HISTORY
# -------------------------
def delete_chat_by_meeting(meeting_id):

    db = get_db_connection()
    cursor = db.cursor()

    try:
        query = """
        DELETE FROM chat_messages
        WHERE meeting_id = %s
        """

        cursor.execute(query, (meeting_id,))
        db.commit()

    finally:
        cursor.close()
        db.close()