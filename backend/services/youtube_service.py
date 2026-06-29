import logging
from urllib.parse import urlparse, parse_qs

from youtube_transcript_api import (
    YouTubeTranscriptApi
)
from youtube_transcript_api._errors import (
    NoTranscriptFound,
    TranscriptsDisabled,
    VideoUnavailable
)

logger = logging.getLogger(__name__)


def extract_video_id(url: str):

    try:

        parsed = urlparse(url)

        if parsed.hostname and "youtube.com" in parsed.hostname:

            return parse_qs(
                parsed.query
            ).get(
                "v",
                [None]
            )[0]

        if parsed.hostname and "youtu.be" in parsed.hostname:

            return parsed.path.lstrip("/")

        return None

    except Exception:

        return None


def is_valid_youtube_url(url: str):

    return extract_video_id(url) is not None


def get_youtube_transcript(url: str):

    video_id = extract_video_id(url)

    if video_id is None:

        return {

            "success": False,

            "error": "Invalid YouTube URL"

        }

    try:

        api = YouTubeTranscriptApi()

        transcript = api.fetch(video_id)

        text = " ".join(

            chunk.text

            for chunk in transcript

        )

        logger.info(
            f"Transcript fetched for {video_id}"
        )

        return {

            "success": True,

            "transcript": text

        }

    except TranscriptsDisabled:

        return {

            "success": False,

            "error": "Transcripts are disabled for this video."

        }

    except NoTranscriptFound:

        return {

            "success": False,

            "error": "No transcript available for this video."

        }

    except VideoUnavailable:

        return {

            "success": False,

            "error": "Video unavailable."

        }

    except Exception as e:

        logger.exception(e)

        return {

            "success": False,

            "error": str(e)

        }