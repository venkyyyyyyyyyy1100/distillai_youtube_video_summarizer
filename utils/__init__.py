# utils/__init__.py
# Makes `utils` a proper Python package.
# All public functions are importable directly from `utils`.

from utils.gemini_client import generate
from utils.transcript import extract_video_id, fetch_transcript
from utils.summarizer import chunk_text, generate_summary
from utils.pdf_export import build_pdf
from utils.thumbnail import get_video_info
from utils.chat import ask_question
from utils.quiz import generate_quiz