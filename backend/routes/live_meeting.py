from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import Dict

from services.live_audio_service import LiveAudioService

router = APIRouter()

# One service instance (model loaded once)
live_service = LiveAudioService()


# -----------------------------
# ACTIVE CONNECTIONS TRACKING
# -----------------------------
active_connections: Dict[str, WebSocket] = {}


# -----------------------------
# WEBSOCKET ENDPOINT
# -----------------------------
@router.websocket("/ws/live/{meeting_id}")
async def live_meeting_websocket(websocket: WebSocket, meeting_id: str):
    """
    Live meeting WebSocket:
    - receives audio chunks
    - sends back transcripts in real time
    """

    await websocket.accept()

    # store connection per meeting
    active_connections[meeting_id] = websocket

    print(f"[LIVE] Meeting started: {meeting_id}")

    try:
        while True:
            # -----------------------------
            # RECEIVE AUDIO CHUNK
            # -----------------------------
            audio_chunk = await websocket.receive_bytes()

            if not audio_chunk:
                continue

            # -----------------------------
            # PROCESS AUDIO
            # -----------------------------
            results = live_service.process_audio_chunk(audio_chunk)

            # -----------------------------
            # SEND BACK RESPONSE
            # -----------------------------
            await websocket.send_json({
                "meeting_id": meeting_id,
                "type": "transcript",
                "data": results
            })

    except WebSocketDisconnect:
        print(f"[LIVE] Meeting ended: {meeting_id}")

    except Exception as e:
        print(f"[ERROR] Live meeting {meeting_id}: {str(e)}")

    finally:
        # cleanup
        if meeting_id in active_connections:
            del active_connections[meeting_id]