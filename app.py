import streamlit as st
import sqlite3
import hashlib
import os

st.set_page_config(page_title="YT Summarizer", layout="wide")

# ---------- DATABASE SETUP ----------
DB_PATH = "users.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def create_user(username, email, password):
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute(
            "INSERT INTO users (username, email, password) VALUES (?, ?, ?)",
            (username, email, hash_password(password))
        )
        conn.commit()
        conn.close()
        return True, "Account created successfully!"
    except sqlite3.IntegrityError as e:
        if "username" in str(e):
            return False, "Username already taken."
        return False, "Email already registered."

def verify_user(email, password):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        "SELECT username FROM users WHERE email=? AND password=?",
        (email, hash_password(password))
    )
    row = c.fetchone()
    conn.close()
    return row[0] if row else None

init_db()

# ---------- SESSION STATE ----------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""
if "show_modal" not in st.session_state:
    st.session_state.show_modal = None  # "login" | "signup" | None

# ---------- REDIRECT IF LOGGED IN ----------
if st.session_state.logged_in:
    st.switch_page("pages/main_app.py")

# ---------- GLOBAL CSS ----------
st.markdown("""
<style>
header[data-testid="stHeader"] { display: none; }
#MainMenu { visibility: hidden; }
footer { visibility: hidden; }

.block-container {
    padding-top: 1rem !important;
    max-width: 1100px;
    padding-left: 6rem;
    padding-right: 6rem;
}

.stApp {
    background: linear-gradient(135deg, #e6edff 0%, #f0f4ff 40%, #ffffff 100%);
}

html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

.navbar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 60px;
}

.logo {
    font-size: 20px;
    font-weight: 700;
    background: linear-gradient(90deg, #6366f1, #0ea5e9);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.gradient-text {
    background: linear-gradient(90deg, #6366f1, #0ea5e9);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.hero {
    text-align: center;
    margin-top: 60px;
    margin-bottom: 60px;
}

.hero h1 { font-size: 48px; font-weight: 700; color: #1e293b; }
.hero p  { font-size: 18px; font-weight: 500; color: #5b6b82; margin-top: 15px; }

.stButton > button {
    background: linear-gradient(90deg, #5f5cff, #00bfa6);
    color: white !important;
    border: none;
    border-radius: 12px;
    padding: 12px 26px;
    font-weight: 600;
    font-size: 16px;
    box-shadow: 0 4px 14px rgba(0,198,169,0.3);
}

.stButton > button:hover {
    background: linear-gradient(90deg, #4f46e5, #00a896);
    color: white !important;
}

.card {
    background: #ffffff;
    padding: 25px;
    border-radius: 20px;
    box-shadow: 0 10px 25px rgba(0,0,0,0.05);
    transition: all 0.3s ease;
}
.card:hover { transform: translateY(-5px); box-shadow: 0 15px 35px rgba(0,0,0,0.08); }

.icon-box {
    width: 45px; height: 45px; border-radius: 12px;
    display: flex; align-items: center; justify-content: center;
    font-size: 20px; margin-bottom: 12px;
}
.icon1 { background: #eef2ff; }
.icon2 { background: #ecfeff; }
.icon3 { background: #f5f3ff; }

.card-title { font-size: 16px; font-weight: 600; margin-bottom: 6px; color: #1e293b; }
.card-desc  { font-size: 14px; color: #64748b; line-height: 1.5; }
.features   { margin-top: 40px; }

span, p, div { color: #334155; }
</style>
""", unsafe_allow_html=True)

# ---------- NAVBAR ----------
st.markdown('<div class="navbar"><div class="logo">⚡ YT Summarizer</div></div>',
            unsafe_allow_html=True)

col_nav1, col_nav2, col_nav3 = st.columns([6, 1, 1])
with col_nav2:
    if st.button("Sign in", key="nav_login"):
        st.session_state.show_modal = "login"
        st.rerun()
