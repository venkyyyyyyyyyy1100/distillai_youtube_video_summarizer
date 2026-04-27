"""
utils/chat.py
-------------
Allows the user to ask follow-up questions about the
AI-generated summary using Gemini.

The full summary is passed as context with every question
so Gemini always answers based on the video content.
"""

from utils.gemini_client import generate


def ask_question(summary: str, question: str, history: list) -> str:
    """
    Ask a follow-up question about the video summary.

    Args:
        summary  : The full AI-generated summary text.
        question : The user's question string.
        history  : List of past (question, answer) tuples for context.

    Returns:
        Gemini's answer as a plain string.
    """
    # Build conversation history string
    history_text = ""
    for q, a in history[-4:]:   # last 4 exchanges to stay within token limits
        history_text += f"User: {q}\nAssistant: {a}\n\n"

    prompt = f"""You are a helpful assistant. A user has just watched a YouTube video 
and has read the following summary of it. Answer their question based ONLY on the 
information in this summary. Be concise and helpful.

--- VIDEO SUMMARY ---
{summary}
---------------------

{history_text}User: {question}
Assistant:"""

    return generate(prompt)