from database.db import get_db_connection
from typing import List, Dict, Optional


# =====================================================
# LIVE MEETING SERVICE (PRODUCTION CLEAN VERSION)
# =====================================================

class LiveMeetingService:

    # -------------------------------------------------
    # CREATE MEETING
    # -------------------------------------------------
    def create_live_meeting(self, user_id: int, title: str) -> int:

        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            cursor.execute(
                """
                INSERT INTO live_meetings (user_id, title, status)
                VALUES (%s, %s, 'active')
                """,
                (user_id, title)
            )

            conn.commit()
            return cursor.lastrowid

        finally:
            cursor.close()
            conn.close()

    # -------------------------------------------------
    # GET SINGLE MEETING (SECURE)
    # -------------------------------------------------
    def get_live_meeting(self, meeting_id: int, user_id: int):

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        try:
            cursor.execute(
                """
                SELECT *
                FROM live_meetings
                WHERE id=%s AND user_id=%s
                """,
                (meeting_id, user_id)
            )

            return cursor.fetchone()

        finally:
            cursor.close()
            conn.close()

    # -------------------------------------------------
    # APPEND SIMPLE TRANSCRIPT
    # -------------------------------------------------
    def append_transcript(self, meeting_id: int, transcript: str):

        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            cursor.execute(
                """
                UPDATE live_meetings
                SET transcript = CONCAT(IFNULL(transcript,''), %s)
                WHERE id=%s
                """,
                ("\n" + transcript, meeting_id)
            )

            conn.commit()

        finally:
            cursor.close()
            conn.close()

    # -------------------------------------------------
    # STRUCTURED TRANSCRIPT (SPEAKERS)
    # -------------------------------------------------
    def append_structured_transcript(self, meeting_id: int, segments: List[Dict]):

        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            formatted = ""

            for seg in segments:
                speaker = seg.get("speaker", "Unknown")
                text = seg.get("text", "").strip()

                if text:
                    formatted += f"{speaker}: {text}\n"

            cursor.execute(
                """
                UPDATE live_meetings
                SET transcript = CONCAT(IFNULL(transcript,''), %s)
                WHERE id=%s
                """,
                (formatted, meeting_id)
            )

            conn.commit()

        finally:
            cursor.close()
            conn.close()

    # -------------------------------------------------
    # SAVE SUMMARY
    # -------------------------------------------------
    def save_live_summary(self, meeting_id: int, summary: str):

        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            cursor.execute(
                """
                UPDATE live_meetings
                SET summary=%s
                WHERE id=%s
                """,
                (summary, meeting_id)
            )

            conn.commit()

        finally:
            cursor.close()
            conn.close()

    # -------------------------------------------------
    # END MEETING
    # -------------------------------------------------
    def end_live_meeting(self, meeting_id: int):

        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            cursor.execute(
                """
                UPDATE live_meetings
                SET status='ended',
                    ended_at=NOW()
                WHERE id=%s
                """,
                (meeting_id,)
            )

            conn.commit()

        finally:
            cursor.close()
            conn.close()

    # -------------------------------------------------
    # DELETE MEETING
    # -------------------------------------------------
    def delete_live_meeting(self, meeting_id: int, user_id: int):

        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            cursor.execute(
                """
                DELETE FROM live_meetings
                WHERE id=%s AND user_id=%s
                """,
                (meeting_id, user_id)
            )

            conn.commit()

        finally:
            cursor.close()
            conn.close()

    # -------------------------------------------------
    # GET USER MEETINGS
    # -------------------------------------------------
    def get_user_live_meetings(self, user_id: int):

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        try:
            cursor.execute(
                """
                SELECT *
                FROM live_meetings
                WHERE user_id=%s
                ORDER BY started_at DESC
                """,
                (user_id,)
            )

            return cursor.fetchall()

        finally:
            cursor.close()
            conn.close()