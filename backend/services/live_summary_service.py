import os
from dotenv import load_dotenv
from google import genai

from services.live_meeting_service import LiveMeetingService

load_dotenv()

client = genai.Client()

live_service = LiveMeetingService()


# =====================================================
# GENERATE LIVE MEETING SUMMARY
# =====================================================

def generate_meeting_summary(meeting_id: int, user_id: int):

    meeting = live_service.get_live_meeting(
        meeting_id,
        user_id
    )

    if meeting is None:
        raise Exception("Meeting not found")

    transcript = meeting.get("transcript", "")

    if not transcript.strip():
        raise Exception("Transcript is empty")

    prompt = f"""
You are an AI meeting assistant.

Analyze the following meeting transcript.

Return:

1. Summary
2. Key Points
3. Action Items
4. Decisions

Keep everything concise.

Transcript:
{transcript}
"""

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )

    summary = response.text

    live_service.save_live_summary(
        meeting_id,
        summary
    )

    return summary