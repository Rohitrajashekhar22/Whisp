import logging
import os
import threading
from pathlib import Path
from typing import Union, Dict, Any

import whisper

logger = logging.getLogger(__name__)


# ==========================================================
# TRANSCRIPTION SERVICE (CLEAN ARCHITECTURE VERSION)
# ==========================================================

class TranscriptionService:
    """
    Whisper transcription layer.

    Supports:
    - file-based transcription (current system)
    - audio buffer / numpy array (future live system)
    """

    def __init__(self, model_name: str = "base"):
        self.model_name = model_name
        self._model = None
        self._lock = threading.Lock()

    # ==========================================================
    # LAZY LOAD MODEL
    # ==========================================================
    def get_model(self):
        if self._model is None:
            with self._lock:
                if self._model is None:
                    logger.info("Loading Whisper model...")
                    self._model = whisper.load_model(self.model_name)
                    logger.info("Whisper model loaded successfully.")
        return self._model

    # ==========================================================
    # MAIN TRANSCRIBE METHOD (FILE OR AUDIO)
    # ==========================================================
    def transcribe(
        self,
        audio_input: Union[str, Any],
        user_id: int = None,
        meeting_id: int = None
    ) -> Dict:
        """
        audio_input:
            - str → file path
            - np.ndarray / audio buffer → future live support
        """

        model = self.get_model()

        # -----------------------------
        # CASE 1: FILE PATH (CURRENT SYSTEM)
        # -----------------------------
        if isinstance(audio_input, str):

            if not os.path.exists(audio_input):
                raise FileNotFoundError(f"Audio file not found: {audio_input}")

            logger.info(f"Transcribing file: {audio_input}")

            result = model.transcribe(audio_input, fp16=False)

        # -----------------------------
        # CASE 2: LIVE AUDIO BUFFER (FUTURE)
        # -----------------------------
        else:
            logger.info("Transcribing audio buffer (live mode)")
            result = model.transcribe(audio_input, fp16=False)

        transcript = result.get("text", "").strip()

        response = {
            "text": transcript,
            "segments": result.get("segments", []),
            "language": result.get("language", None)
        }

        # Save only if IDs provided (batch mode)
        if user_id is not None and meeting_id is not None:
            self._save_transcript(
                transcript,
                audio_input if isinstance(audio_input, str) else "live_audio",
                user_id,
                meeting_id
            )

        return response

    # ==========================================================
    # SAVE TRANSCRIPT (UNCHANGED BUT CLEANED)
    # ==========================================================
    def _save_transcript(
        self,
        transcript: str,
        audio_source: str,
        user_id: int,
        meeting_id: int
    ):
        transcript_dir = Path(
            f"transcripts/user_{user_id}/meeting_{meeting_id}"
        )

        transcript_dir.mkdir(parents=True, exist_ok=True)

        safe_name = Path(str(audio_source)).stem if isinstance(audio_source, str) else "live"

        txt_file = transcript_dir / f"{safe_name}.txt"

        with open(txt_file, "w", encoding="utf-8") as f:
            f.write(transcript)

        logger.info(f"Transcript saved -> {txt_file}")

        return str(txt_file)