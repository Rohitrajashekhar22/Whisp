from fastapi import APIRouter, Depends, Form, HTTPException
import threading

from security import get_current_user

from services.live_meeting_service import LiveMeetingService
from services.live_stream_service import (
    start_live_stream,
    stop_meeting,
    is_meeting_running
)
from services.live_summary_service import generate_meeting_summary
from services.embedding_service import create_meeting_embeddings

router = APIRouter(
    tags=["Live Meeting"]
)

service = LiveMeetingService()


# =====================================================
# VERIFY OWNER
# =====================================================

def verify_meeting_owner(
    meeting_id: int,
    current_user
):

    meeting = service.get_live_meeting(
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
# START MEETING
# =====================================================

@router.post("/start")
def start_meeting(
    title: str = Form(...),
    current_user=Depends(get_current_user)
):

    meeting_id = service.create_live_meeting(
        current_user["id"],
        title
    )

    threading.Thread(
        target=start_live_stream,
        args=(meeting_id, current_user["id"]),
        daemon=True
    ).start()

    return {
        "message": "Meeting started",
        "meeting_id": meeting_id
    }


# =====================================================
# STOP RECORDING
# =====================================================

@router.post("/{meeting_id}/stop")
def stop_recording(
    meeting_id: int,
    current_user=Depends(get_current_user)
):

    verify_meeting_owner(
        meeting_id,
        current_user
    )

    if not stop_meeting(meeting_id):
        raise HTTPException(
            status_code=400,
            detail="Meeting already stopped"
        )

    return {
        "message": "Recording stopped"
    }


# =====================================================
# END MEETING
# =====================================================

@router.post("/{meeting_id}/end")
def end_meeting(
    meeting_id: int,
    current_user=Depends(get_current_user)
):

    verify_meeting_owner(
        meeting_id,
        current_user
    )

    stop_meeting(meeting_id)

    summary = generate_meeting_summary(
        meeting_id,
        current_user["id"]
    )

    try:
        create_meeting_embeddings(
            meeting_id,
            current_user["id"]
        )
    except Exception as e:
        print(e)

    service.end_live_meeting(meeting_id)

    return {
        "message": "Meeting ended",
        "summary": summary
    }


# =====================================================
# GET MEETING
# =====================================================

@router.get("/{meeting_id}")
def get_meeting(
    meeting_id: int,
    current_user=Depends(get_current_user)
):

    return verify_meeting_owner(
        meeting_id,
        current_user
    )


# =====================================================
# GET TRANSCRIPT
# =====================================================

@router.get("/{meeting_id}/transcript")
def get_transcript(
    meeting_id: int,
    current_user=Depends(get_current_user)
):

    meeting = verify_meeting_owner(
        meeting_id,
        current_user
    )

    return {
        "transcript": meeting["transcript"]
    }


# =====================================================
# GET SUMMARY
# =====================================================

@router.get("/{meeting_id}/summary")
def get_summary(
    meeting_id: int,
    current_user=Depends(get_current_user)
):

    meeting = verify_meeting_owner(
        meeting_id,
        current_user
    )

    return {
        "summary": meeting["summary"]
    }


# =====================================================
# STATUS
# =====================================================

@router.get("/{meeting_id}/status")
def meeting_status(
    meeting_id: int,
    current_user=Depends(get_current_user)
):

    verify_meeting_owner(
        meeting_id,
        current_user
    )

    return {
        "running": is_meeting_running(meeting_id)
    }