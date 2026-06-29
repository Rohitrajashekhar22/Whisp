from google import genai
from services.retrieval_service import search_transcript

client = genai.Client()


def ask_meeting_question(meeting_id: int, user_id: int, question: str) -> str:

    # -------------------------------------------------
    # RETRIEVE CONTEXT (USER SCOPED - IMPORTANT)
    # -------------------------------------------------
    results = search_transcript(
        meeting_id=meeting_id,
        user_id=user_id,   # ✅ ADD THIS (IMPORTANT FIX)
        question=question,
        k=5
    )

    if not results:
        return "I could not find relevant information in this meeting."

    # -------------------------------------------------
    # BUILD CONTEXT
    # -------------------------------------------------
    context_chunks = [
        doc.page_content for doc in results if doc.page_content
    ]

    if not context_chunks:
        return "No usable transcript context found."

    context = "\n\n".join(context_chunks)
    context = context[:8000]

    # -------------------------------------------------
    # PROMPT
    # -------------------------------------------------
    prompt = f"""
You are an AI meeting assistant.

Answer ONLY using the provided meeting transcript context.

STRICT RULES:
- Do NOT guess or hallucinate
- If not found, say "Not found in meeting"
- Be concise

CONTEXT:
---------------------
{context}
---------------------

QUESTION:
{question}

ANSWER:
"""

    # -------------------------------------------------
    # GEMINI CALL
    # -------------------------------------------------
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )

    return response.text