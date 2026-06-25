from services.youtube_service import get_youtube_transcript

result = get_youtube_transcript(
    "https://www.youtube.com/watch?v=_iAUVTo49X0"
)

print(result)