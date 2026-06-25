from services.transcription_service import (
    transcribe_audio
)


def transcribe_chunk(
    audio_path
):

    transcript = transcribe_audio(
        audio_path
    )

    return transcript