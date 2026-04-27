"""
utils/gemini_client.py
----------------------
Handles all communication with the Google Gemini API.
Includes retry logic for both rate-limits (429) and
server overload (503), plus automatic model fallback.
"""

import time
import streamlit as st
from google import genai

# ---------- MODEL CONFIG ----------
PRIMARY_MODEL  = "gemini-2.5-flash"
FALLBACK_MODEL = "gemini-2.5-pro"

# Client initialised once using the API key from Streamlit secrets
client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])

# Errors that are worth retrying (temporary server-side issues)
RETRYABLE = ("429", "503", "UNAVAILABLE", "overloaded", "high demand")


def generate_with_retry(model_name: str, contents, retries: int = 4, wait: int = 20) -> str:
    """
    Try to generate a response from a given model.
    Automatically retries on rate-limit (429) AND server overload (503) errors.

    Args:
        model_name : Gemini model identifier string.
        contents   : Prompt content passed to the Gemini API.
        retries    : Maximum number of retry attempts (default 4).
        wait       : Seconds to wait between retries (default 20).

    Returns:
        The generated text response as a stripped string.
    """
    for attempt in range(retries):
        try:
            response = client.models.generate_content(
                model=model_name,
                contents=contents
            )
            return response.text.strip()

        except Exception as e:
            err = str(e)
            is_retryable = any(code in err for code in RETRYABLE)

            if is_retryable and attempt < retries - 1:
                wait_time = wait * (attempt + 1)   # progressive back-off: 20s, 40s, 60s
                st.warning(
                    f"⏳ Gemini is busy (attempt {attempt + 1}/{retries}). "
                    f"Retrying in {wait_time}s..."
                )
                time.sleep(wait_time)
            else:
                raise


def generate(contents) -> str:
    """
    Generate a response using the primary model.
    Falls back to the secondary model if the primary is quota-exhausted or unavailable.

    Args:
        contents: Prompt content passed to the Gemini API.

    Returns:
        The generated text response as a string.
    """
    for model_name in [PRIMARY_MODEL, FALLBACK_MODEL]:
        try:
            return generate_with_retry(model_name, contents)
        except Exception as e:
            err = str(e)
            should_fallback = any(code in err for code in RETRYABLE)
            if should_fallback and model_name == PRIMARY_MODEL:
                st.warning(f"⚠️ {PRIMARY_MODEL} unavailable, switching to {FALLBACK_MODEL}...")
                continue
            raise