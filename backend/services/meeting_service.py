from database.db import get_db_connection


# ==========================
# MEETINGS TABLE FUNCTIONS
# ==========================

def create_meeting(user_id, title, source_type, source_url=None, file_path=None):
    connection = get_db_connection()
    cursor = connection.cursor()

    query = """
    INSERT INTO meetings (
        user_id,
        title,
        source_type,
        source_url,
        file_path,
        status
    )
    VALUES (%s, %s, %s, %s, %s, %s)
    """

    cursor.execute(
        query,
        (
            user_id,
            title,
            source_type,
            source_url,
            file_path,
            "processing"
        )
    )

    connection.commit()

    meeting_id = cursor.lastrowid

    cursor.close()
    connection.close()

    return meeting_id


def save_uploaded_meeting(meeting_id, file_path):
    connection = get_db_connection()
    cursor = connection.cursor()

    query = """
    UPDATE meetings
    SET file_path = %s
    WHERE id = %s
    """

    cursor.execute(query, (file_path, meeting_id))

    connection.commit()

    cursor.close()
    connection.close()


def save_youtube_meeting(meeting_id, youtube_url):
    connection = get_db_connection()
    cursor = connection.cursor()

    query = """
    UPDATE meetings
    SET source_url = %s
    WHERE id = %s
    """

    cursor.execute(query, (youtube_url, meeting_id))

    connection.commit()

    cursor.close()
    connection.close()


def update_transcript(meeting_id, transcript):
    connection = get_db_connection()
    cursor = connection.cursor()

    query = """
    UPDATE meetings
    SET transcript = %s
    WHERE id = %s
    """

    cursor.execute(query, (transcript, meeting_id))

    connection.commit()

    cursor.close()
    connection.close()


def update_summary(meeting_id, summary):
    connection = get_db_connection()
    cursor = connection.cursor()

    query = """
    UPDATE meetings
    SET summary = %s
    WHERE id = %s
    """

    cursor.execute(query, (summary, meeting_id))

    connection.commit()

    cursor.close()
    connection.close()


def update_key_points(meeting_id, key_points):
    connection = get_db_connection()
    cursor = connection.cursor()

    query = """
    UPDATE meetings
    SET key_points = %s
    WHERE id = %s
    """

    cursor.execute(query, (key_points, meeting_id))

    connection.commit()

    cursor.close()
    connection.close()


def update_tasks(meeting_id, tasks):
    connection = get_db_connection()
    cursor = connection.cursor()

    query = """
    UPDATE meetings
    SET tasks = %s
    WHERE id = %s
    """

    cursor.execute(query, (tasks, meeting_id))

    connection.commit()

    cursor.close()
    connection.close()


def update_decisions(meeting_id, decisions):
    connection = get_db_connection()
    cursor = connection.cursor()

    query = """
    UPDATE meetings
    SET decisions = %s
    WHERE id = %s
    """

    cursor.execute(query, (decisions, meeting_id))

    connection.commit()

    cursor.close()
    connection.close()


def update_status(meeting_id, status):
    connection = get_db_connection()
    cursor = connection.cursor()

    query = """
    UPDATE meetings
    SET status = %s
    WHERE id = %s
    """

    cursor.execute(query, (status, meeting_id))

    connection.commit()

    cursor.close()
    connection.close()


def get_user_meetings(user_id):
    connection = get_db_connection()

    cursor = connection.cursor(dictionary=True)

    query = """
    SELECT *
    FROM meetings
    WHERE user_id = %s
    ORDER BY created_at DESC
    """

    cursor.execute(query, (user_id,))

    meetings = cursor.fetchall()

    cursor.close()
    connection.close()

    return meetings


def get_meeting(meeting_id):
    connection = get_db_connection()

    cursor = connection.cursor(dictionary=True)

    query = """
    SELECT *
    FROM meetings
    WHERE id = %s
    """

    cursor.execute(query, (meeting_id,))

    meeting = cursor.fetchone()

    cursor.close()
    connection.close()

    return meeting


def delete_meeting(meeting_id):
    connection = get_db_connection()

    cursor = connection.cursor()

    query = """
    DELETE FROM meetings
    WHERE id = %s
    """

    cursor.execute(query, (meeting_id,))

    connection.commit()

    cursor.close()
    connection.close()


def update_meeting_full(meeting_id, transcript, summary):
    connection = get_db_connection()

    cursor = connection.cursor()

    query = """
    UPDATE meetings
    SET transcript = %s,
        summary = %s,
        status = %s
    WHERE id = %s
    """

    cursor.execute(
        query,
        (
            transcript,
            summary,
            "completed",
            meeting_id
        )
    )

    connection.commit()

    cursor.close()
    connection.close()


# ==========================
# LIVE MEETINGS TABLE
# ==========================

def create_live_meeting(user_id, title):
    connection = get_db_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        INSERT INTO live_meetings
        (user_id, title)
        VALUES (%s, %s)
        """,
        (user_id, title)
    )

    connection.commit()

    meeting_id = cursor.lastrowid

    cursor.close()
    connection.close()

    return meeting_id


def append_transcript(meeting_id, text):
    connection = get_db_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        UPDATE live_meetings
        SET transcript = CONCAT(
            IFNULL(transcript, ''),
            %s
        )
        WHERE id = %s
        """,
       (
    f"{text}\n",
    meeting_id
)
    )

    connection.commit()

    cursor.close()
    connection.close()


def end_live_meeting(meeting_id):
    connection = get_db_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        UPDATE live_meetings
        SET status = 'ended'
        WHERE id = %s
        """,
        (meeting_id,)
    )

    connection.commit()

    cursor.close()
    connection.close()


def get_live_meeting(meeting_id, user_id):

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute(
        """
        SELECT *
        FROM live_meetings
        WHERE id = %s
        AND user_id = %s
        """,
        (
            meeting_id,
            user_id
        )
    )

    meeting = cursor.fetchone()

    cursor.close()
    connection.close()

    return meeting

def save_live_summary(meeting_id, summary):

    connection = get_db_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        UPDATE live_meetings
        SET summary = %s
        WHERE id = %s
        """,
        (summary, meeting_id)
    )

    connection.commit()

    cursor.close()
    connection.close()