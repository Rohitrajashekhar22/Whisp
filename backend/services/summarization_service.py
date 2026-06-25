import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

client = genai.Client()


def summarize_transcript(
    transcript: str,
    content_type: str = "general"
):

    prompt = f"""
You are an AI summarizer.

This transcript may come from:
- meeting recording
- YouTube video
- MP3 audio
- MP4 video
- lecture
- podcast
- interview

Your job is to understand it and return a clean summary.

Content type: {content_type}

Transcript:
{transcript}

Return the output in this exact format:

1. Meeting / Content Summary
- Give a clear simple summary.

2. Key Points
- Highlight the most important points.

3. Action Items / Tasks
- List tasks if any.
- If no tasks, write "No clear action items found."

4. Decisions Made
- List decisions if any.
- If no decisions, write "No clear decisions found."

5. Important Highlights
- Mention important quotes, ideas, warnings, or useful points.
"""

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )

    return response.text


def save_summary(
    summary: str,
    original_file_name: str,
    user_id: int,
    meeting_id: int
):

    # create summaries folder
    summary_dir = f"summaries/user_{user_id}/meeting_{meeting_id}"
    os.makedirs(
        summary_dir,
        exist_ok=True
    )

    # get filename without extension
    file_name = os.path.splitext(
        os.path.basename(original_file_name)
    )[0]

    # create summary file path
    summary_file_path = (
        f"{summary_dir}/{file_name}_summary.txt"
    )

    # save summary
    with open(
        summary_file_path,
        "w",
        encoding="utf-8"
    ) as file:

        file.write(summary)

    return summary_file_path