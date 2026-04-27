"""
utils/transcript.py
-------------------
Responsible for extracting the transcript / captions from a YouTube video.

Three methods are tried in order (fastest → slowest):
  1. youtube-transcript-api  — uses YouTube's own caption data
  2. yt-dlp                  — downloads only the subtitle file, no audio
  3. Gemini Vision           — last resort, uses API quota to watch the video
"""

import re
import os
import json
import glob
import streamlit as st
from youtube_transcript_api import YouTubeTranscriptApi
from google.genai import types
from utils.gemini_client import generate


# ---------- EXTRACT VIDEO ID ----------
def extract_video_id(url: str) -> str:
    """
    Parse a YouTube URL (or bare video ID) and return the 11-character video ID.

    Supports standard watch URLs, shortened youtu.be links, and Shorts.

    Args:
        url: Any valid YouTube URL string.

    Returns:
        The 11-character YouTube video ID.

    Raises:
        Exception: If the URL does not match any known pattern.
    """
    patterns = [
        r"(?:v=|\/)([0-9A-Za-z_-]{11})",
        r"(?:youtu\.be\/)([0-9A-Za-z_-]{11})",
        r"(?:shorts\/)([0-9A-Za-z_-]{11})",
        r"^([0-9A-Za-z_-]{11})$"
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    raise Exception("Invalid YouTube URL. Please check the link and try again.")


# ---------- METHOD 2: yt-dlp CAPTION DOWNLOAD ----------
def _get_captions_ytdlp(url: str):
    """
    Use yt-dlp to download only the subtitle/caption file — no audio, very fast.

    Args:
        url: Full YouTube video URL.

    Returns:
        Plain-text transcript string, or None if captions are unavailable.
    """
    try:
        import yt_dlp

        out_path = "captions_temp"

        # Clean up any leftover files from a previous run
        for f in glob.glob(f"{out_path}.*"):
            os.remove(f)

        ydl_opts = {
            "skip_download":    True,
            "writesubtitles":   True,
            "writeautomaticsub": True,
            "subtitleslangs":   ["en", "en-US", "en-GB", "a.en"],
            "subtitlesformat":  "json3",
            "outtmpl":          out_path,
            "quiet":            True,
            "no_warnings":      True,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        sub_files = glob.glob(f"{out_path}*.json3")
        if not sub_files:
            return None

        with open(sub_files[0], "r", encoding="utf-8") as f:
            data = json.load(f)

        lines = []
        for event in data.get("events", []):
            for seg in event.get("segs", []):
                text = seg.get("utf8", "").strip()
                if text and text != "\n":
                    lines.append(text)

        for f in sub_files:
            os.remove(f)

        transcript = " ".join(lines).strip()
        return transcript if transcript else None

    except Exception:
        return None


# ---------- METHOD 3: GEMINI VISION ----------
def _transcribe_with_gemini(url: str) -> str:
    """
    Ask Gemini to transcribe the video directly (uses API quota).
    Only called when no captions are available anywhere.

    Args:
        url: Full YouTube video URL.

    Returns:
        Raw transcript string from Gemini.

    Raises:
        Exception: If Gemini detects no speech in the video.
    """
    contents = [
        types.Content(
            parts=[
                types.Part(file_data=types.FileData(file_uri=url)),
                types.Part(text=(
                    "Please transcribe all the spoken content from this YouTube video. "
                    "Output only the raw transcript text with no timestamps, speaker labels, "
                    "or formatting. If there is no speech at all, return an empty string."
                ))
            ]
        )
    ]
    text = generate(contents)
    if not text:
        raise Exception("Gemini could not detect any speech in this video.")
    return text


# ---------- PUBLIC ENTRY POINT ----------
def fetch_transcript(video_id: str, url: str) -> str:
    """
    Attempt to retrieve the transcript for a YouTube video using multiple methods.

    Methods tried in order:
      1. youtube-transcript-api (English)
      2. youtube-transcript-api (any available language)
      3. yt-dlp subtitle download
      4. Gemini Vision transcription

    Args:
        video_id : The 11-character YouTube video ID.
        url      : The full YouTube video URL (needed for yt-dlp and Gemini).

    Returns:
        Full transcript text as a single string.
    """
    # --- Method 1: youtube-transcript-api (English) ---
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        text = " ".join([seg["text"] for seg in transcript])
        if text.strip():
            return text
    except Exception:
        pass

    # --- Method 2: youtube-transcript-api (any language) ---
    try:
        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
        for t in transcript_list:
            segs = t.fetch()
            text = " ".join([seg["text"] for seg in segs])
            if text.strip():
                return text
    except Exception:
        pass

    # --- Method 3: yt-dlp subtitle download ---
    st.info("Trying yt-dlp caption extraction...")
    result = _get_captions_ytdlp(url)
    if result:
        return result

    # --- Method 4: Gemini Vision (last resort) ---
    st.warning("No captions found anywhere. Using Gemini vision as last resort...")
    return _transcribe_with_gemini(url)