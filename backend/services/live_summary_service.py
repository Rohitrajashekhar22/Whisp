import os
from dotenv import load_dotenv

from services.meeting_service import (
    get_live_meeting,
    save_live_summary
)

load_dotenv()
from google import genai

client = genai.Client()


def generate_meeting_summary(meeting_id):

    meeting = get_live_meeting(meeting_id)

    transcript = meeting["transcript"]

    prompt = f"""
You are an AI meeting assistant.

Analyze the following meeting transcript.

Return a clean meeting summary.

Transcript:

{transcript}
"""

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )

    summary = response.text

    save_live_summary(
        meeting_id,
        summary
    )

    return summary