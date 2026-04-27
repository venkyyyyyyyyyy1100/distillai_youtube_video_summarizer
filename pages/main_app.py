"""
pages/main_app.py
-----------------
Main YouTube Summarizer UI — shown after login.

Features:
  - Video thumbnail preview       (utils/thumbnail.py)
  - AI summary with PDF download  (utils/summarizer.py, utils/pdf_export.py)
  - Chat with the summary         (utils/chat.py)
  - Quiz generator                (utils/quiz.py)
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import streamlit as st
from utils.transcript import extract_video_id, fetch_transcript
from utils.summarizer import chunk_text, generate_summary
from utils.pdf_export import build_pdf
from utils.thumbnail import get_video_info
from utils.chat import ask_question
from utils.quiz import generate_quiz


# ════════════════════════════════════════════
#  GUARD — redirect if not logged in
# ════════════════════════════════════════════
if not st.session_state.get("logged_in", False):
    st.switch_page("app.py")


# ════════════════════════════════════════════
#  CUSTOM CSS
# ════════════════════════════════════════════
st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600;700&family=DM+Serif+Display:ital@0;1&display=swap');

  .stApp { background: #FDF6EC; font-family: 'DM Sans', sans-serif; }
  #MainMenu, footer, header { visibility: hidden; }
  .block-container { max-width: 760px !important; padding-top: 2rem !important; padding-bottom: 4rem !important; }

  .hero-banner {
      background: linear-gradient(135deg, #FF6B35 0%, #F7931E 50%, #FFD166 100%);
      border-radius: 20px; padding: 2.5rem 2rem 2rem 2rem;
      margin-bottom: 2rem; box-shadow: 0 8px 32px rgba(255,107,53,0.25); text-align: center;
  }
  .hero-banner h1 {
      font-family: 'DM Serif Display', serif; font-size: 2.6rem; color: #fff;
      margin: 0 0 0.4rem 0; letter-spacing: -0.5px; text-shadow: 0 2px 8px rgba(0,0,0,0.12);
  }
  .hero-banner p { color: rgba(255,255,255,0.92); font-size: 1.05rem; margin: 0; }

  label[data-testid="stTextInputLabel"] {
      font-family: 'DM Sans', sans-serif !important; font-weight: 600 !important;
      font-size: 0.95rem !important; color: #3D2B1F !important;
  }
  .stTextInput > div > div > input {
      background: #fff !important; border: 2px solid #E8D5C4 !important;
      border-radius: 12px !important; padding: 0.75rem 1rem !important;
      font-family: 'DM Sans', sans-serif !important; font-size: 0.97rem !important; color: #3D2B1F !important;
  }
  .stTextInput > div > div > input:focus { border-color: #FF6B35 !important; box-shadow: 0 0 0 3px rgba(255,107,53,0.15) !important; }
  .stTextInput > div > div > input::placeholder { color: #B8A090 !important; }

  .stButton > button[kind="primary"] {
      background: linear-gradient(135deg, #FF6B35, #F7931E) !important; color: #fff !important;
      border: none !important; border-radius: 12px !important;
      font-family: 'DM Sans', sans-serif !important; font-weight: 600 !important;
      font-size: 1rem !important; padding: 0.7rem 1.5rem !important;
      box-shadow: 0 4px 16px rgba(255,107,53,0.35) !important;
  }
  .stButton > button[kind="primary"]:hover { transform: translateY(-2px) !important; box-shadow: 0 6px 24px rgba(255,107,53,0.45) !important; }

  .stDownloadButton > button {
      background: #fff !important; color: #FF6B35 !important; border: 2px solid #FF6B35 !important;
      border-radius: 12px !important; font-family: 'DM Sans', sans-serif !important;
      font-weight: 600 !important; font-size: 0.95rem !important; padding: 0.55rem 1.2rem !important;
  }
  .stDownloadButton > button:hover { background: #FF6B35 !important; color: #fff !important; }

  .stAlert { border-radius: 12px !important; font-family: 'DM Sans', sans-serif !important; }

  .summary-card {
      background: #fff; border-radius: 18px; padding: 2rem 2.2rem; margin-top: 1.5rem;
      box-shadow: 0 4px 24px rgba(61,43,31,0.08); border-left: 5px solid #FF6B35;
  }
  hr { border-color: #E8D5C4 !important; }

  .stMarkdown p, .stMarkdown li, .stMarkdown span, .stMarkdown div,
  .stMarkdown h1, .stMarkdown h2, .stMarkdown h3, .stMarkdown h4,
  .stMarkdown strong, .stMarkdown em,
  [data-testid="stMarkdownContainer"] p, [data-testid="stMarkdownContainer"] li,
  [data-testid="stMarkdownContainer"] span, [data-testid="stMarkdownContainer"] div,
  [data-testid="stMarkdownContainer"] h1, [data-testid="stMarkdownContainer"] h2,
  [data-testid="stMarkdownContainer"] h3, [data-testid="stMarkdownContainer"] strong {
      color: #2C1A0E !important; font-family: 'DM Sans', sans-serif !important; line-height: 1.75 !important;
  }

  .how-it-works { display: flex; gap: 1rem; margin-top: 2rem; margin-bottom: 0.5rem; }
  .step-pill {
      background: #fff; border-radius: 14px; padding: 1rem 1.2rem; flex: 1;
      text-align: center; box-shadow: 0 2px 12px rgba(61,43,31,0.07); border: 1.5px solid #F0E2D4;
  }
  .step-pill .icon { font-size: 1.6rem; margin-bottom: 0.4rem; }
  .step-pill .label {
      font-family: 'DM Sans', sans-serif; font-size: 0.82rem; font-weight: 600;
      color: #7A5C48; text-transform: uppercase; letter-spacing: 0.5px;
  }

  /* Thumbnail card */
  .thumb-card {
      background: #fff; border-radius: 16px; overflow: hidden;
      box-shadow: 0 4px 20px rgba(61,43,31,0.10); margin-bottom: 1.5rem;
  }
  .thumb-title {
      font-family: 'DM Sans', sans-serif; font-weight: 600;
      font-size: 1rem; color: #3D2B1F; padding: 0.8rem 1rem 1rem 1rem;
  }

  /* Chat bubble styles */
  .chat-user {
      background: #FF6B35; color: #fff !important; border-radius: 16px 16px 4px 16px;
      padding: 0.7rem 1rem; margin: 0.4rem 0; display: inline-block;
      max-width: 85%; float: right; clear: both; font-family: 'DM Sans', sans-serif;
  }
  .chat-bot {
      background: #fff; color: #2C1A0E !important; border-radius: 16px 16px 16px 4px;
      padding: 0.7rem 1rem; margin: 0.4rem 0; display: inline-block;
      max-width: 85%; float: left; clear: both; font-family: 'DM Sans', sans-serif;
      box-shadow: 0 2px 8px rgba(61,43,31,0.08); border: 1.5px solid #F0E2D4;
  }
  .chat-wrap { overflow: hidden; margin-bottom: 0.5rem; }

  /* Quiz styles */
  .quiz-card {
      background: #fff; border-radius: 14px; padding: 1.2rem 1.5rem; margin-bottom: 1rem;
      box-shadow: 0 2px 12px rgba(61,43,31,0.07); border-left: 4px solid #FF6B35;
  }
  .quiz-q { font-weight: 600; color: #3D2B1F; margin-bottom: 0.5rem; font-family: 'DM Sans', sans-serif; }
  .correct { color: #16a34a !important; font-weight: 600; }
  .wrong   { color: #dc2626 !important; }
  .explanation { color: #7A5C48 !important; font-size: 0.88rem; margin-top: 0.4rem; font-style: italic; }
</style>
""", unsafe_allow_html=True)


