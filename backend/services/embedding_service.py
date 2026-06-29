import logging
import os
import shutil

from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

from services.meeting_service import get_meeting

logger = logging.getLogger(__name__)

# =====================================
# EMBEDDING MODEL
# =====================================

embedding_model = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)


# =====================================
# CREATE EMBEDDINGS
# =====================================

def create_meeting_embeddings(
    meeting_id: int,
    user_id: int
):

    meeting = get_meeting(meeting_id)

    if meeting is None:

        logger.error(
            f"Meeting {meeting_id} not found."
        )

        return False

    if meeting["user_id"] != user_id:

        logger.error(
            "User does not own this meeting."
        )

        return False

    transcript = meeting.get("transcript")

    if not transcript:

        logger.warning(
            f"Meeting {meeting_id} has no transcript."
        )

        return False

    splitter = RecursiveCharacterTextSplitter(

        chunk_size=500,

        chunk_overlap=100

    )

    chunks = splitter.split_text(
        transcript
    )

    if not chunks:

        logger.warning(
            "Transcript produced no chunks."
        )

        return False

    vector_directory = (
        f"vector_db/user_{user_id}/meeting_{meeting_id}"
    )

    os.makedirs(
        os.path.dirname(vector_directory),
        exist_ok=True
    )

    # ---------------------------------
    # Remove previous embeddings
    # ---------------------------------

    if os.path.exists(vector_directory):

        shutil.rmtree(vector_directory)

    vector_store = Chroma(

        persist_directory=vector_directory,

        embedding_function=embedding_model

    )

    metadatas = [

        {

            "meeting_id": meeting_id,

            "user_id": user_id,

            "chunk_index": index

        }

        for index in range(len(chunks))

    ]

    vector_store.add_texts(

        texts=chunks,

        metadatas=metadatas

    )

    logger.info(

        f"Stored {len(chunks)} chunks "

        f"for meeting {meeting_id}"

    )

    return True