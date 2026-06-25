from fastapi import APIRouter, UploadFile, File, Form
from google import genai

from services.youtube_service import get_youtube_transcript
from services.meeting_service import (
    create_meeting,
    update_transcript,
    update_summary,
    update_status,
    get_user_meetings,
    get_meeting,
    delete_meeting
)

from services.chat_service import (
    save_chat_message,
    get_chat_history,
    delete_chat_by_meeting
)

from services.transcription_service import transcribe_audio
from services.summarization_service import summarize_transcript

import shutil
import os

router = APIRouter(prefix="/meetings", tags=["Meetings"])

client = genai.Client()

# =====================================================
# 1. YOU TUBE (MODIFIED YOUR EXISTING CODE)
# =====================================================
@router.post("/youtube")
def process_youtube_meeting(
    user_id: int = Form(...),
    title: str = Form(...),
    youtube_url: str = Form(...)
):

    print("=" * 50)
    print("USER ID:", user_id)
    print("TITLE:", title)
    print("URL:", youtube_url)
    print("=" * 50)

    meeting_id = create_meeting(
        user_id=user_id,
        title=title,
        source_type="youtube",
        source_url=youtube_url,
        file_path=None
    )

    try:

        result = get_youtube_transcript(
            youtube_url
        )

        if not result["success"]:

            update_status(
                meeting_id,
                "failed"
            )

            return result

        transcript = result["transcript"]

        print(
            "TRANSCRIPT LENGTH:",
            len(transcript)
        )

        update_transcript(
            meeting_id,
            transcript
        )

        summary = summarize_transcript(
            transcript
        )

        print("SUMMARY:")
        print(summary)

        update_summary(
            meeting_id,
            summary
        )

        update_status(
            meeting_id,
            "completed"
        )

        return {
            "meeting_id": meeting_id,
            "title": title,
            "transcript": transcript,
            "summary": summary,
            "status": "completed"
        }

    except Exception as e:

        print("YOUTUBE ERROR:", str(e))

        update_status(
            meeting_id,
            "failed"
        )

        return {
            "error": str(e)
        }

# =====================================================
# 2. UPLOAD MEETING (NEW)
# =====================================================

@router.post("/upload")
async def upload_meeting(
    user_id: int = Form(...),
    title: str = Form(...),
    file: UploadFile = File(...)
):

    file_path = f"uploads/user_{user_id}/meeting_{meeting_id}/{file.filename}"

    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    with open(file_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    meeting_id = create_meeting(
        user_id=user_id,
        title=title,
        source_type="upload",
        source_url=None,
        file_path=file_path
    )

    transcript = transcribe_audio(file_path, user_id, meeting_id)
    update_transcript(meeting_id, transcript)

    summary = summarize_transcript(transcript)
    update_summary(meeting_id, summary)

    update_status(meeting_id, "completed")

    save_summary(summary, file.filename, user_id, meeting_id)

    return {
        "meeting_id": meeting_id,
        "title": title,
        "transcript": transcript,
        "summary": summary,
        "status": "completed"
    }

# =====================================================
# 3. GET ALL MEETINGS (FIXED STEP 17)
# =====================================================

@router.get("/")
def get_meetings(user_id: int):
    return get_user_meetings(user_id)

# =====================================================
# 4. GET SINGLE MEETING
# =====================================================

@router.get("/{meeting_id}")
def get_single_meeting(meeting_id: int):
    return get_meeting(meeting_id)

# =====================================================
# 5. DELETE MEETING (WITH CHAT CLEANUP)
# =====================================================

@router.delete("/{meeting_id}")
def delete_meeting_api(meeting_id: int):

    delete_chat_by_meeting(meeting_id)
    delete_meeting(meeting_id)

    return {"message": "Deleted successfully"}

# =====================================================
# 6. CHAT WITH MEETING (STEP 15 + 17)
# =====================================================

@router.post("/{meeting_id}/chat")
def chat_with_meeting(
    meeting_id: int,
    user_id: int,
    question: str
):

    meeting = get_meeting(meeting_id)

    if not meeting:
        return {"error": "Meeting not found"}

    transcript = meeting["transcript"]

    prompt = f"""
You are an AI assistant.

Use ONLY this transcript:

{transcript}

Question:
{question}
"""

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )

    answer = response.text

    save_chat_message(
        meeting_id,
        user_id,
        "user",
        question,
        answer
    )

    return {
        "answer": answer
    }

# =====================================================
# 7. GET CHAT HISTORY
# =====================================================

@router.get("/meetings/{meeting_id}/chat")
def chat_history(
    meeting_id: int,
    user_id: int
):

    history = get_chat_history(
        meeting_id,
        user_id
    )

    return {
        "meeting_id": meeting_id,
        "history": history
    }