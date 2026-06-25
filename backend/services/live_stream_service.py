import os
import threading
import queue

from services.live_audio_service import (
    record_audio_chunk
)

from services.transcription_service import (
    transcribe_audio
)

from services.meeting_service import (
    append_transcript
)




def recorder_worker(user_id, meeting_id):

    global meeting_stopped

    while not meeting_stopped:

        audio_file = record_audio_chunk(user_id, meeting_id)

        audio_queue.put(audio_file)

    print("Recorder stopped")

def transcription_worker(meeting_id, user_id):

    global meeting_stopped

    while True:

        audio_file = audio_queue.get()

        try:

            transcript = transcribe_audio(
                audio_file,
                user_id,
                meeting_id
            )

            print("\nTranscript:")
            print(transcript)

            append_transcript(
                meeting_id,
                transcript
            )

            if os.path.exists(audio_file):
                os.remove(audio_file)

            print("Audio file deleted")

        except Exception as e:

            print("Transcription Error:", e)

        finally:

            audio_queue.task_done()

        # Exit only after queue is fully processed
        if meeting_stopped and audio_queue.empty():

            print("Meeting processing complete")

            break

def start_live_stream(meeting_id, user_id):

    global meeting_stopped
    meeting_stopped = False

    recorder_thread = threading.Thread(
        target=recorder_worker,
        args=(user_id, meeting_id),
        daemon=True
    )

    transcriber_thread = threading.Thread(
        target=transcription_worker,
        args=(meeting_id, user_id),
        daemon=True
    )

    recorder_thread.start()
    transcriber_thread.start()

    recorder_thread.join()
    transcriber_thread.join()

audio_queue = queue.Queue()

meeting_stopped = False


def stop_meeting():
    global meeting_stopped
    meeting_stopped = True