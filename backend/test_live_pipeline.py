from services.live_audio_service import record_audio_chunk
from services.transcription_service import transcribe_audio
from services.meeting_service import append_transcript

meeting_id = 4

audio_file = record_audio_chunk()

transcript = transcribe_audio(audio_file)

print("Transcript:")
print(transcript)

append_transcript(
    meeting_id,
    transcript
)

print("Saved to database")