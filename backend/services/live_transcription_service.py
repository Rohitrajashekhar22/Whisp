from services.transcription_service import (
    transcribe_audio
)


def transcribe_chunk(
    audio_path: str,
    user_id: int,
    meeting_id: int
):

    return transcribe_audio(
        audio_path=audio_path,
        user_id=user_id,
        meeting_id=meeting_id
    )