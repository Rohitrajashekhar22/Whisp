import numpy as np
import sounddevice as sd
import soundfile as sf
from scipy.signal import resample
from dataclasses import dataclass
from typing import Optional


# -----------------------------
# CONFIG
# -----------------------------
SAMPLE_RATE = 16000
CHANNELS = 1


@dataclass
class AudioChunk:
    mic: np.ndarray
    system: np.ndarray


class AudioCaptureService:
    """
    Captures:
    - Microphone audio
    - System audio (loopback)
    Then merges them for transcription pipeline
    """

    def __init__(self):
        self.sample_rate = SAMPLE_RATE

    # -----------------------------
    # MIC RECORDING
    # -----------------------------
    def record_microphone(self, duration: float) -> np.ndarray:
        audio = sd.rec(
            int(duration * self.sample_rate),
            samplerate=self.sample_rate,
            channels=CHANNELS,
            dtype="float32"
        )
        sd.wait()
        return audio.flatten()

    # -----------------------------
    # SYSTEM AUDIO (WINDOWS LOOPBACK)
    # -----------------------------
    def record_system_audio(self, duration: float) -> np.ndarray:
        """
        Captures system audio using WASAPI loopback (Windows only)
        """

        try:
            devices = sd.query_devices()
            default_output = sd.default.device[1]

            audio = sd.rec(
                int(duration * self.sample_rate),
                samplerate=self.sample_rate,
                channels=CHANNELS,
                dtype="float32",
                extra_settings=sd.WasapiSettings(loopback=True),
                device=default_output
            )

            sd.wait()
            return audio.flatten()

        except Exception as e:
            print(f"[WARN] System audio capture failed: {e}")
            return np.zeros(int(duration * self.sample_rate))

    # -----------------------------
    # MERGE AUDIO
    # -----------------------------
    def merge_audio(self, mic: np.ndarray, system: np.ndarray) -> np.ndarray:
        """
        Simple merge strategy:
        - normalize
        - sum signals
        - avoid clipping
        """

        min_len = min(len(mic), len(system))

        mic = mic[:min_len]
        system = system[:min_len]

        mixed = mic + system

        # normalize
        max_val = np.max(np.abs(mixed)) + 1e-6
        mixed = mixed / max_val

        return mixed.astype(np.float32)

    # -----------------------------
    # FULL PIPELINE (MVP MODE)
    # -----------------------------
    def capture_and_merge(self, duration: float = 5.0) -> np.ndarray:
        """
        Captures mic + system audio and returns merged audio
        """

        print("[Audio] Recording microphone...")
        mic = self.record_microphone(duration)

        print("[Audio] Recording system audio...")
        system = self.record_system_audio(duration)

        print("[Audio] Merging streams...")
        return self.merge_audio(mic, system)

    # -----------------------------
    # SAVE TO WAV (FOR WHISPER)
    # -----------------------------
    def save_wav(self, audio: np.ndarray, path: str):
        sf.write(path, audio, self.sample_rate)
        return path