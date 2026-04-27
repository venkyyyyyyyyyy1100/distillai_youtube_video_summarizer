"""
utils/summarizer.py
-------------------
Handles all text-processing and AI summarization logic.

Responsibilities:
  - Splitting long transcripts into manageable chunks
  - Building the prompt sent to Gemini
  - Generating and merging chunk-level summaries into one final summary
"""

import streamlit as st
from utils.gemini_client import generate


# ---------- CHUNKING ----------
def chunk_text(text: str, chunk_size: int = 7000, overlap: int = 1000) -> list[str]:
    """
    Split a long transcript into overlapping chunks so that Gemini can
    process each part within its context window.

    Chunks are split at sentence boundaries ('. ', '! ', '? ') where possible
    to avoid cutting a sentence in the middle.

    Args:
        text       : The full transcript string.
        chunk_size : Maximum character length of each chunk.
        overlap    : Number of characters to repeat between consecutive chunks
                     so that context is not lost at boundaries.

    Returns:
        A list of non-empty text chunk strings.
    """
    chunks = []
    start = 0

    while start < len(text):
        end = min(start + chunk_size, len(text))

        # Try to end the chunk at a sentence boundary
        if end < len(text):
            sub = text[max(start, end - 200):end]
            last_dot = max(sub.rfind(". "), sub.rfind("! "), sub.rfind("? "))
            if last_dot != -1:
                end = (end - 200) + last_dot + 2

        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)

        if end >= len(text):
            break

        start = end - overlap
        if start <= 0:
            break

    return chunks


# ---------- PROMPT BUILDER ----------
def create_prompt(text: str) -> str:
    """
    Build the structured summarization prompt that is sent to Gemini.

    The prompt instructs Gemini to return a summary with five clearly
    labelled sections using emoji headers.

    Args:
        text: A single chunk of transcript text.

    Returns:
        The complete prompt string ready to be sent to the Gemini API.
    """
    return f"""Please provide a detailed summary of the following transcript content.

Structure your response as follows:

🎯 TITLE: Create a descriptive title for this content

📝 OVERVIEW (2-3 sentences):
Provide brief context and the main purpose of this video.

🔑 KEY POINTS:
- Extract and explain the main arguments or topics covered
- Include specific examples or data mentioned
- Highlight any unique perspectives or insights

💡 MAIN TAKEAWAYS:
- List 3-5 practical insights from this content
- Explain why each takeaway matters

🔄 CONTEXT & IMPLICATIONS:
- Broader context or background discussed
- Any future implications or next steps mentioned

Transcript:
{text}

Write the summary so that someone who hasn't watched the video gets full value from reading it.
"""


# ---------- SUMMARY GENERATOR ----------
def generate_summary(chunks: list[str]) -> str:
    """
    Generate a complete summary from one or more transcript chunks.

    For multi-chunk transcripts, each chunk is summarised independently
    and then all partial summaries are merged into a single cohesive output.

    Args:
        chunks: List of transcript text chunks produced by chunk_text().

    Returns:
        Final merged summary string.
    """
    summaries = []
    progress = st.progress(0, text="Starting summarization...")

    for i, chunk in enumerate(chunks):
        progress.progress(
            (i + 1) / len(chunks),
            text=f"Summarizing part {i + 1} of {len(chunks)}..."
        )
        result = generate(create_prompt(chunk))
        summaries.append(result)

    progress.empty()

    # If only one chunk, return its summary directly
    if len(summaries) == 1:
        return summaries[0]

    # Merge multiple partial summaries into one
    combined = "\n\n".join(summaries)
    merge_prompt = f"""Below are summaries of different parts of the same video.
Merge them into one single cohesive summary using the same structure:
🎯 TITLE, 📝 OVERVIEW, 🔑 KEY POINTS, 💡 MAIN TAKEAWAYS, 🔄 CONTEXT & IMPLICATIONS.
Remove repetition and make it flow naturally.

{combined}"""

    return generate(merge_prompt)