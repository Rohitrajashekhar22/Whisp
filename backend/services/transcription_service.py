import whisper
import os
import re

print("Loading Whisper model...")

model = whisper.load_model(
    "base"
)

print("Whisper loaded!")


def transcribe_audio(audio_path, user_id, meeting_id):

    print("Transcribing...")

    result = model.transcribe(
        audio_path
    )

    transcript = result["text"]

    # create transcripts folder if it doesn't exist
    os.makedirs(
        "transcripts",
        exist_ok=True
    )

    # get filename without extension
    file_name = os.path.basename(
        audio_path
    )

    file_name = os.path.splitext(
        file_name
    )[0]

    # remove invalid characters for Windows
    safe_file_name = re.sub(
        r'[\\/*?:"<>|]',
        "",
        file_name
    )

    # transcript file path
    txt_file_path = (
        f"transcripts/user_{user_id}/meeting_{meeting_id}/{safe_file_name}.txt"
    )
    
    os.makedirs(os.path.dirname(txt_file_path), exist_ok=True)

    # save transcript to txt file
    with open(
        txt_file_path,
        "w",
        encoding="utf-8"
    ) as file:
        file.write(
            transcript
        )

    print("Done!")

    return transcript