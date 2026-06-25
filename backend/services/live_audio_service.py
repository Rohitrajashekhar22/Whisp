import sounddevice as sd
from scipy.io.wavfile import write
import os
import uuid


def record_audio_chunk(user_id, meeting_id):

    temp_dir = f"temp/user_{user_id}/meeting_{meeting_id}"
    os.makedirs(
        temp_dir,
        exist_ok=True
    )
    filename = f"{temp_dir}/{uuid.uuid4()}.wav"

    sample_rate = 16000

    duration = 5

    print("Recording...")

    audio = sd.rec(
        int(duration * sample_rate),
        samplerate=sample_rate,
        channels=1,
        dtype="int16"
    )

    sd.wait()

    write(
        filename,
        sample_rate,
        audio
    )

    print("Recording Finished")

    return filename