with col_nav3:
    if st.button("Sign up", key="nav_signup"):
        st.session_state.show_modal = "signup"
        st.rerun()

# ---------- HERO ----------
st.markdown("""
<div class="hero">
    <h1>
        Transform YouTube videos into <br>
        <span class="gradient-text">intelligent summaries</span>
    </h1>
    <p>
        Get AI-powered summaries with topic detection and multi-language support.
    </p>
</div>
""", unsafe_allow_html=True)

c1, c2, c3 = st.columns([3, 2, 3])
with c2:
    if st.button("🚀 Get Started Free", use_container_width=True):
        st.session_state.show_modal = "signup"
        st.rerun()

# ---------- FEATURES ----------
st.markdown('<div class="features">', unsafe_allow_html=True)
col1, col2, col3 = st.columns(3, gap="large")

with col1:
    st.markdown("""<div class="card">
        <div class="icon-box icon1">⚡</div>
        <div class="card-title">AI-Powered Analysis</div>
        <div class="card-desc">Intelligent summarization using Gemini for fast, accurate results.</div>
    </div>""", unsafe_allow_html=True)

with col2:
    st.markdown("""<div class="card">
        <div class="icon-box icon2">🕒</div>
        <div class="card-title">Chapter Detection</div>
        <div class="card-desc">Automatically detect topics with precise timestamps for easy navigation.</div>
    </div>""", unsafe_allow_html=True)

with col3:
    st.markdown("""<div class="card">
        <div class="icon-box icon3">🌍</div>
        <div class="card-title">Multi-Language</div>
        <div class="card-desc">Generate summaries in your preferred language regardless of video language.</div>
    </div>""", unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# ---------- LOGIN MODAL ----------
if st.session_state.show_modal == "login":
    st.divider()
    st.subheader("🔐 Sign In")

    with st.form("login_form"):
        email    = st.text_input("Email")
        password = st.text_input("Password", type="password")
        col_a, col_b = st.columns([1, 1])
        with col_a:
            submitted = st.form_submit_button("Sign In", use_container_width=True)
        with col_b:
            cancelled = st.form_submit_button("Cancel", use_container_width=True)

    if submitted:
        if not email or not password:
            st.error("Please fill in all fields.")
        else:
            username = verify_user(email, password)
            if username:
                st.session_state.logged_in = True
                st.session_state.username  = username
                st.session_state.show_modal = None
                st.success(f"Welcome back, {username}!")
                st.switch_page("pages/main_app.py")
            else:
                st.error("Invalid email or password.")

    if cancelled:
        st.session_state.show_modal = None
        st.rerun()

    st.caption("Don't have an account?")
    if st.button("Create one →"):
        st.session_state.show_modal = "signup"
        st.rerun()

# ---------- SIGNUP MODAL ----------
if st.session_state.show_modal == "signup":
    st.divider()
    st.subheader("✨ Create Account")

    with st.form("signup_form"):
        username = st.text_input("Username")
        email    = st.text_input("Email")
        password = st.text_input("Password", type="password")
        confirm  = st.text_input("Confirm Password", type="password")
        col_a, col_b = st.columns([1, 1])
        with col_a:
            submitted = st.form_submit_button("Create Account", use_container_width=True)
        with col_b:
            cancelled = st.form_submit_button("Cancel", use_container_width=True)

    if submitted:
        if not username or not email or not password or not confirm:
            st.error("Please fill in all fields.")
        elif password != confirm:
            st.error("Passwords do not match.")
        elif len(password) < 6:
            st.error("Password must be at least 6 characters.")
        else:
            success, msg = create_user(username, email, password)
            if success:
                st.success(msg + " Please sign in.")
                st.session_state.show_modal = "login"
                st.rerun()
            else:
                st.error(msg)

    if cancelled:
        st.session_state.show_modal = None
        st.rerun()

    st.caption("Already have an account?")
    if st.button("Sign in →"):
        st.session_state.show_modal = "login"
        st.rerun()