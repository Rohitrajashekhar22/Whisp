import os
import queue
import logging
import threading

from services.audio_capture_service import AudioCaptureService
from services.transcription_service import TranscriptionService
from services.live_meeting_service import LiveMeetingService
from services.diarization_service import DiarizationService
from services.merge_service import MergeService

logger = logging.getLogger(__name__)


# =====================================================
# SERVICES
# =====================================================

audio_service = AudioCaptureService()
transcription_service = TranscriptionService()
meeting_service = LiveMeetingService()

# NEW (ADDED FOR SPEAKER SUPPORT)
diarization_service = DiarizationService(hf_token=os.getenv("HF_TOKEN"))
merge_service = MergeService()


# =====================================================
# ACTIVE MEETING STATE
# =====================================================

active_meetings = {}
state_lock = threading.Lock()


# =====================================================
# CREATE STATE
# =====================================================

def create_meeting_state(meeting_id):

    with state_lock:

        if meeting_id in active_meetings:
            return active_meetings[meeting_id]

        state = {
            "queue": queue.Queue(),
            "stop_event": threading.Event(),
            "recorder_thread": None,
            "transcriber_thread": None
        }

        active_meetings[meeting_id] = state

        logger.info(f"Meeting {meeting_id} initialized.")

        return state


# =====================================================
# GET STATE
# =====================================================

def get_meeting_state(meeting_id):
    with state_lock:
        return active_meetings.get(meeting_id)


# =====================================================
# CLEANUP
# =====================================================

def cleanup_meeting(meeting_id):

    with state_lock:
        if meeting_id in active_meetings:
            del active_meetings[meeting_id]
            logger.info(f"Meeting {meeting_id} cleaned up.")


# =====================================================
# RECORDER WORKER (UNCHANGED)
# =====================================================

def recorder_worker(meeting_id, user_id, chunk_duration=5):

    state = get_meeting_state(meeting_id)
    if state is None:
        return

    stop_event = state["stop_event"]
    audio_queue = state["queue"]

    logger.info(f"[Recorder] Started meeting {meeting_id}")

    while not stop_event.is_set():

        try:
            audio = audio_service.capture_and_merge(chunk_duration)

            temp_path = f"temp_{meeting_id}.wav"
            audio_service.save_wav(audio, temp_path)

            audio_queue.put(temp_path)

        except Exception as e:
            logger.exception(f"[Recorder Error] {e}")
            break

    logger.info(f"[Recorder] Stopped meeting {meeting_id}")


# =====================================================
# TRANSCRIPTION WORKER (UPGRADED CORE LOGIC)
# =====================================================

def transcription_worker(meeting_id, user_id):

    state = get_meeting_state(meeting_id)
    if state is None:
        return

    stop_event = state["stop_event"]
    audio_queue = state["queue"]

    logger.info(f"[Transcriber] Started meeting {meeting_id}")

    while True:

        try:
            audio_file = audio_queue.get(timeout=1)

        except queue.Empty:
            if stop_event.is_set():
                break
            continue

        try:
            # ----------------------------------------
            # 1. TRANSCRIBE (WHISPER)
            # ----------------------------------------
            result = transcription_service.transcribe(
                audio_file,
                user_id,
                meeting_id
            )

            whisper_segments = result.get("segments", [])
            text = result.get("text", "")

            # ----------------------------------------
            # 2. DIARIZATION (SPEAKER DETECTION)
            # ----------------------------------------
            diarization_segments = diarization_service.diarize(audio_file)
            diarization_segments = diarization_service.normalize_speakers(diarization_segments)

            # ----------------------------------------
            # 3. MERGE (SPEAKER + TEXT)
            # ----------------------------------------
            merged = merge_service.assign_speakers(
                whisper_segments,
                diarization_segments
            )

            # ----------------------------------------
            # 4. STORE STRUCTURED TRANSCRIPT
            # ----------------------------------------
            if merged:

                meeting_service.append_structured_transcript(
                    meeting_id,
                    merged
                )

            # fallback (raw text)
            elif text:
                meeting_service.append_transcript(
                    meeting_id,
                    text
                )
                asyncio.run(manager.broadcast(meeting_id, { "type": "transcript","text": text
    })
)

            # ----------------------------------------
            # 5. CLEANUP
            # ----------------------------------------
            if audio_file and os.path.exists(audio_file):
                os.remove(audio_file)

        except Exception as e:
            logger.exception(f"[Transcription Error] {e}")

        finally:
            audio_queue.task_done()

    logger.info(f"[Transcriber] Stopped meeting {meeting_id}")


# =====================================================
# START LIVE STREAM (UNCHANGED)
# =====================================================

def start_live_stream(meeting_id, user_id):

    state = create_meeting_state(meeting_id)

    recorder_thread = threading.Thread(
        target=recorder_worker,
        args=(meeting_id, user_id),
        daemon=False
    )

    transcriber_thread = threading.Thread(
        target=transcription_worker,
        args=(meeting_id, user_id),
        daemon=False
    )

    state["recorder_thread"] = recorder_thread
    state["transcriber_thread"] = transcriber_thread

    recorder_thread.start()
    transcriber_thread.start()

    logger.info(f"[Live Stream] Started meeting {meeting_id}")

    recorder_thread.join()

    state["queue"].join()

    state["stop_event"].set()

    transcriber_thread.join()

    cleanup_meeting(meeting_id)

    logger.info(f"[Live Stream] Finished meeting {meeting_id}")


# =====================================================
# STOP MEETING
# =====================================================

def stop_meeting(meeting_id):

    state = get_meeting_state(meeting_id)

    if state is None:
        logger.warning(f"Meeting {meeting_id} not found.")
        return False

    state["stop_event"].set()

    logger.info(f"Stopping meeting {meeting_id}")

    return True


# =====================================================
# STATUS CHECK
# =====================================================

def is_meeting_running(meeting_id):

    state = get_meeting_state(meeting_id)

    if state is None:
        return False

    return not state["stop_event"].is_set()