# ════════════════════════════════════════════
#  WELCOME BAR + LOGOUT
# ════════════════════════════════════════════
username = st.session_state.get("username", "User")
col_w1, col_w2 = st.columns([6, 1])
with col_w1:
    st.markdown(f'<p style="font-family:DM Sans,sans-serif;color:#7A5C48;font-size:0.9rem;margin:0.5rem 0;">👋 Welcome back, <b style="color:#FF6B35">{username}</b>!</p>', unsafe_allow_html=True)
with col_w2:
    if st.button("Logout"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.switch_page("app.py")


# ════════════════════════════════════════════
#  HERO BANNER
# ════════════════════════════════════════════
st.markdown("""
<div class="hero-banner">
  <h1>🎬 YouTube Summarizer</h1>
  <p>Paste any YouTube link — get a clear, structured AI summary in seconds.</p>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="how-it-works">
  <div class="step-pill"><div class="icon">🔗</div><div class="label">Paste Link</div></div>
  <div class="step-pill"><div class="icon">📄</div><div class="label">Fetch Transcript</div></div>
  <div class="step-pill"><div class="icon">🤖</div><div class="label">AI Summarizes</div></div>
  <div class="step-pill"><div class="icon">⬇️</div><div class="label">Download PDF</div></div>
</div>
""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)


# ════════════════════════════════════════════
#  URL INPUT + GENERATE
# ════════════════════════════════════════════
url = st.text_input("YouTube URL", placeholder="https://www.youtube.com/watch?v=...")

if st.button("✨ Generate Summary", type="primary", use_container_width=True):
    if not url.strip():
        st.warning("Please enter a YouTube URL first.")
    else:
        try:
            with st.spinner("Extracting video ID..."):
                video_id = extract_video_id(url.strip())

            # ── Thumbnail preview ──
            with st.spinner("Fetching video info..."):
                info = get_video_info(video_id)
            if info["thumbnail_url"]:
                st.markdown('<div class="thumb-card">', unsafe_allow_html=True)
                st.image(info["thumbnail_url"], use_container_width=True)
                if info["title"]:
                    st.markdown(f'<div class="thumb-title">🎬 {info["title"]}</div>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)

            with st.spinner("Fetching transcript..."):
                transcript = fetch_transcript(video_id, url.strip())

            st.success(f"✅ Transcript ready — {len(transcript):,} characters")

            with st.spinner("Summarizing with Gemini..."):
                chunks  = chunk_text(transcript)
                summary = generate_summary(chunks)

            # Persist in session
            st.session_state["summary"]    = summary
            st.session_state["url"]        = url.strip()
            st.session_state["video_id"]   = video_id
            st.session_state["chat_history"] = []
            st.session_state["quiz_data"]  = []
            st.session_state["quiz_done"]  = False

        except Exception as e:
            st.error(f"Something went wrong: {str(e)}")


# ════════════════════════════════════════════
#  RESULTS SECTION
# ════════════════════════════════════════════
if "summary" in st.session_state:
    summary    = st.session_state["summary"]
    source_url = st.session_state["url"]

    st.divider()

    # ── PDF Download ──
    pdf_bytes = build_pdf(summary, source_url)
    st.download_button(
        label="⬇️ Download Summary as PDF",
        data=pdf_bytes,
        file_name="youtube_summary.pdf",
        mime="application/pdf",
        use_container_width=True,
    )

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Summary Card ──
    st.markdown('<div class="summary-card">', unsafe_allow_html=True)
    st.markdown(summary)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ════════════════════════════════════════
    #  TABS: Chat + Quiz
    # ════════════════════════════════════════
    tab1, tab2 = st.tabs(["💬 Chat with Summary", "📝 Quiz Me"])

    # ── TAB 1: CHAT ──
    with tab1:
        st.markdown("#### Ask anything about this video")

        # Show history
        for q, a in st.session_state.get("chat_history", []):
            st.markdown(f'<div class="chat-wrap"><div class="chat-user">{q}</div></div>', unsafe_allow_html=True)
            st.markdown(f'<div class="chat-wrap"><div class="chat-bot">{a}</div></div>', unsafe_allow_html=True)

        # Input
        user_q = st.text_input("Your question", placeholder="e.g. What is the main argument?", key="chat_input")
        if st.button("Send 💬", type="primary"):
            if user_q.strip():
                with st.spinner("Thinking..."):
                    answer = ask_question(
                        summary,
                        user_q.strip(),
                        st.session_state.get("chat_history", [])
                    )
                st.session_state["chat_history"].append((user_q.strip(), answer))
                st.rerun()

    # ── TAB 2: QUIZ ──
    with tab2:
        st.markdown("#### Test your understanding!")

        if not st.session_state.get("quiz_data"):
            if st.button("🎯 Generate Quiz", type="primary", use_container_width=True):
                with st.spinner("Generating quiz questions..."):
                    questions = generate_quiz(summary, num_questions=5)
                if questions:
                    st.session_state["quiz_data"]    = questions
                    st.session_state["quiz_answers"] = {}
                    st.session_state["quiz_done"]    = False
                    st.rerun()
                else:
                    st.error("Could not generate quiz. Please try again.")

        else:
            questions = st.session_state["quiz_data"]

            for i, q in enumerate(questions):
                st.markdown(f'<div class="quiz-card"><div class="quiz-q">Q{i+1}. {q["question"]}</div></div>', unsafe_allow_html=True)
                choice = st.radio(
                    f"Q{i+1}",
                    options=q["options"],
                    key=f"quiz_{i}",
                    label_visibility="collapsed"
                )
                st.session_state["quiz_answers"][i] = choice

            if st.button("✅ Submit Quiz", type="primary", use_container_width=True):
                st.session_state["quiz_done"] = True

            if st.session_state.get("quiz_done"):
                st.divider()
                score = 0
                for i, q in enumerate(questions):
                    user_ans   = st.session_state["quiz_answers"].get(i, "")
                    correct_letter = q["answer"]
                    correct_opt    = next((o for o in q["options"] if o.startswith(correct_letter)), "")
                    is_correct     = user_ans == correct_opt
                    if is_correct:
                        score += 1
                    icon = "✅" if is_correct else "❌"
                    st.markdown(f"**{icon} Q{i+1}:** {q['question']}")
                    if not is_correct:
                        st.markdown(f'<span class="wrong">Your answer: {user_ans}</span>', unsafe_allow_html=True)
                    st.markdown(f'<span class="correct">Correct: {correct_opt}</span>', unsafe_allow_html=True)
                    st.markdown(f'<span class="explanation">💡 {q["explanation"]}</span>', unsafe_allow_html=True)
                    st.markdown("---")

                st.success(f"🎉 You scored **{score}/{len(questions)}**!")

                if st.button("🔄 Try Again"):
                    st.session_state["quiz_data"]    = []
                    st.session_state["quiz_answers"] = {}
                    st.session_state["quiz_done"]    = False
                    st.rerun()