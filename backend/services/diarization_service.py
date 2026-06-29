import logging
import threading
from typing import List, Dict

from pyannote.audio import Pipeline

logger = logging.getLogger(__name__)


# ==========================================================
# DIARIZATION SERVICE
# ==========================================================

class DiarizationService:
    """
    Speaker diarization using pyannote.audio

    Output:
    [
        {
            "speaker": "SPEAKER_1",
            "start": 0.0,
            "end": 3.2
        }
    ]
    """

    def __init__(self, hf_token: str, model_name: str = "pyannote/speaker-diarization-3.1"):
        self.hf_token = hf_token
        self.model_name = model_name

        self._pipeline = None
        self._lock = threading.Lock()

    # ----------------------------------------------------------
    # LOAD MODEL (LAZY)
    # ----------------------------------------------------------
    def get_pipeline(self):
        if self._pipeline is None:
            with self._lock:
                if self._pipeline is None:
                    logger.info("Loading diarization model...")

                    self._pipeline = Pipeline.from_pretrained(
                        self.model_name,
                        use_auth_token=self.hf_token
                    )

                    logger.info("Diarization model loaded.")

        return self._pipeline

    # ----------------------------------------------------------
    # RUN DIARIZATION
    # ----------------------------------------------------------
    def diarize(self, audio_path: str) -> List[Dict]:
        """
        Run speaker diarization on audio file
        """

        pipeline = self.get_pipeline()

        logger.info(f"Running diarization: {audio_path}")

        try:
            diarization = pipeline(audio_path)

            segments = []

            for turn, _, speaker in diarization.itertracks(yield_label=True):
                segments.append({
                    "speaker": speaker,
                    "start": float(turn.start),
                    "end": float(turn.end)
                })

            logger.info(f"Diarization completed: {len(segments)} segments")

            return segments

        except Exception as e:
            logger.exception("Diarization failed")
            raise RuntimeError(f"Diarization failed: {e}")

    # ----------------------------------------------------------
    # OPTIONAL: NORMALIZE SPEAKER LABELS
    # ----------------------------------------------------------
    def normalize_speakers(self, segments: List[Dict]) -> List[Dict]:
        """
        Converts:
        SPEAKER_00, SPEAKER_01 → Speaker 1, Speaker 2
        """

        mapping = {}
        counter = 1

        normalized = []

        for seg in segments:
            spk = seg["speaker"]

            if spk not in mapping:
                mapping[spk] = f"Speaker {counter}"
                counter += 1

            normalized.append({
                "speaker": mapping[spk],
                "start": seg["start"],
                "end": seg["end"]
            })

        return normalized