"""
utils/quiz.py
-------------
Generates a multiple-choice quiz from the AI summary
using Gemini. Returns structured question data that
the UI can render interactively.
"""

import json
from utils.gemini_client import generate


def generate_quiz(summary: str, num_questions: int = 5) -> list[dict]:
    """
    Generate multiple-choice quiz questions from a video summary.

    Args:
        summary       : The full AI-generated summary text.
        num_questions : Number of questions to generate (default 5).

    Returns:
        List of dicts, each with keys:
            - 'question' : Question string
            - 'options'  : List of 4 answer strings (A, B, C, D)
            - 'answer'   : Correct option string (e.g. "A")
            - 'explanation': Brief explanation of the correct answer
    """
    prompt = f"""Based on the following video summary, generate exactly {num_questions} 
multiple-choice quiz questions to test understanding of the content.

Return ONLY a valid JSON array with no extra text, markdown, or explanation.
Each item must have exactly these keys:
  "question"    : the question text
  "options"     : list of exactly 4 strings labelled "A) ...", "B) ...", "C) ...", "D) ..."
  "answer"      : one of "A", "B", "C", or "D"
  "explanation" : one sentence explaining why the answer is correct

VIDEO SUMMARY:
{summary}

JSON array:"""

    raw = generate(prompt)

    # Strip markdown fences if present
    clean = raw.strip()
    if clean.startswith("```"):
        clean = clean.split("```")[1]
        if clean.startswith("json"):
            clean = clean[4:]
    clean = clean.strip()

    try:
        questions = json.loads(clean)
        # Validate structure
        validated = []
        for q in questions:
            if all(k in q for k in ["question", "options", "answer", "explanation"]):
                validated.append(q)
        return validated
    except Exception:
        return []