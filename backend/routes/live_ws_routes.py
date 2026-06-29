from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
from security import decode_token
from services.websocket_manager import manager
from services.live_meeting_service import LiveMeetingService
from services.live_audio_service import LiveAudioService

router = APIRouter()

live_service = LiveMeetingService()


@router.websocket("/ws/live/{meeting_id}")
async def live_ws(websocket: WebSocket, meeting_id: int, token: str = Query(...)):

    # AUTH
    try:
        user = decode_token(token)
        user_id = user["user_id"]
    except:
        await websocket.close(code=4001)
        return

    await manager.connect(meeting_id, websocket)

    audio_service = LiveAudioService()

    try:
        while True:
            audio = await websocket.receive_bytes()

            result = audio_service.process(audio)

            # ✅ SAVE TRANSCRIPT (CRITICAL FIX)
            if isinstance(result, dict) and result.get("text"):
                live_service.append_transcript(meeting_id, result["text"])

            await manager.send(meeting_id, {
                "type": "transcript",
                "data": result
            })

    except WebSocketDisconnect:
        manager.disconnect(meeting_id, websocket)