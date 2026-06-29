import logging
from pathlib import Path

import ffmpeg
import yt_dlp

logger = logging.getLogger(__name__)


# ==========================================================
# INTERNAL HELPER
# ==========================================================

def _convert_to_wav(input_path: str, output_path: str) -> str:

    try:

        Path(output_path).parent.mkdir(
            parents=True,
            exist_ok=True
        )

        (
            ffmpeg
            .input(input_path)
            .output(
                output_path,
                format="wav",
                acodec="pcm_s16le",
                ac=1,
                ar="16000"
            )
            .run(
                overwrite_output=True,
                quiet=True
            )
        )

        logger.info(
            f"Converted {input_path} -> {output_path}"
        )

        return output_path

    except ffmpeg.Error as e:

        logger.exception(
            "FFmpeg conversion failed."
        )

        raise RuntimeError(
            f"Audio conversion failed: {e}"
        )


# ==========================================================
# MP3 -> WAV
# ==========================================================

def convert_mp3_to_wav(
    input_path: str,
    output_path: str
):

    return _convert_to_wav(
        input_path,
        output_path
    )


# ==========================================================
# MP4 -> WAV
# ==========================================================

def convert_mp4_to_wav(
    input_path: str,
    output_path: str
):

    return _convert_to_wav(
        input_path,
        output_path
    )


# ==========================================================
# VIDEO -> AUDIO
# ==========================================================

def video_to_audio(
    input_path: str,
    output_path: str
):

    return _convert_to_wav(
        input_path,
        output_path
    )


# ==========================================================
# GENERIC CONVERSION
# ==========================================================

def convert_to_wav(
    input_path: str,
    output_path: str
):

    return _convert_to_wav(
        input_path,
        output_path
    )


# ==========================================================
# DOWNLOAD YOUTUBE AUDIO
# ==========================================================

def download_youtube_audio(
    youtube_url: str
):

    try:

        download_dir = Path("downloads")

        download_dir.mkdir(
            exist_ok=True
        )

        ydl_opts = {

            "format": "bestaudio/best",

            "outtmpl":
            str(
                download_dir /
                "%(id)s.%(ext)s"
            ),

            "quiet": True,

            "noplaylist": True

        }

        with yt_dlp.YoutubeDL(
            ydl_opts
        ) as ydl:

            info = ydl.extract_info(
                youtube_url,
                download=True
            )

            downloaded_file = ydl.prepare_filename(
                info
            )

        logger.info(
            f"YouTube audio downloaded: {downloaded_file}"
        )

        return downloaded_file

    except Exception as e:

        logger.exception(
            "YouTube download failed."
        )

        raise RuntimeError(
            f"Failed to download YouTube audio: {e}"
        )