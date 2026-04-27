"""
utils/thumbnail.py
------------------
Fetches the YouTube video thumbnail URL and title
using the YouTube oEmbed API — no API key needed.
"""

import requests


def get_video_info(video_id: str) -> dict:
    """
    Fetch thumbnail URL and title for a YouTube video.

    Args:
        video_id: The 11-character YouTube video ID.

    Returns:
        Dict with keys: 'thumbnail_url', 'title'.
        Falls back to empty strings on failure.
    """
    try:
        url = f"https://www.youtube.com/oembed?url=https://www.youtube.com/watch?v={video_id}&format=json"
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            return {
                "title":         data.get("title", ""),
                "thumbnail_url": f"https://img.youtube.com/vi/{video_id}/maxresdefault.jpg",
            }
    except Exception:
        pass

    return {"title": "", "thumbnail_url": ""}