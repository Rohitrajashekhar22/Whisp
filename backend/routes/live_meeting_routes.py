from fastapi import APIRouter, Form
import threading

from services.embedding_service import create_meeting_embeddings
from services.meeting_service import (
    create_live_meeting,
    get_live_meeting,
    end_live_meeting
)

from services.live_stream_service import (
    start_live_stream,
    stop_meeting
)

from services.live_summary_service import (
    generate_meeting_summary
)

router = APIRouter()

# -------------------------
# START LIVE MEETING
# -------------------------
@router.post("/start-meeting")
def start_meeting(
    user_id: int = Form(...),
    title: str = Form(...)
):

    meeting_id = create_live_meeting(
        user_id,
        title
    )

    thread = threading.Thread(
        target=start_live_stream,
        args=(meeting_id, user_id),
        daemon=True
    )

    thread.start()

    return {
        "message": "Live meeting started",
        "meeting_id": meeting_id
    }


# -------------------------
# STOP LIVE MEETING
# -------------------------
@router.post("/stop-meeting")
def stop_live_meeting():

    stop_meeting()

    return {
        "message": "Meeting stopped"
    }


# -------------------------
# GET LIVE MEETING
# -------------------------
@router.get("/live-meeting/{meeting_id}")
def get_meeting_data(meeting_id: int):

    meeting = get_live_meeting(
        meeting_id
    )

    return meeting


# -------------------------
# GET TRANSCRIPT
# -------------------------
@router.get("/live-meeting/{meeting_id}/transcript")
def get_transcript(meeting_id: int):

    meeting = get_live_meeting(
        meeting_id
    )

    return {
        "meeting_id": meeting_id,
        "transcript": meeting["transcript"]
    }


# -------------------------
# GENERATE SUMMARY
# -------------------------
@router.post("/live-meeting/{meeting_id}/summary")
def create_summary(meeting_id: int):

    summary = generate_meeting_summary(
        meeting_id
    )

    return {
        "meeting_id": meeting_id,
        "summary": summary
    }


# -------------------------
# GET SUMMARY
# -------------------------
@router.get("/live-meeting/{meeting_id}/summary")
def get_summary(meeting_id: int):

    meeting = get_live_meeting(
        meeting_id
    )

    return {
        "meeting_id": meeting_id,
        "summary": meeting["summary"]
    }


# -------------------------
# END LIVE MEETING
# -------------------------
@router.post("/live-meeting/{meeting_id}/end")
def end_meeting(meeting_id:int):






    # generate and store meeting summary
    generate_meeting_summary(meeting_id)

    # create embeddings here
    create_meeting_embeddings(
        meeting_id
    )


    end_live_meeting(meeting_id)


    return {
        "message":"Meeting ended"
    }