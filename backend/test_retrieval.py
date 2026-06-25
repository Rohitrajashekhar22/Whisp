import os

from dotenv import load_dotenv
from google import genai

from services.retrieval_service import (
    search_transcript
)

load_dotenv()

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)

question = "What happened in the meeting?"

docs = search_transcript(
    4,
    question
)

context = "\n\n".join(
    doc.page_content
    for doc in docs
)

print("\n===== RETRIEVED CHUNKS =====\n")
print(context)

prompt = f"""
Answer ONLY from the meeting context.

If the answer is not present in the context,
say:
'I could not find that information in the meeting.'

Meeting Context:
{context}

Question:
{question}
"""

response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents=prompt
)

print("\n===== AI ANSWER =====\n")
print(response.text)