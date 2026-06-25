from services.live_audio_service import record_audio_chunk
from services.transcription_service import transcribe_audio

from services.meeting_service import (
    append_transcript,
    end_live_meeting
)

from services.live_summary_service import (
    generate_meeting_summary
)

meeting_id = 4

print("Meeting Started")

while True:

    audio_file = record_audio_chunk()

    transcript = transcribe_audio(
        audio_file
    )

    print("\nTranscript:")
    print(transcript)

    if "stop meeting" in transcript.lower():

        print("\nStopping Meeting...")

        summary = generate_meeting_summary(
            meeting_id
        )

        end_live_meeting(
            meeting_id
        )

        print("\nMeeting Summary:\n")
        print(summary)

        print("\nMeeting Ended")

        break

    append_transcript(
        meeting_id,
        transcript
    )

    print("Saved")