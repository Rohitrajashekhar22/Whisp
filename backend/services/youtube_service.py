from youtube_transcript_api import YouTubeTranscriptApi
from urllib.parse import urlparse, parse_qs


def extract_video_id(url):

    try:

        parsed_url = urlparse(url)

        if parsed_url.hostname and "youtube.com" in parsed_url.hostname:
            return parse_qs(
                parsed_url.query
            ).get("v", [None])[0]

        elif parsed_url.hostname and "youtu.be" in parsed_url.hostname:
            return parsed_url.path[1:]

        return None

    except Exception:
        return None


def is_valid_youtube_url(url):
    return extract_video_id(url) is not None


def get_youtube_transcript(url):

    video_id = extract_video_id(url)

    print("VIDEO ID:", video_id)

    if not video_id:
        return {
            "success": False,
            "error": "Invalid YouTube URL"
        }

    try:

        api = YouTubeTranscriptApi()

        transcript_data = api.fetch(video_id)

        transcript_text = " ".join(
            chunk.text
            for chunk in transcript_data
        )

        return {
            "success": True,
            "transcript": transcript_text
        }

    except Exception as e:

        print("TRANSCRIPT ERROR:", str(e))

        return {
            "success": False,
            "error": str(e)
        }