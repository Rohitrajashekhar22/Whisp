from fastapi import FastAPI, UploadFile, File, Form
import os
import shutil
from services.embedding_service import create_meeting_embeddings
from services.chat_memory_service import (
    get_meeting_chat_memory
)
app = FastAPI()

from routes.live_meeting_routes import (
    router as live_meeting_router
)

app.include_router(live_meeting_router)


from routes.qa_routes import (
    router as qa_router
)


app.include_router(qa_router)





from services.transcription_service import transcribe_audio
from services.summarization_service import summarize_transcript, save_summary
from services.audio_service import (
    convert_mp3_to_wav,
    convert_mp4_to_wav,
    convert_to_wav,
    download_youtube_audio
)

from services.rag_service import ask_meeting_question

from services.chat_service import save_chat_message

from services.meeting_service import (
    create_meeting,
    get_meeting,
    update_transcript,
    update_summary,
    update_key_points,
    update_tasks,
    update_decisions,
    update_status,
    update_meeting_full
)
from services.chat_memory_service import (
    get_meeting_chat_memory
)

from youtube_transcript_api import YouTubeTranscriptApi
from urllib.parse import urlparse, parse_qs


# =========================
# FOLDERS
# =========================
os.makedirs("uploads", exist_ok=True)
os.makedirs("processed", exist_ok=True)
os.makedirs("summaries", exist_ok=True)

# =========================
# ROUTES
# =========================
from routes.meeting_routes import router as meeting_router
from routes.auth_routes import router as auth_router

app.include_router(meeting_router)
app.include_router(auth_router)

# =========================
# HEALTH CHECK
# =========================
@app.get("/health")
def health():
    return {"status": "running"}


# =========================================================
# FILE UPLOAD → TRANSCRIBE → SUMMARIZE → STORE EMBEDDINGS
# =========================================================
@app.post("/upload-meeting")
async def upload_meeting(
    user_id: int = Form(...),
    title: str = Form(...),
    file: UploadFile = File(...)
):

    # 1. Save file
    file_path = f"uploads/user_{user_id}/meeting_{meeting_id}/{file.filename}"
    
    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    filename = os.path.splitext(file.filename)[0]

    # 2. Create meeting
    meeting_id = create_meeting(
        user_id=user_id,
        title=title,
        source_type="upload",
        source_url=None,
        file_path=file_path
    )

    update_status(meeting_id, "processing")

    # 3. Convert to WAV
    wav_path = f"processed/user_{user_id}/meeting_{meeting_id}/{filename}.wav"
    
    os.makedirs(os.path.dirname(wav_path), exist_ok=True)

    if file.filename.endswith(".mp4"):
        convert_mp4_to_wav(file_path, wav_path)

    elif file.filename.endswith(".mp3"):
        convert_mp3_to_wav(file_path, wav_path)

    elif file.filename.endswith(".wav"):
        wav_path = file_path

    else:
        update_status(meeting_id, "failed")

        return {
            "error": "Only mp3, mp4, wav allowed"
        }

    # 4. Transcribe
    transcript = transcribe_audio(wav_path, user_id, meeting_id)

    update_transcript(
        meeting_id,
        transcript
    )

    # 5. Store embeddings
    create_meeting_embeddings(
    meeting_id=meeting_id,
    )

    # 6. Summarize
    summary = summarize_transcript(transcript)

    update_summary(
        meeting_id,
        summary
    )

    # 7. Save summary file
    save_summary(
        summary,
        file.filename,
        user_id,
        meeting_id
    )

    # 8. Complete
    update_status(
        meeting_id,
        "completed"
    )

    return {
        "message": "Upload processed successfully",
        "meeting_id": meeting_id,
        "transcript": transcript,
        "summary": summary
    }


# =========================================================
# YOUTUBE HELPERS
# =========================================================
def extract_video_id(url):

    try:

        parsed = urlparse(url)

        if "youtube.com" in parsed.hostname:
            return parse_qs(parsed.query)["v"][0]

        elif "youtu.be" in parsed.hostname:
            return parsed.path[1:]

        return None

    except:
        return None


def get_youtube_transcript(url):

    video_id = extract_video_id(url)

    print("VIDEO ID:", video_id)

    if not video_id:
        return None

    try:

        api = YouTubeTranscriptApi()

        transcript_data = api.fetch(video_id)

        transcript_text = " ".join(
            chunk.text
            for chunk in transcript_data
        )

        print(
            "TRANSCRIPT LENGTH:",
            len(transcript_text)
        )

        return transcript_text

    except Exception as e:

        print(
            "YOUTUBE TRANSCRIPT ERROR:",
            str(e)
        )

        return None

# =========================================================
# YOUTUBE → TRANSCRIPT → SUMMARY → EMBEDDINGS
# =========================================================
@app.post("/youtube-meeting")
async def youtube_meeting(
    user_id: int = Form(...),
    title: str = Form(...),
    url: str = Form(...)
):

    # 1. Create meeting
    meeting_id = create_meeting(
        user_id=user_id,
        title=title,
        source_type="youtube",
        source_url=url,
        file_path=None
    )

    update_status(
        meeting_id,
        "processing"
    )

    # 2. Get transcript
    transcript = get_youtube_transcript(url)

    if not transcript:

        update_status(
            meeting_id,
            "failed"
        )

        return {
            "error": "No transcript available"
        }

    update_transcript(
        meeting_id,
        transcript
    )

    # 3. Store embeddings
    create_meeting_embeddings(
        meeting_id=meeting_id,
        user_id=user_id
    )

    # 4. Summarize
    summary = summarize_transcript(
        transcript
    )

    update_summary(
        meeting_id,
        summary
    )

    # 5. Save summary
    save_summary(
        summary,
        title
    )

    # 6. Complete
    update_status(
        meeting_id,
        "completed"
    )

    return {
        "message": "YouTube processed successfully",
        "meeting_id": meeting_id,
        "transcript": transcript,
        "summary": summary
    }


# =========================================================
# CHAT WITH MEETING (RAG)
# =========================================================
@qa_router.post("/meetings/{meeting_id}/chat")
def chat_with_meeting(
    meeting_id:int,
    user_id:int,
    question:str
):

    meeting = get_meeting(meeting_id)

    if not meeting:
        return {
            "error":"Meeting not found"
        }


    transcript = meeting["transcript"]


    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )


    answer = response.text


    save_chat_message(
        meeting_id,
        user_id,
        question,
        answer
    )


    return {
        "answer":answer
    }

#chatmemory
from fastapi import Query

@app.get("/meeting/{meeting_id}/chat-history")
def chat_history(
    meeting_id: int,
    user_id: int = Query(...)
):

    chats = get_meeting_chat_memory(
        meeting_id,
        user_id
    )

    return {
        "meeting_id": meeting_id,
        "messages": chats
    }