from fastapi import (
    APIRouter,
    UploadFile,
    File,
    Form,
    Depends,
    HTTPException
)

import os
import shutil
import logging

from google import genai

from security import get_current_user

from services.youtube_service import get_youtube_transcript

from services.meeting_service import (
    create_meeting,
    update_transcript,
    update_summary,
    update_status,
    get_user_meetings,
    get_meeting,
    delete_meeting,
    save_uploaded_meeting
)

from services.chat_service import (
    save_chat_message,
    get_chat_history,
    delete_chat_by_meeting
)

from services.transcription_service import (
    transcribe_audio
)

from services.summarization_service import (
    summarize_transcript,
    save_summary
)

from services.embedding_service import (
    create_meeting_embeddings
)

from services.audio_service import (
    convert_mp3_to_wav,
    convert_mp4_to_wav
)

router = APIRouter(
    prefix="/meetings",
    tags=["Meetings"]
)

logger = logging.getLogger(__name__)

client = genai.Client()


# =====================================================
# VERIFY OWNERSHIP
# =====================================================

def verify_meeting_owner(meeting_id, current_user):

    meeting = get_live_meeting(
        meeting_id,
        current_user["id"]
    )

    if meeting is None:
        raise HTTPException(
            status_code=404,
            detail="Meeting not found"
        )

    return meeting


# =====================================================
# YOUTUBE MEETING
# =====================================================

@router.post("/youtube")
def process_youtube_meeting(

    title: str = Form(...),

    youtube_url: str = Form(...),

    current_user=Depends(get_current_user)

):

    user_id = current_user["id"]

    meeting_id = create_meeting(

        user_id=user_id,

        title=title,

        source_type="youtube",

        source_url=youtube_url,

        file_path=None

    )

    update_status(
        meeting_id,
        "processing"
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

        update_transcript(
            meeting_id,
            transcript
        )

        create_meeting_embeddings(
            meeting_id,
            user_id
        )

        summary = summarize_transcript(
            transcript
        )

        update_summary(
            meeting_id,
            summary
        )

        save_summary(

            summary,

            title,

            user_id,

            meeting_id

        )

        update_status(
            meeting_id,
            "completed"
        )

        return {

            "meeting_id": meeting_id,

            "title": title,

            "summary": summary,

            "status": "completed"

        }

    except Exception as e:

        logger.exception(e)

        update_status(
            meeting_id,
            "failed"
        )

        raise HTTPException(

            status_code=500,

            detail=str(e)

        )


# =====================================================
# UPLOAD MEETING
# =====================================================

@router.post("/upload")
async def upload_meeting(

    title: str = Form(...),

    file: UploadFile = File(...),

    current_user=Depends(get_current_user)

):

    user_id = current_user["id"]

    meeting_id = create_meeting(

        user_id=user_id,

        title=title,

        source_type="upload",

        source_url=None,

        file_path=None

    )

    update_status(
        meeting_id,
        "processing"
    )

    try:

        upload_dir = (
            f"uploads/user_{user_id}/meeting_{meeting_id}"
        )

        os.makedirs(
            upload_dir,
            exist_ok=True
        )

        file_path = os.path.join(
            upload_dir,
            file.filename
        )

        with open(
            file_path,
            "wb"
        ) as f:

            shutil.copyfileobj(
                file.file,
                f
            )

        save_uploaded_meeting(
            meeting_id,
            file_path
        )

        filename = os.path.splitext(
            file.filename
        )[0]

        extension = os.path.splitext(
            file.filename
        )[1].lower()

        processed_dir = (
            f"processed/user_{user_id}/meeting_{meeting_id}"
        )

        os.makedirs(
            processed_dir,
            exist_ok=True
        )

        wav_path = os.path.join(
            processed_dir,
            f"{filename}.wav"
        )

        if extension == ".mp3":

            convert_mp3_to_wav(
                file_path,
                wav_path
            )

        elif extension == ".mp4":

            convert_mp4_to_wav(
                file_path,
                wav_path
            )

        elif extension == ".wav":

            wav_path = file_path

        else:

            update_status(
                meeting_id,
                "failed"
            )

            raise HTTPException(

                status_code=400,

                detail="Only mp3, mp4 and wav are supported."

            )

        transcript = transcribe_audio(

            wav_path,

            user_id,

            meeting_id

        )

        update_transcript(

            meeting_id,

            transcript

        )

        create_meeting_embeddings(

            meeting_id,

            user_id

        )

        summary = summarize_transcript(
            transcript
        )

        update_summary(
            meeting_id,
            summary
        )

        save_summary(

            summary,

            file.filename,

            user_id,

            meeting_id

        )

        update_status(
            meeting_id,
            "completed"
        )

        return {

            "meeting_id": meeting_id,

            "title": title,

            "summary": summary,

            "status": "completed"

        }

    except Exception as e:

        logger.exception(e)

        update_status(
            meeting_id,
            "failed"
        )

        raise HTTPException(

            status_code=500,

            detail=str(e)

        )# =====================================================
# GET ALL USER MEETINGS
# =====================================================

@router.get("/")
def get_meetings(

    current_user=Depends(get_current_user)

):

    return get_user_meetings(

        current_user["id"]

    )


# =====================================================
# GET SINGLE MEETING
# =====================================================

@router.get("/{meeting_id}")
def get_single_meeting(

    meeting_id: int,

    current_user=Depends(get_current_user)

):

    meeting = verify_meeting_owner(

        meeting_id,

        current_user

    )

    return meeting


# =====================================================
# DELETE MEETING
# =====================================================

@router.delete("/{meeting_id}")
def delete_meeting_api(

    meeting_id: int,

    current_user=Depends(get_current_user)

):

    verify_meeting_owner(

        meeting_id,

        current_user

    )

    delete_chat_by_meeting(

        meeting_id

    )

    delete_meeting(

        meeting_id

    )

    return {

        "message": "Meeting deleted successfully"

    }


# =====================================================
# CHAT WITH MEETING
# =====================================================

@router.post("/{meeting_id}/chat")
def chat_with_meeting(

    meeting_id: int,

    question: str = Form(...),

    current_user=Depends(get_current_user)

):

    meeting = verify_meeting_owner(

        meeting_id,

        current_user

    )

    transcript = meeting.get("transcript")

    if not transcript:

        raise HTTPException(

            status_code=404,

            detail="Transcript not found."

        )

    prompt = f"""
You are an AI Meeting Assistant.

Answer ONLY from the transcript below.

If the answer does not exist in the transcript,
say:

"I couldn't find that information in this meeting."

Transcript:

{transcript}

Question:

{question}
"""

    try:

        response = client.models.generate_content(

            model="gemini-2.5-flash",

            contents=prompt

        )

        answer = response.text

        save_chat_message(

            meeting_id=meeting_id,

            user_id=current_user["id"],

            sender="user",

            question=question,

            answer=answer

        )

        return {

            "answer": answer

        }

    except Exception as e:

        logger.exception(e)

        raise HTTPException(

            status_code=500,

            detail="Failed to generate answer."

        )


# =====================================================
# GET CHAT HISTORY
# =====================================================

@router.get("/{meeting_id}/chat")
def chat_history(

    meeting_id: int,

    current_user=Depends(get_current_user)

):

    verify_meeting_owner(

        meeting_id,

        current_user

    )

    history = get_chat_history(

        meeting_id,

        current_user["id"]

    )

    return {

        "meeting_id": meeting_id,

        "history": history

    }