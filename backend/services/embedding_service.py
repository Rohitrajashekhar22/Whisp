from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma

from services.meeting_service import get_live_meeting

embedding_model = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)


def create_meeting_embeddings(meeting_id: int, user_id: int):
    meeting = get_live_meeting(meeting_id)
    if not meeting:
        print("Meeting not found")
        return False

    transcript = meeting.get("transcript")

    if not transcript:
        print("Transcript missing")
        return False

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=100
    )

    chunks = splitter.split_text(transcript)

    if not chunks:
        print("No chunks created")
        return False

    # ✅ THIS IS YOUR VECTOR DB (NO SERVICE, NO PERSIST CALL)
    vector_store = Chroma(
        persist_directory=f"vector_db/meeting_{meeting_id}",
        embedding_function=embedding_model
    )

    metadatas = [
        {
            "meeting_id": meeting_id,
            "chunk_index": i
        }
        for i in range(len(chunks))
    ]

    vector_store.add_texts(
        texts=chunks,
        metadatas=metadatas
    )

    print(f"Stored {len(chunks)} chunks for meeting {meeting_id}")

    return True