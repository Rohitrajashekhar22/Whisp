from google import genai

from services.retrieval_service import search_transcript


client = genai.Client()


def ask_meeting_question(
    meeting_id: int,
    question: str,
) -> str:

    print(f"Searching meeting {meeting_id}")
    print(f"Question: {question}")

    results = search_transcript(
        meeting_id=meeting_id,
        question=question,
        k=5
    )

    print(f"Documents found: {len(results)}")

    if not results:
        return "I could not find anything in this meeting."

    context = "\n\n".join(
        doc.page_content
        for doc in results
    )

    print("\nRetrieved Context:")
    print(context[:1000])

    prompt = f"""
You are an AI meeting assistant.

Summarize the transcript context.

Use only the provided context.

If the transcript is unclear, make the best possible summary from available information.

Do not say you cannot find information unless the context is completely empty.

Transcript Context:
{context}

Question:
{question}
"""

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )

    return response.text