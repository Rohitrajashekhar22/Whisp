from services.retrieval_service import search_transcript

results = search_transcript(
    meeting_id=4,
    question="What was discussed?"
)

print("RESULTS:", len(results))

for r in results:
    print(r.page_content[:300])