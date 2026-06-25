from pathlib import Path

from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma


embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

def search_transcript(
    meeting_id,
    question,
    k=5
):

    db_path = f"vector_db/meeting_{meeting_id}"

    print("=" * 50)
    print("MEETING ID:", meeting_id)
    print("DB PATH:", db_path)
    print("EXISTS:", Path(db_path).exists())
    print("=" * 50)

    if not Path(db_path).exists():
        return []

    vector_store = Chroma(
        persist_directory=db_path,
        embedding_function=embeddings
    )

    results = vector_store.similarity_search(
        question,
        k=k
    )

    print("RESULTS FOUND:", len(results))

    return results
