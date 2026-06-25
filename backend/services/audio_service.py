import ffmpeg
import yt_dlp

def convert_mp3_to_wav(input_path, output_path):

    (
        ffmpeg
        .input(input_path)
        .output(output_path)
        .run()
    )
    return output_path


def convert_mp4_to_wav(input_path, output_path):

    (
        ffmpeg
        .input(input_path)
        .output(output_path)
        .run()
    )
    return output_path


def video_to_audio(input_path, output_path):

    (
        ffmpeg
        .input(input_path)
        .output(output_path)
        .run()
    )
    return output_path

def convert_to_wav(input_path, output_path):

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

        .run(overwrite_output=True)
    )

    return output_path

def download_youtube_audio(youtube_url):

    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": "%(title)s.%(ext)s",
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:

        info = ydl.extract_info(youtube_url, download=True)

        downloaded_file = ydl.prepare_filename(info)

    return downloaded_file