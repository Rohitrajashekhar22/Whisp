from faster_whisper import WhisperModel
import tempfile
import os


class LiveAudioService:

    def __init__(self):
        self.model = WhisperModel(
            "base",
            device="cpu",
            compute_type="int8"
        )

    def process(self, audio_bytes):

        temp = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
        temp.write(audio_bytes)
        temp.close()

        try:
            segments, _ = self.model.transcribe(temp.name)

            text = " ".join([seg.text for seg in segments])

            return {
                "text": text
            }

        finally:
            os.remove(temp.name)