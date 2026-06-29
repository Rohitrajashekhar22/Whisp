import logging
from pathlib import Path

from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

from database.db import execute_query

logger = logging.getLogger(__name__)

# =====================================
# EMBEDDING MODEL
# =====================================

embedding_model = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

# =====================================
# ACCESS CHECK (IMPORTANT FIX)
# =====================================

def verify_meeting_access(meeting_id: int, user_id: int):

    meeting = execute_query(
        "SELECT id FROM meetings WHERE id=%s AND user_id=%s",
        (meeting_id, user_id),
        fetchone=True
    )

    return meeting is not None


# =====================================
# SEARCH TRANSCRIPT (RAG CORE)
# =====================================

def search_transcript(
    meeting_id: int,
    user_id: int,
    question: str,
    k: int = 5
):

    # -------------------------------------------------
    # VERIFY ACCESS (SECURE)
    # -------------------------------------------------
    if not verify_meeting_access(meeting_id, user_id):
        logger.error(f"Unauthorized access attempt: user={user_id}, meeting={meeting_id}")
        return []

    # -------------------------------------------------
    # VECTOR DB PATH
    # -------------------------------------------------
    db_path = Path(f"vector_db/user_{user_id}/meeting_{meeting_id}")

    if not db_path.exists():
        logger.warning(f"Vector DB not found: {db_path}")
        return []

    # -------------------------------------------------
    # LOAD VECTOR STORE
    # -------------------------------------------------
    vector_store = Chroma(
        persist_directory=str(db_path),
        embedding_function=embedding_model
    )

    try:
        results = vector_store.similarity_search(
            question,
            k=k
        )

        logger.info(
            f"Retrieved {len(results)} chunks for meeting {meeting_id}"
        )

        return results

    except Exception as e:
        logger.exception(f"Vector search failed: {e}")
        return []