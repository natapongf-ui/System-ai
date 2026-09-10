import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import cv2
import time
from datetime import datetime
import numpy as np
import os

# Internal modules
from app.pose.detector import PoseDetector
from app.pose.comparator import PoseComparator, RepCounter
from app.audio.voice_alert import voice_alert

API_URL = "http://localhost:8000/api"

# ---------------------------------------------------------------------------
# Page Configuration
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="AI FIT PRO • ระบบออกกำลังกายอัจฉริยะ",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------------------------------------------------------------------
# Theme: "Cyber Athletic / Neon High-Tech Gym HUD"
# Premium Glassmorphism, Sci-Fi HUD overlays, Google Fonts
# ---------------------------------------------------------------------------
st.markdown("""
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Kanit:ital,wght@0,300;0,400;0,500;0,600;0,700;0,800;1,700&family=Orbitron:wght@500;700;800;900&family=Prompt:wght@300;400;500;600;700&family=IBM+Plex+Sans+Thai:wght@300;400;500;600;700&display=swap" rel="stylesheet">

<style>
    :root {
        --bg-void: #070A12;
        --bg-dark: #0B101D;
        --bg-surface: rgba(15, 23, 42, 0.75);
        --bg-surface-2: rgba(22, 33, 58, 0.85);
        --bg-card: rgba(15, 23, 42, 0.72);
        --bg-card-hover: rgba(26, 39, 68, 0.88);
        
        --neon-lime: #00FF87;
        --neon-cyan: #60EFFF;
        --neon-blue: #00F2FE;
        --neon-purple: #9D4EDD;
        --neon-amber: #FFB703;
        --neon-red: #FF0055;
        
        --text-primary: #F8FAFC;
        --text-secondary: #94A3B8;
        --text-muted: #64748B;
        
        --border-glass: rgba(0, 255, 135, 0.18);
        --border-cyan: rgba(96, 239, 255, 0.22);
        --border-subtle: rgba(148, 163, 184, 0.12);
        
        --glow-lime: 0 0 20px rgba(0, 255, 135, 0.35);
        --glow-cyan: 0 0 20px rgba(96, 239, 255, 0.35);
        --glow-box: 0 8px 32px 0 rgba(0, 0, 0, 0.45);
    }

    html, body, .stApp {
        background-color: var(--bg-void) !important;
        background-image: 
            radial-gradient(circle at 15% 15%, rgba(0, 255, 135, 0.04) 0%, transparent 40%),
            radial-gradient(circle at 85% 85%, rgba(96, 239, 255, 0.04) 0%, transparent 40%),
            linear-gradient(rgba(255, 255, 255, 0.015) 1px, transparent 1px),
            linear-gradient(90deg, rgba(255, 255, 255, 0.015) 1px, transparent 1px) !important;
        background-size: 100% 100%, 100% 100%, 40px 40px, 40px 40px !important;
        color: var(--text-primary) !important;
        font-family: 'Prompt', 'IBM Plex Sans Thai', sans-serif !important;
        -webkit-font-smoothing: antialiased;
    }

    h1, h2, h3, h4, h5, h6 {
        font-family: 'Kanit', sans-serif !important;
        font-weight: 700 !important;
        letter-spacing: 0.03em !important;
        color: var(--text-primary) !important;
    }

    .digital-num {
        font-family: 'Orbitron', monospace !important;
        font-variant-numeric: tabular-nums;
    }

    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #090E1A 0%, #060810 100%) !important;
        border-right: 1px solid var(--border-glass) !important;
        box-shadow: 4px 0 24px rgba(0, 0, 0, 0.5) !important;
    }

    [data-testid="stSidebar"] hr {
        border-color: var(--border-subtle) !important;
        margin: 14px 0 !important;
    }

    .sidebar-brand {
        padding: 14px 8px 10px 8px;
        text-align: center;
        border-bottom: 1px solid var(--border-glass);
        margin-bottom: 14px;
    }
    .sidebar-brand-title {
        font-family: 'Orbitron', sans-serif;
        font-size: 1.45rem;
        font-weight: 900;
        background: linear-gradient(90deg, #00FF87 0%, #60EFFF 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        letter-spacing: 0.08em;
        margin: 0;
    }
    .sidebar-brand-subtitle {
        font-size: 0.72rem;
        color: var(--text-secondary);
        letter-spacing: 0.15em;
        text-transform: uppercase;
        margin-top: 3px;
    }

    .athlete-card {
        background: var(--bg-surface);
        border: 1px solid var(--border-glass);
        border-radius: 12px;
        padding: 12px;
        margin-bottom: 14px;
        backdrop-filter: blur(12px);
        box-shadow: var(--glow-box);
    }
    .athlete-header {
        display: flex;
        align-items: center;
        gap: 10px;
    }
    .athlete-avatar {
        width: 42px;
        height: 42px;
        border-radius: 10px;
        background: linear-gradient(135deg, #00FF87 0%, #00F2FE 100%);
        display: flex;
        align-items: center;
        justify-content: center;
        font-family: 'Orbitron', sans-serif;
        font-weight: 800;
        font-size: 1.05rem;
        color: #070A12;
        box-shadow: var(--glow-lime);
    }
    .athlete-info { flex: 1; }
    .athlete-name {
        font-weight: 700;
        font-size: 0.92rem;
        color: var(--text-primary);
        line-height: 1.2;
    }
    .athlete-tag {
        font-size: 0.72rem;
        color: var(--neon-lime);
        letter-spacing: 0.05em;
        text-transform: uppercase;
    }

    .status-pill {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        background: rgba(0, 255, 135, 0.1);
        border: 1px solid rgba(0, 255, 135, 0.3);
        border-radius: 20px;
        padding: 3px 10px;
        font-size: 0.72rem;
        color: var(--neon-lime);
        font-weight: 600;
    }
    .status-dot {
        width: 7px;
        height: 7px;
        background-color: var(--neon-lime);
        border-radius: 50%;
        box-shadow: 0 0 8px var(--neon-lime);
        animation: pulse-dot 1.8s infinite ease-in-out;
    }
    @keyframes pulse-dot {
        0%, 100% { opacity: 1; transform: scale(1); }
        50% { opacity: 0.4; transform: scale(0.8); }
    }

    .stButton>button {
        background: var(--bg-surface-2) !important;
        color: var(--text-primary) !important;
        border: 1px solid var(--border-glass) !important;
        border-radius: 8px !important;
        padding: 9px 16px !important;
        font-family: 'Kanit', sans-serif !important;
        font-size: 0.92rem !important;
        font-weight: 600 !important;
        transition: all 0.2s ease !important;
        backdrop-filter: blur(8px) !important;
    }
    .stButton>button:hover {
        background: linear-gradient(135deg, rgba(0, 255, 135, 0.25) 0%, rgba(96, 239, 255, 0.25) 100%) !important;
        color: #FFFFFF !important;
        border-color: var(--neon-lime) !important;
        box-shadow: 0 0 16px rgba(0, 255, 135, 0.4) !important;
        transform: translateY(-2px) !important;
    }

    .stFormSubmitButton>button, .stButton>button[kind="primary"] {
        background: linear-gradient(135deg, #00FF87 0%, #00F2FE 100%) !important;
        color: #070A12 !important;
        border: none !important;
        font-weight: 700 !important;
        font-size: 0.98rem !important;
        letter-spacing: 0.04em !important;
        text-transform: uppercase !important;
        box-shadow: 0 0 18px rgba(0, 255, 135, 0.4) !important;
    }
    .stFormSubmitButton>button:hover, .stButton>button[kind="primary"]:hover {
        background: linear-gradient(135deg, #00E676 0%, #60EFFF 100%) !important;
        color: #05070B !important;
        box-shadow: 0 0 24px rgba(0, 255, 135, 0.6) !important;
        transform: translateY(-2px) !important;
    }

    .hud-card {
        background: var(--bg-card);
        border: 1px solid var(--border-glass);
        border-radius: 14px;
        padding: 18px 20px;
        margin-bottom: 18px;
        position: relative;
        overflow: hidden;
        backdrop-filter: blur(16px);
        box-shadow: var(--glow-box);
        transition: all 0.25s ease;
    }
    .hud-card:hover {
        border-color: rgba(0, 255, 135, 0.45);
        box-shadow: 0 10px 30px rgba(0, 255, 135, 0.15);
        transform: translateY(-2px);
    }
    .hud-card::before {
        content: "";
        position: absolute;
        top: 0; left: 0;
        width: 4px; height: 100%;
        background: linear-gradient(180deg, #00FF87 0%, #00F2FE 100%);
    }
    .hud-card.purple::before { background: linear-gradient(180deg, #9D4EDD 0%, #00F2FE 100%); }
    .hud-card.amber::before { background: linear-gradient(180deg, #FFB703 0%, #FF5252 100%); }
    .hud-card.cyan::before { background: linear-gradient(180deg, #60EFFF 0%, #0077B6 100%); }

    .hud-label {
        font-size: 0.78rem;
        color: var(--text-secondary);
        text-transform: uppercase;
        letter-spacing: 0.1em;
        margin-bottom: 4px;
        font-weight: 500;
        display: flex;
        align-items: center;
        gap: 6px;
    }
    .hud-value {
        font-family: 'Orbitron', sans-serif;
        font-size: 2rem;
        font-weight: 800;
        background: linear-gradient(90deg, #FFFFFF 0%, #E2E8F0 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        line-height: 1.1;
    }
    .hud-value.lime {
        background: linear-gradient(90deg, #00FF87 0%, #60EFFF 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .hud-value.amber {
        background: linear-gradient(90deg, #FFB703 0%, #FF5252 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .hud-sub {
        font-size: 0.73rem;
        color: var(--neon-lime);
        margin-top: 5px;
        font-weight: 500;
    }

    .exercise-card {
        background: var(--bg-card);
        border: 1px solid var(--border-glass);
        border-radius: 14px;
        padding: 20px;
        margin-bottom: 18px;
        position: relative;
        overflow: hidden;
        backdrop-filter: blur(14px);
        box-shadow: var(--glow-box);
        transition: all 0.25s ease;
        height: 270px;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
    }
    .exercise-card:hover {
        border-color: var(--neon-lime);
        transform: translateY(-4px);
        box-shadow: 0 12px 36px rgba(0, 255, 135, 0.2);
    }
    .exercise-card-header {
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
        margin-bottom: 8px;
    }
    .exercise-icon-wrap {
        width: 44px;
        height: 44px;
        border-radius: 12px;
        background: rgba(0, 255, 135, 0.12);
        border: 1px solid rgba(0, 255, 135, 0.3);
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.4rem;
    }
    .exercise-title {
        font-family: 'Kanit', sans-serif;
        font-size: 1.2rem;
        font-weight: 700;
        color: #FFFFFF;
        margin: 6px 0 3px 0;
    }
    .exercise-desc {
        font-size: 0.82rem;
        color: var(--text-secondary);
        line-height: 1.4;
        margin-bottom: 10px;
        flex-grow: 1;
    }
    .exercise-tags {
        display: flex;
        flex-wrap: wrap;
        gap: 6px;
        margin-bottom: 10px;
    }
    .badge {
        padding: 3px 8px;
        border-radius: 6px;
        font-size: 0.7rem;
        font-weight: 600;
    }
    .badge-diff-easy {
        background: rgba(0, 255, 135, 0.15);
        color: var(--neon-lime);
        border: 1px solid rgba(0, 255, 135, 0.3);
    }
    .badge-diff-med {
        background: rgba(255, 183, 3, 0.15);
        color: var(--neon-amber);
        border: 1px solid rgba(255, 183, 3, 0.3);
    }
    .badge-diff-hard {
        background: rgba(255, 0, 85, 0.15);
        color: var(--neon-red);
        border: 1px solid rgba(255, 0, 85, 0.3);
    }
    .badge-muscle {
        background: rgba(96, 239, 255, 0.12);
        color: var(--neon-cyan);
        border: 1px solid rgba(96, 239, 255, 0.25);
    }

    .hud-camera-frame {
        border: 2px solid var(--neon-lime);
        border-radius: 14px;
        position: relative;
        overflow: hidden;
        box-shadow: 0 0 25px rgba(0, 255, 135, 0.25);
        background: #000;
    }
    .hud-rep-counter-box {
        background: var(--bg-card);
        border: 1px solid var(--border-glass);
        border-radius: 14px;
        padding: 16px;
        text-align: center;
        backdrop-filter: blur(14px);
        margin-bottom: 12px;
        box-shadow: var(--glow-box);
    }
    .hud-rep-big {
        font-family: 'Orbitron', sans-serif;
        font-size: 3.2rem;
        font-weight: 900;
        background: linear-gradient(90deg, #00FF87 0%, #60EFFF 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        line-height: 1;
        margin: 4px 0;
    }
    .hud-coach-feedback {
        background: rgba(15, 23, 42, 0.9);
        border: 1px solid rgba(255, 183, 3, 0.4);
        border-radius: 10px;
        padding: 10px 14px;
        color: var(--neon-amber);
        font-weight: 600;
        font-size: 0.9rem;
        box-shadow: 0 0 16px rgba(255, 183, 3, 0.2);
    }

    .victory-card {
        background: linear-gradient(145deg, rgba(15, 23, 42, 0.95) 0%, rgba(9, 14, 26, 0.95) 100%);
        border: 2px solid var(--neon-lime);
        border-radius: 18px;
        padding: 26px;
        text-align: center;
        backdrop-filter: blur(20px);
        box-shadow: 0 0 45px rgba(0, 255, 135, 0.35);
        margin: 16px auto;
        max-width: 720px;
    }
    .victory-badge {
        width: 72px;
        height: 72px;
        border-radius: 50%;
        background: linear-gradient(135deg, #00FF87 0%, #00F2FE 100%);
        color: #070A12;
        font-size: 2.2rem;
        display: flex;
        align-items: center;
        justify-content: center;
        margin: 0 auto 12px auto;
        box-shadow: var(--glow-lime);
    }
    .victory-grid {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 12px;
        margin: 20px 0;
    }
    .victory-stat-item {
        background: rgba(255, 255, 255, 0.04);
        border: 1px solid var(--border-glass);
        border-radius: 10px;
        padding: 12px;
    }

    .achievement-card {
        background: var(--bg-card);
        border: 1px solid var(--border-glass);
        border-radius: 12px;
        padding: 14px;
        margin-bottom: 12px;
        display: flex;
        align-items: center;
        gap: 14px;
        transition: all 0.2s ease;
    }
    .achievement-card.locked {
        opacity: 0.55;
        border-color: rgba(148, 163, 184, 0.2);
    }
    .achievement-icon {
        width: 48px;
        height: 48px;
        border-radius: 12px;
        background: rgba(0, 255, 135, 0.15);
        border: 1px solid rgba(0, 255, 135, 0.3);
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.5rem;
    }
    .achievement-card.locked .achievement-icon {
        background: rgba(148, 163, 184, 0.1);
        border-color: rgba(148, 163, 184, 0.2);
    }

    .stTabs [data-baseweb="tab-list"] {
        border-bottom: 1px solid var(--border-glass) !important;
        gap: 10px !important;
    }
    .stTabs [data-baseweb="tab"] {
        background: transparent !important;
        border: none !important;
        color: var(--text-secondary) !important;
        font-family: 'Kanit', sans-serif !important;
        font-size: 0.95rem !important;
        font-weight: 600 !important;
        padding: 8px 16px !important;
    }
    .stTabs [aria-selected="true"] {
        color: var(--neon-lime) !important;
        border-bottom: 2px solid var(--neon-lime) !important;
        background: rgba(0, 255, 135, 0.06) !important;
    }

    .stTextInput input, .stNumberInput input, .stSelectbox div[data-baseweb="select"] {
        background-color: var(--bg-surface-2) !important;
        border: 1px solid var(--border-subtle) !important;
        border-radius: 8px !important;
        color: var(--text-primary) !important;
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Session State Initialization
# ---------------------------------------------------------------------------
if 'token' not in st.session_state:
    st.session_state.token = None
if 'user' not in st.session_state:
    st.session_state.user = None
if 'current_page' not in st.session_state:
    st.session_state.current_page = "เข้าสู่ระบบ"
if 'last_workout_summary' not in st.session_state:
    st.session_state.last_workout_summary = None
if 'selected_category' not in st.session_state:
    st.session_state.selected_category = "ทั้งหมด"
if 'voice_enabled' not in st.session_state:
    st.session_state.voice_enabled = True
if 'target_reps' not in st.session_state:
    st.session_state.target_reps = 15
if 'enable_countdown' not in st.session_state:
    st.session_state.enable_countdown = True

# ---------------------------------------------------------------------------
# Cached API Helper Functions (Performance Boost)
# ---------------------------------------------------------------------------
def api_get(endpoint):
    headers = {"Authorization": f"Bearer {st.session_state.token}"} if st.session_state.token else {}
    try:
        response = requests.get(f"{API_URL}/{endpoint}", headers=headers, timeout=4)
        return response.json() if response.status_code == 200 else None
    except Exception:
        return None

def api_post(endpoint, data):
    headers = {"Authorization": f"Bearer {st.session_state.token}"} if st.session_state.token else {}
    try:
        response = requests.post(f"{API_URL}/{endpoint}", json=data, headers=headers, timeout=4)
        return response
    except Exception:
        return None

def api_put(endpoint, data):
    headers = {"Authorization": f"Bearer {st.session_state.token}"} if st.session_state.token else {}
    try:
        response = requests.put(f"{API_URL}/{endpoint}", json=data, headers=headers, timeout=4)
        return response
    except Exception:
        return None

def api_delete(endpoint):
    headers = {"Authorization": f"Bearer {st.session_state.token}"} if st.session_state.token else {}
    try:
        response = requests.delete(f"{API_URL}/{endpoint}", headers=headers, timeout=4)
        return response
    except Exception:
        return None

@st.cache_data(ttl=60)
def cached_get_exercises():
    try:
        res = requests.get(f"{API_URL}/exercises", timeout=4)
        return res.json() if res.status_code == 200 else []
    except Exception:
        return []

def api_login(username, password):
    try:
        response = requests.post(f"{API_URL}/login", data={"username": username, "password": password}, timeout=4)
        if response.status_code == 200:
            data = response.json()
            st.session_state.token = data["access_token"]
            profile = api_get("profile")
            if profile is None:
                st.session_state.token = None
                st.session_state.user = None
                return False
            st.session_state.user = profile
            return True
        return False
    except Exception:
        return False

# ---------------------------------------------------------------------------
# Health Calculation Helpers (BMR, TDEE, Water)
# ---------------------------------------------------------------------------
def calculate_bmr(weight, height, age, gender):
    # Mifflin-St Jeor Equation
    if gender == "หญิง":
        bmr = (10 * weight) + (6.25 * height) - (5 * age) - 161
    else:
        bmr = (10 * weight) + (6.25 * height) - (5 * age) + 5
    return max(int(bmr), 800)

def calculate_tdee(bmr, activity_level="moderate"):
    multipliers = {
        "sedentary": 1.2,
        "light": 1.375,
        "moderate": 1.55,
        "active": 1.725
    }
    return int(bmr * multipliers.get(activity_level, 1.55))

def calculate_daily_water(weight):
    # Water in liters = weight (kg) * 0.033
    return round(weight * 0.033, 1)

def get_bmi_status(bmi):
    if bmi <= 0:
        return "N/A", "#94A3B8"
    elif bmi < 18.5:
        return "น้ำหนักน้อยกว่าเกณฑ์ (Underweight)", "#60EFFF"
    elif bmi < 23.0:
        return "สมส่วน / เกณฑ์มาตรฐาน (Normal)", "#00FF87"
    elif bmi < 25.0:
        return "น้ำหนักเกิน / ท้วม (Overweight)", "#FFB703"
    else:
        return "ภาวะอ้วน (Obese)", "#FF0055"

def get_exercise_icon(name):
    icons = {
        "squat": "🦵", "pushup": "💪", "situp": "🧘", "plank": "⚡",
        "bicep_curl": "🏋️", "lunge": "🏃", "jumping_jack": "⭐",
        "shoulder_press": "👐", "mountain_climber": "🧗", "burpee": "🔥"
    }
    return icons.get(name.lower(), "💪")

def get_difficulty_badge(diff):
    if "ง่าย" in diff or "easy" in diff.lower():
        return "<span class='badge badge-diff-easy'>🟢 ระดับ: ง่าย</span>"
    elif "ยาก" in diff or "hard" in diff.lower():
        return "<span class='badge badge-diff-hard'>🔴 ระดับ: ยาก</span>"
    else:
        return "<span class='badge badge-diff-med'>🟡 ระดับ: ปานกลาง</span>"

# ---------------------------------------------------------------------------
# PAGE 1: Login & Register
# ---------------------------------------------------------------------------
def page_login_register():
    hero_col, auth_col = st.columns([1.2, 1], gap="large")
    
    with hero_col:
        st.markdown("""
        <div style='padding: 20px 0;'>
            <div class='status-pill' style='margin-bottom: 16px;'>
                <span class='status-dot'></span> AI-POWERED COMPUTER VISION HUD
            </div>
            <h1 style='font-size: 2.8rem; line-height: 1.15; margin-bottom: 12px; background: linear-gradient(90deg, #FFFFFF 0%, #60EFFF 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent;'>
                ระบบออกกำลังกาย<br><span style='background: linear-gradient(90deg, #00FF87 0%, #00F2FE 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent;'>อัจฉริยะแบบ REAL-TIME</span>
            </h1>
            <p style='font-size: 1.02rem; color: #94A3B8; line-height: 1.6; margin-bottom: 24px;'>
                วิเคราะห์โครงกระดูก 33 จุดทั่วร่างกาย ประมวลผลลื่นไหล 60 FPS วัดมุมองศาข้อต่อแม่นยำ พร้อมโค้ชเสียงภาษาไทยแจ้งเตือนและระบบจัดอันดับนักกีฬา
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("""
            <div class='hud-card' style='height: 135px; margin-bottom: 14px;'>
                <div class='hud-label'>⚡ 60 FPS POSE AI</div>
                <div style='font-weight: 700; font-size: 1.05rem; color: #FFF;'>ตรวจจับกระดูก 33 จุด</div>
                <div style='font-size: 0.78rem; color: #94A3B8; margin-top: 3px;'>ประมวลผลเร็วขึ้น 3 เท่าด้วย Low-latency Engine</div>
            </div>
            <div class='hud-card cyan' style='height: 135px;'>
                <div class='hud-label'>🎯 CALIBRATION & GOALS</div>
                <div style='font-weight: 700; font-size: 1.05rem; color: #FFF;'>ตั้งเป้าหมาย & เช็คระยะกล้อง</div>
                <div style='font-size: 0.78rem; color: #94A3B8; margin-top: 3px;'>ระบบวัดระยะและนับถอยหลังก่อนเริ่มฝึก</div>
            </div>
            """, unsafe_allow_html=True)
        with c2:
            st.markdown("""
            <div class='hud-card purple' style='height: 135px; margin-bottom: 14px;'>
                <div class='hud-label'>🔊 THAI VOICE COACH</div>
                <div style='font-weight: 700; font-size: 1.05rem; color: #FFF;'>โค้ชเสียงไทยอัจฉริยะ</div>
                <div style='font-size: 0.78rem; color: #94A3B8; margin-top: 3px;'>แจ้งเตือนทันทีแบบ Non-blocking ไม่ทำให้เฟรมกระตุก</div>
            </div>
            <div class='hud-card amber' style='height: 135px;'>
                <div class='hud-label'>🏆 LEADERBOARD & XP</div>
                <div style='font-weight: 700; font-size: 1.05rem; color: #FFF;'>กระดานอันดับ & เหรียญรางวัล</div>
                <div style='font-size: 0.78rem; color: #94A3B8; margin-top: 3px;'>สะสมเหรียญความสำเร็จและแข่งอันดับกับเพื่อน</div>
            </div>
            """, unsafe_allow_html=True)

    with auth_col:
        st.markdown("""
        <div style='background: var(--bg-card); border: 1px solid var(--border-glass); border-radius: 16px; padding: 22px; backdrop-filter: blur(16px); box-shadow: var(--glow-box); margin-top: 10px;'>
            <div style='text-align: center; margin-bottom: 18px;'>
                <div style='font-size: 2.2rem;'>⚡</div>
                <h3 style='margin: 4px 0 2px 0; font-size: 1.35rem; background: linear-gradient(90deg, #00FF87 0%, #60EFFF 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent;'>ATHLETE PORTAL</h3>
                <div style='font-size: 0.8rem; color: #94A3B8;'>เข้าสู่ระบบเพื่อเริ่มการฝึกซ้อม</div>
            </div>
        """, unsafe_allow_html=True)
        
        tab_login, tab_register = st.tabs(["🔑 เข้าสู่ระบบ", "📝 สมัครสมาชิกใหม่"])
        
        with tab_login:
            with st.form("login_form"):
                username = st.text_input("ชื่อผู้ใช้ (Username)", placeholder="กรอกชื่อผู้ใช้")
                password = st.text_input("รหัสผ่าน (Password)", type="password", placeholder="กรอกรหัสผ่าน")
                submit = st.form_submit_button("🚀 เข้าสู่ระบบ (SIGN IN)", use_container_width=True)
                
                if submit:
                    if not username or not password:
                        st.warning("กรุณากรอกชื่อผู้ใช้และรหัสผ่าน")
                    else:
                        with st.spinner("กำลังตรวจสอบข้อมูล..."):
                            if api_login(username, password):
                                st.success("🎉 เข้าสู่ระบบสำเร็จ ยินดีต้อนรับ!")
                                st.session_state.current_page = "Dashboard"
                                st.rerun()
                            else:
                                st.error("❌ ชื่อผู้ใช้หรือรหัสผ่านไม่ถูกต้อง")
                                
            st.markdown("""
            <div style='margin-top: 12px; padding: 8px 12px; background: rgba(0, 255, 135, 0.06); border: 1px solid rgba(0, 255, 135, 0.2); border-radius: 8px; font-size: 0.76rem; color: #94A3B8;'>
                💡 <b>บัญชีทดสอบด่วน:</b> Username = <code>jimin</code> | Password = <code>123456</code>
            </div>
            """, unsafe_allow_html=True)
            
        with tab_register:
            with st.form("register_form"):
                reg_username = st.text_input("ชื่อผู้ใช้ (Username)*", placeholder="username ภาษาอังกฤษ")
                reg_password = st.text_input("รหัสผ่าน (Password)*", type="password", placeholder="password")
                reg_email = st.text_input("อีเมล (Email)*", placeholder="athlete@email.com")
                reg_name = st.text_input("ชื่อ-นามสกุล (Full Name)*", placeholder="นาย สมชาย มุ่งมั่น")
                
                col_a, col_b = st.columns(2)
                with col_a:
                    reg_age = st.number_input("อายุ (ปี)", min_value=10, max_value=100, value=24)
                    reg_height = st.number_input("ส่วนสูง (ซม.)", min_value=100.0, max_value=230.0, value=175.0, step=0.5)
                with col_b:
                    reg_gender = st.selectbox("เพศ", ["ชาย", "หญิง", "อื่นๆ"])
                    reg_weight = st.number_input("น้ำหนัก (กก.)", min_value=30.0, max_value=250.0, value=68.0, step=0.5)
                    
                reg_submit = st.form_submit_button("✨ สมัครสมาชิก (CREATE ACCOUNT)", use_container_width=True)
                
                if reg_submit:
                    if not reg_username or not reg_password or not reg_email or not reg_name:
                        st.warning("กรุณากรอกข้อมูลให้ครบถ้วน")
                    else:
                        data = {
                            "username": reg_username, "password": reg_password,
                            "email": reg_email, "full_name": reg_name,
                            "age": reg_age, "gender": reg_gender,
                            "height": reg_height, "weight": reg_weight
                        }
                        with st.spinner("กำลังสร้างบัญชี..."):
                            res = api_post("register", data)
                            if res and res.status_code == 200:
                                st.success("🎉 สมัครสมาชิกสำเร็จ! กรุณาเข้าสู่ระบบ")
                            else:
                                err = res.json().get('detail', 'เกิดข้อผิดพลาด') if res else 'เชื่อมต่อไม่สำเร็จ'
                                st.error(f"❌ {err}")
                                
        st.markdown("</div>", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# PAGE 2: Dashboard
# ---------------------------------------------------------------------------
def page_dashboard():
    user = st.session_state.user
    full_name = user.get('full_name', 'Athlete')
    bmi = user.get('bmi', 0)
    bmi_text, bmi_color = get_bmi_status(bmi)
    
    now = datetime.now()
    date_str = now.strftime('%d %B %Y').upper()
    time_str = now.strftime('%H:%M')
    
    head_col1, head_col2 = st.columns([2.2, 1])
    with head_col1:
        st.markdown(f"""
        <div style='margin-bottom: 18px;'>
            <div style='display: flex; align-items: center; gap: 8px; margin-bottom: 4px;'>
                <span class='badge' style='background: rgba(0, 255, 135, 0.15); color: var(--neon-lime); border: 1px solid rgba(0, 255, 135, 0.3); font-family: "Orbitron";'>⚡ ATHLETE COMMAND</span>
                <span style='font-size: 0.8rem; color: #94A3B8;'>{date_str} • {time_str} น.</span>
            </div>
            <h1 style='margin: 0; font-size: 2.2rem;'>ยินดีต้อนรับ, <span style='background: linear-gradient(90deg, #00FF87 0%, #60EFFF 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent;'>{full_name}</span> 👋</h1>
            <p style='color: #94A3B8; font-size: 0.92rem; margin-top: 3px;'>พร้อมสำหรับการฝึกซ้อมวันนี้หรือยัง? เช็คความพร้อมและสถิติของคุณด้านล่าง</p>
        </div>
        """, unsafe_allow_html=True)
    
    with head_col2:
        st.markdown("<div style='text-align: right; margin-top: 8px;'>", unsafe_allow_html=True)
        if st.button("🚀 เริ่มออกกำลังกายทันที", type="primary", use_container_width=True):
            st.session_state.current_page = "เลือกท่าออกกำลังกาย"
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    stats = api_get("statistics")
    today_stats = stats[-1] if stats else {"total_reps": 0, "total_calories": 0, "total_duration": 0, "avg_accuracy": 0}
    
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        reps_today = today_stats.get('total_reps', 0)
        st.markdown(f"""
        <div class='hud-card'>
            <div class='hud-label'>🏋️ จำนวนครั้งสะสมวันนี้</div>
            <div class='hud-value lime digital-num'>{reps_today}</div>
            <div class='hud-sub'>⚡ Reps Completed Today</div>
        </div>
        """, unsafe_allow_html=True)
    with c2:
        duration_mins = today_stats.get('total_duration', 0) // 60
        duration_secs = today_stats.get('total_duration', 0) % 60
        st.markdown(f"""
        <div class='hud-card cyan'>
            <div class='hud-label'>⏱️ เวลาออกกำลังกายรวม</div>
            <div class='hud-value digital-num'>{duration_mins}<span style='font-size: 1.1rem; color: #94A3B8;'>ม. </span>{duration_secs}<span style='font-size: 1.1rem; color: #94A3B8;'>วิ</span></div>
            <div class='hud-sub' style='color: var(--neon-cyan);'>Active Training Time</div>
        </div>
        """, unsafe_allow_html=True)
    with c3:
        cals_today = today_stats.get('total_calories', 0)
        st.markdown(f"""
        <div class='hud-card amber'>
            <div class='hud-label'>🔥 แคลอรี่ที่เผาผลาญ</div>
            <div class='hud-value amber digital-num'>{cals_today:.1f} <span style='font-size: 1rem;'>kcal</span></div>
            <div class='hud-sub' style='color: var(--neon-amber);'>Total Energy Burned</div>
        </div>
        """, unsafe_allow_html=True)
    with c4:
        st.markdown(f"""
        <div class='hud-card purple'>
            <div class='hud-label'>🎯 ค่า BMI สุขภาพของคุณ</div>
            <div class='hud-value digital-num' style='color: {bmi_color};'>{bmi:.1f}</div>
            <div class='hud-sub' style='color: {bmi_color}; font-weight: 600;'>{bmi_text}</div>
        </div>
        """, unsafe_allow_html=True)

    # Charts Section
    st.markdown("<h3 style='margin: 14px 0 10px 0;'>📊 รายงานและการวิเคราะห์พัฒนาการ</h3>", unsafe_allow_html=True)
    if stats and len(stats) > 0:
        df_stats = pd.DataFrame(stats)
        df_stats['date_fmt'] = pd.to_datetime(df_stats['date']).dt.strftime('%d/%m')
        
        col_g1, col_g2 = st.columns(2)
        with col_g1:
            fig_cal = go.Figure()
            fig_cal.add_trace(go.Scatter(
                x=df_stats['date_fmt'], y=df_stats['total_calories'],
                mode='lines+markers', name='Calories (kcal)',
                line=dict(color='#00FF87', width=3, shape='spline'),
                marker=dict(size=8, color='#60EFFF', line=dict(color='#070A12', width=2)),
                fill='tozeroy', fillcolor='rgba(0, 255, 135, 0.08)'
            ))
            fig_cal.update_layout(
                title=dict(text='🔥 พลังงานแคลอรี่ที่เผาผลาญ (รายวัน)', font=dict(family='Kanit', size=15, color='#FFFFFF')),
                plot_bgcolor='rgba(15, 23, 42, 0.5)', paper_bgcolor='rgba(15, 23, 42, 0)',
                font=dict(family='Prompt', color='#94A3B8'),
                xaxis=dict(showgrid=True, gridcolor='rgba(148, 163, 184, 0.1)', title='วันที่'),
                yaxis=dict(showgrid=True, gridcolor='rgba(148, 163, 184, 0.1)', title='แคลอรี่ (kcal)'),
                margin=dict(l=20, r=20, t=40, b=20), height=300
            )
            st.plotly_chart(fig_cal, use_container_width=True)
        with col_g2:
            fig_reps = go.Figure()
            fig_reps.add_trace(go.Bar(
                x=df_stats['date_fmt'], y=df_stats['total_reps'], name='Total Reps',
                marker=dict(color='#60EFFF', line=dict(color='#00FF87', width=1))
            ))
            fig_reps.update_layout(
                title=dict(text='🏋️ จำนวนครั้งที่ทำได้สะสม (รายวัน)', font=dict(family='Kanit', size=15, color='#FFFFFF')),
                plot_bgcolor='rgba(15, 23, 42, 0.5)', paper_bgcolor='rgba(15, 23, 42, 0)',
                font=dict(family='Prompt', color='#94A3B8'),
                xaxis=dict(showgrid=False, title='วันที่'),
                yaxis=dict(showgrid=True, gridcolor='rgba(148, 163, 184, 0.1)', title='จำนวนครั้ง (Reps)'),
                margin=dict(l=20, r=20, t=40, b=20), height=300
            )
            st.plotly_chart(fig_reps, use_container_width=True)
    else:
        st.markdown("""
        <div style='background: var(--bg-card); border: 1px dashed var(--border-glass); border-radius: 12px; padding: 28px 20px; text-align: center; margin: 12px 0;'>
            <div style='font-size: 2rem; margin-bottom: 6px;'>🎯</div>
            <h4 style='color: #FFFFFF; margin-bottom: 2px;'>ยังไม่มีข้อมูลสถิติการออกกำลังกาย</h4>
            <p style='color: #94A3B8; font-size: 0.85rem;'>เริ่มต้นออกกำลังกายรอบแรกวันนี้เพื่อดูสถิติและกราฟพัฒนาการ</p>
        </div>
        """, unsafe_allow_html=True)
        
    st.markdown("<h3 style='margin: 16px 0 12px 0;'>⚡ ท่าออกกำลังกายแนะนำ (Quick Start)</h3>", unsafe_allow_html=True)
    exercises = cached_get_exercises()
    if exercises:
        q_cols = st.columns(min(len(exercises), 4))
        for idx, ex in enumerate(exercises[:4]):
            with q_cols[idx]:
                st.markdown(f"""
                <div style='background: var(--bg-card); border: 1px solid var(--border-glass); border-radius: 12px; padding: 12px; text-align: center; margin-bottom: 8px;'>
                    <div style='font-size: 1.6rem; margin-bottom: 2px;'>{get_exercise_icon(ex["name"])}</div>
                    <div style='font-weight: 700; color: #FFF; font-size: 0.9rem;'>{ex["display_name"]}</div>
                    <div style='font-size: 0.72rem; color: var(--neon-lime); margin-top: 2px;'>{ex["target_muscles"]}</div>
                </div>
                """, unsafe_allow_html=True)
                if st.button(f"เริ่ม {ex['display_name'].split('(')[0]}", key=f"quick_{ex['id']}", use_container_width=True):
                    st.session_state.selected_exercise = ex
                    st.session_state.current_page = "Exercise_Active"
                    st.session_state.last_workout_summary = None
                    st.rerun()

# ---------------------------------------------------------------------------
# PAGE 3: Exercise Selection & Goal Configuration
# ---------------------------------------------------------------------------
def page_exercise_selection():
    st.markdown("""
    <div style='margin-bottom: 16px;'>
        <div style='display: flex; align-items: center; gap: 8px;'>
            <span class='badge' style='background: rgba(0, 255, 135, 0.15); color: var(--neon-lime); border: 1px solid rgba(0, 255, 135, 0.3); font-family: "Orbitron";'>TRAINING CATALOG</span>
        </div>
        <h1 style='margin: 4px 0 4px 0; font-size: 2.2rem;'>เลือกท่าออกกำลังกาย <span style='background: linear-gradient(90deg, #00FF87 0%, #60EFFF 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent;'>AI VISION</span></h1>
        <p style='color: #94A3B8; font-size: 0.92rem;'>กำหนดเป้าหมายจำนวนครั้ง แล้วเริ่มฝึกซ้อมด้วยระบบกล้อง AI ตรวจจับโครงกระดูก</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Workout Pre-Configuration Bar
    with st.expander("⚙️ ตั้งค่าเป้าหมายการฝึกซ้อม (Workout Goals & Options)", expanded=True):
        col_g1, col_g2, col_g3 = st.columns(3)
        with col_g1:
            st.session_state.target_reps = st.selectbox("🎯 เป้าหมายจำนวนครั้ง (Target Reps):", [10, 15, 20, 25, 30, 50, 0], index=1, format_func=lambda x: "ไม่จำกัด (Unlimited)" if x == 0 else f"{x} ครั้ง (Reps)")
        with col_g2:
            st.session_state.voice_enabled = st.toggle("🔊 เปิดโค้ชเสียงภาษาไทย (Voice Alert)", value=st.session_state.voice_enabled)
            voice_alert.set_enabled(st.session_state.voice_enabled)
        with col_g3:
            st.session_state.enable_countdown = st.toggle("⏱️ นับถอยหลัง 3 วินาทีก่อนเริ่ม (3-2-1 Countdown)", value=st.session_state.enable_countdown)

    exercises = cached_get_exercises()
    if not exercises:
        st.warning("⚠️ ไม่สามารถดึงข้อมูลท่าออกกำลังกายได้")
        return
        
    categories = ["ทั้งหมด", "ช่วงล่าง / ขา", "ช่วงบน / แขน", "แกนกลางลำตัว", "คาร์ดิโอ"]
    cat_cols = st.columns(len(categories))
    for i, cat in enumerate(categories):
        with cat_cols[i]:
            if st.button(cat, key=f"cat_{i}", use_container_width=True, type="primary" if st.session_state.selected_category == cat else "secondary"):
                st.session_state.selected_category = cat
                st.rerun()

    filtered_exercises = []
    for ex in exercises:
        muscles = ex.get('target_muscles', '')
        cat = st.session_state.selected_category
        if cat == "ทั้งหมด":
            filtered_exercises.append(ex)
        elif cat == "ช่วงล่าง / ขา" and ("ขา" in muscles or "สะโพก" in muscles or "ก้น" in muscles):
            filtered_exercises.append(ex)
        elif cat == "ช่วงบน / แขน" and ("แขน" in muscles or "อก" in muscles or "ไหล่" in muscles):
            filtered_exercises.append(ex)
        elif cat == "แกนกลางลำตัว" and ("หน้าท้อง" in muscles or "แกนกลาง" in muscles or "หลัง" in muscles):
            filtered_exercises.append(ex)
        elif cat == "คาร์ดิโอ" and ("คาร์ดิโอ" in muscles or "ทั่ว" in muscles or "หัวใจ" in muscles):
            filtered_exercises.append(ex)

    if not filtered_exercises:
        filtered_exercises = exercises

    st.markdown("<div style='margin-top: 14px;'></div>", unsafe_allow_html=True)
    cols = st.columns(3)
    
    for i, ex in enumerate(filtered_exercises):
        with cols[i % 3]:
            icon = get_exercise_icon(ex['name'])
            diff_badge = get_difficulty_badge(ex['difficulty'])
            
            st.markdown(f"""
            <div class='exercise-card'>
                <div>
                    <div class='exercise-card-header'>
                        <div class='exercise-icon-wrap'>{icon}</div>
                        <div>{diff_badge}</div>
                    </div>
                    <div class='exercise-title'>{ex['display_name']}</div>
                    <div class='exercise-desc'>{ex['description']}</div>
                </div>
                <div>
                    <div class='exercise-tags'>
                        <span class='badge badge-muscle'>🎯 {ex['target_muscles']}</span>
                        <span class='badge' style='background: rgba(255, 183, 3, 0.12); color: var(--neon-amber); border: 1px solid rgba(255, 183, 3, 0.25);'>⚡ ~8-12 kcal/นาที</span>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button(f"🚀 เริ่มฝึก {ex['display_name'].split('(')[0]}", key=f"btn_{ex['id']}", type="primary", use_container_width=True):
                st.session_state.selected_exercise = ex
                st.session_state.current_page = "Exercise_Active"
                st.session_state.last_workout_summary = None
                st.rerun()

# ---------------------------------------------------------------------------
# PAGE 4: Live AI Workout Mode (HUD Viewport)
# ---------------------------------------------------------------------------
def page_exercise_active():
    ex = st.session_state.get('selected_exercise')
    if not ex:
        st.session_state.current_page = "เลือกท่าออกกำลังกาย"
        st.rerun()
        
    target_reps = st.session_state.get('target_reps', 15)

    if st.session_state.last_workout_summary:
        summary = st.session_state.last_workout_summary
        st.markdown(f"""
        <div class='victory-card'>
            <div class='victory-badge'>🏆</div>
            <h2 style='font-size: 1.9rem; margin-bottom: 2px; background: linear-gradient(90deg, #00FF87 0%, #60EFFF 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent;'>
                การฝึกซ้อมเสร็จสมบูรณ์!
            </h2>
            <div style='font-size: 1rem; color: #94A3B8;'>{ex['display_name']} • บันทึกสถิติลงในฐานข้อมูลเรียบร้อยแล้ว</div>
            
            <div class='victory-grid'>
                <div class='victory-stat-item'>
                    <div class='hud-label'>🏋️ จำนวนรอบ</div>
                    <div class='hud-value lime digital-num' style='font-size: 1.7rem;'>{summary['reps']}</div>
                    <div style='font-size: 0.72rem; color: #94A3B8;'>ครั้ง (Reps)</div>
                </div>
                <div class='victory-stat-item'>
                    <div class='hud-label'>⏱️ เวลาที่ใช้</div>
                    <div class='hud-value digital-num' style='font-size: 1.7rem;'>{summary['duration']}</div>
                    <div style='font-size: 0.72rem; color: #94A3B8;'>วินาที</div>
                </div>
                <div class='victory-stat-item'>
                    <div class='hud-label'>🔥 เผาผลาญ</div>
                    <div class='hud-value amber digital-num' style='font-size: 1.7rem;'>{summary['calories']:.1f}</div>
                    <div style='font-size: 0.72rem; color: #94A3B8;'>kcal</div>
                </div>
                <div class='victory-stat-item'>
                    <div class='hud-label'>🎯 ความแม่นยำ</div>
                    <div class='hud-value digital-num' style='font-size: 1.7rem; color: var(--neon-cyan);'>{summary['accuracy']:.0f}%</div>
                    <div style='font-size: 0.72rem; color: var(--neon-lime); font-weight: 700;'>GRADE {summary['grade']}</div>
                </div>
            </div>
            
            <p style='color: #60EFFF; font-size: 0.95rem; margin-bottom: 16px;'>✨ ได้รับ +{summary['reps'] * 10 + int(summary['calories'] * 2)} XP พัฒนาการยอดเยี่ยม!</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Rest Interval Timer
        with st.expander("⏱️ พักระหว่างเซ็ต (Rest Interval Timer)", expanded=False):
            st.markdown("<div style='text-align: center;'>เลือกเวลาพักฟื้นกล้ามเนื้อก่อนเริ่มเซ็ตถัดไป</div>", unsafe_allow_html=True)
            col_r1, col_r2 = st.columns(2)
            with col_r1:
                if st.button("⏱️ พัก 30 วินาที", use_container_width=True):
                    progress_bar = st.progress(0)
                    for sec in range(30, 0, -1):
                        progress_bar.progress((30 - sec) / 30, text=f"กำลังพัก: {sec} วินาที...")
                        time.sleep(1)
                    progress_bar.empty()
                    st.success("🔔 หมดเวลาพัก พร้อมเริ่มเซ็ตต่อไป!")
            with col_r2:
                if st.button("⏱️ พัก 60 วินาที", use_container_width=True):
                    progress_bar = st.progress(0)
                    for sec in range(60, 0, -1):
                        progress_bar.progress((60 - sec) / 60, text=f"กำลังพัก: {sec} วินาที...")
                        time.sleep(1)
                    progress_bar.empty()
                    st.success("🔔 หมดเวลาพัก พร้อมเริ่มเซ็ตต่อไป!")

        c_btn1, c_btn2 = st.columns(2)
        with c_btn1:
            if st.button("📊 ไปที่แดชบอร์ดดูสถิติรวม", type="primary", use_container_width=True):
                st.session_state.last_workout_summary = None
                st.session_state.current_page = "Dashboard"
                st.rerun()
        with c_btn2:
            if st.button("🔄 ออกกำลังกายต่อ / เลือกท่าอื่น", use_container_width=True):
                st.session_state.last_workout_summary = None
                st.session_state.current_page = "เลือกท่าออกกำลังกาย"
                st.rerun()
        return

    # Active Workout Top Header
    st.markdown(f"""
    <div style='display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;'>
        <div>
            <div style='display: flex; align-items: center; gap: 8px;'>
                <span class='status-pill'><span class='status-dot'></span> LIVE AI SKELETON HUD</span>
                <span style='font-size: 0.82rem; color: #94A3B8;'>เป้าหมาย: {ex['target_muscles']}</span>
            </div>
            <h2 style='margin: 3px 0 0 0;'>🔴 กำลังฝึก: <span style='color: var(--neon-lime);'>{ex['display_name']}</span></h2>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    view_col, hud_col = st.columns([2.6, 1.4], gap="medium")
    
    with view_col:
        st.markdown("<div class='hud-camera-frame'>", unsafe_allow_html=True)
        stframe = st.empty()
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Real-time Calibration & Positioning Tag
        calib_placeholder = st.empty()
        
    with hud_col:
        # Rep Counter HUD Box
        st.markdown("<div class='hud-rep-counter-box'>", unsafe_allow_html=True)
        st.markdown("<div class='hud-label' style='justify-content: center;'>🏋️ จำนวนครั้ง (REPS COUNT)</div>", unsafe_allow_html=True)
        rep_hud = st.empty()
        state_hud = st.empty()
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Target Goal Progress Bar
        goal_hud = st.empty()
        
        # Accuracy & Metrics HUD Box
        st.markdown("<div class='hud-card' style='padding: 14px; margin-bottom: 12px;'>", unsafe_allow_html=True)
        acc_hud = st.empty()
        time_hud = st.empty()
        cal_hud = st.empty()
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Real-time Voice / Text Coach Banner
        coach_hud = st.empty()
        
        st.markdown("<div style='margin-top: 14px;'></div>", unsafe_allow_html=True)
        stop_btn = st.button("⏹️ จบเซสชันและบันทึกผล", type="primary", use_container_width=True)

    # Initializing high-speed Pose Detector (model_complexity=0)
    cap = cv2.VideoCapture(0)
    # Set webcam resolution to 640x480 for ultra-fast processing
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    
    detector = PoseDetector(model_complexity=0)
    comparator = PoseComparator()
    counter = RepCounter(ex['name'])
    
    ref_angles = {'left_elbow': 170, 'left_knee': 170, 'left_hip': 170}

    start_time = time.time()
    acc_history = []
    final_count = 0
    final_duration = 0
    final_calories = 0.0

    try:
        while cap.isOpened():
            if stop_btn:
                break
                
            success, img = cap.read()
            if not success:
                st.error("⚠️ ไม่สามารถเปิดกล้อง Webcam ได้")
                break
                
            img = cv2.flip(img, 1)
            
            # Detect Pose
            img = detector.find_pose(img, draw=False)
            lm_list = detector.get_position(img, draw=False)
            
            current_acc = 0.0
            feedback_text = ""
            current_state = "UP"
            
            if len(lm_list) != 0:
                # Body position & distance calibration check
                is_good, pos_msg, _ = detector.check_body_visibility(lm_list, img.shape)
                if is_good:
                    calib_placeholder.markdown(f"<div style='color: var(--neon-lime); font-size: 0.78rem; padding: 4px 8px;'>{pos_msg}</div>", unsafe_allow_html=True)
                else:
                    calib_placeholder.markdown(f"<div style='color: var(--neon-amber); font-size: 0.78rem; padding: 4px 8px;'>{pos_msg}</div>", unsafe_allow_html=True)

                angles = detector.get_joint_angles(lm_list)
                current_acc, feedback = comparator.compare_pose(angles, ref_angles)
                acc_history.append(current_acc)
                
                # Dynamic Skeleton Color based on Accuracy
                if current_acc > 75:
                    bone_color = (0, 255, 135)
                    joint_color = (96, 239, 255)
                elif current_acc > 50:
                    bone_color = (3, 183, 255)
                    joint_color = (255, 255, 255)
                else:
                    bone_color = (85, 0, 255)
                    joint_color = (0, 0, 255)
                    
                detector.mp_draw.draw_landmarks(
                    img, detector.results.pose_landmarks, detector.mp_pose.POSE_CONNECTIONS,
                    detector.mp_draw.DrawingSpec(color=joint_color, thickness=2, circle_radius=2),
                    detector.mp_draw.DrawingSpec(color=bone_color, thickness=2, circle_radius=2)
                )
                
                if feedback:
                    feedback_text = feedback[0]
                    
                count, current_state, rep_feedback = counter.update(angles, current_acc)
                if rep_feedback:
                    feedback_text = rep_feedback
            else:
                count = counter.count
                calib_placeholder.markdown("<div style='color: var(--neon-red); font-size: 0.78rem; padding: 4px 8px;'>❌ ไม่พบผู้ใช้งานในเฟรมกล้อง</div>", unsafe_allow_html=True)
                
            final_count = count
            final_duration = int(time.time() - start_time)
            final_calories = (final_duration * 0.06) + (final_count * 0.45)
            
            mins = final_duration // 60
            secs = final_duration % 60
            time_str = f"{mins:02d}:{secs:02d}"
            
            img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            stframe.image(img_rgb, channels="RGB", use_container_width=True)
            
            rep_hud.markdown(f"<div class='hud-rep-big'>{count:02d}</div>", unsafe_allow_html=True)
            state_hud.markdown(f"<span class='badge' style='background: rgba(0, 255, 135, 0.15); color: var(--neon-lime); font-family: Orbitron; font-size: 0.78rem;'>STATE: [{current_state}]</span>", unsafe_allow_html=True)
            
            # Goal Progress Display
            if target_reps > 0:
                pct = min(int((count / target_reps) * 100), 100)
                goal_hud.markdown(f"""
                <div style='margin-bottom: 10px;'>
                    <div style='display: flex; justify-content: space-between; font-size: 0.78rem; margin-bottom: 3px;'>
                        <span style='color: #94A3B8;'>เป้าหมาย: {count}/{target_reps} ครั้ง</span>
                        <span style='color: var(--neon-lime); font-weight: 700;'>{pct}%</span>
                    </div>
                    <div style='background: rgba(255,255,255,0.1); border-radius: 6px; height: 6px; overflow: hidden;'>
                        <div style='background: linear-gradient(90deg, #00FF87, #60EFFF); width: {pct}%; height: 100%;'></div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                if count >= target_reps and target_reps > 0:
                    coach_hud.markdown("<div class='hud-coach-feedback' style='background: rgba(0,255,135,0.2); border-color: var(--neon-lime); color: var(--neon-lime);'>🏆 ครบตามเป้าหมายแล้ว! ยอดเยี่ยมมาก!</div>", unsafe_allow_html=True)
            else:
                goal_hud.empty()
            
            acc_color = "var(--neon-lime)" if current_acc > 75 else ("var(--neon-amber)" if current_acc > 50 else "var(--neon-red)")
            acc_hud.markdown(f"<div style='display: flex; justify-content: space-between; margin-bottom: 4px;'><span style='font-size: 0.82rem; color: #94A3B8;'>🎯 ความแม่นยำ:</span><span class='digital-num' style='color: {acc_color}; font-weight: 800;'>{current_acc:.1f}%</span></div>", unsafe_allow_html=True)
            time_hud.markdown(f"<div style='display: flex; justify-content: space-between; margin-bottom: 4px;'><span style='font-size: 0.82rem; color: #94A3B8;'>⏱️ เวลาฝึกซ้อม:</span><span class='digital-num' style='color: #FFFFFF; font-weight: 700;'>{time_str}</span></div>", unsafe_allow_html=True)
            cal_hud.markdown(f"<div style='display: flex; justify-content: space-between;'><span style='font-size: 0.82rem; color: #94A3B8;'>🔥 แคลอรี่:</span><span class='digital-num' style='color: var(--neon-amber); font-weight: 700;'>{final_calories:.1f} kcal</span></div>", unsafe_allow_html=True)
            
            if feedback_text:
                coach_hud.markdown(f"<div class='hud-coach-feedback'>💬 {feedback_text}</div>", unsafe_allow_html=True)
            else:
                coach_hud.markdown("<div class='hud-coach-feedback' style='border-color: rgba(0, 255, 135, 0.3); color: var(--neon-lime);'>✨ ท่าทางถูกต้อง รักษาฟอร์มไว้!</div>", unsafe_allow_html=True)
                
            time.sleep(0.015)
    finally:
        cap.release()
    
    avg_acc = float(np.mean(acc_history)) if acc_history else 85.0
    grade = "S" if avg_acc >= 90 else ("A" if avg_acc >= 75 else ("B" if avg_acc >= 60 else "C"))
    
    history_payload = {
        "exercise_id": ex['id'],
        "reps": final_count,
        "duration": max(final_duration, 1),
        "calories": round(final_calories, 2),
        "accuracy": round(avg_acc, 2)
    }
    
    api_post("history", history_payload)
    
    st.session_state.last_workout_summary = {
        "reps": final_count,
        "duration": final_duration,
        "calories": final_calories,
        "accuracy": avg_acc,
        "grade": grade
    }
    st.rerun()

# ---------------------------------------------------------------------------
# PAGE 5: Exercise History & Analytics
# ---------------------------------------------------------------------------
def page_history():
    st.markdown("""
    <div style='margin-bottom: 16px;'>
        <div style='display: flex; align-items: center; gap: 8px;'>
            <span class='badge' style='background: rgba(0, 255, 135, 0.15); color: var(--neon-lime); border: 1px solid rgba(0, 255, 135, 0.3); font-family: "Orbitron";'>WORKOUT LOGS</span>
        </div>
        <h1 style='margin: 4px 0 4px 0; font-size: 2.2rem;'>ประวัติการออกกำลังกาย <span style='background: linear-gradient(90deg, #00FF87 0%, #60EFFF 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent;'>& ANALYTICS</span></h1>
        <p style='color: #94A3B8; font-size: 0.92rem;'>บันทึกประวัติการฝึกซ้อมทั้งหมด ข้อมูลจำนวนรอบ แคลอรี่ที่เผาผลาญ และคะแนนความแม่นยำ</p>
    </div>
    """, unsafe_allow_html=True)
    
    histories = api_get("history")
    if not histories or len(histories) == 0:
        st.markdown("""
        <div style='background: var(--bg-card); border: 1px dashed var(--border-glass); border-radius: 14px; padding: 40px 20px; text-align: center;'>
            <div style='font-size: 2.5rem; margin-bottom: 10px;'>📅</div>
            <h3 style='color: #FFFFFF; margin-bottom: 4px;'>ยังไม่มีประวัติการออกกำลังกาย</h3>
            <p style='color: #94A3B8; font-size: 0.9rem; margin-bottom: 16px;'>เริ่มต้นการฝึกซ้อมแรกของคุณเพื่อบันทึกประวัติและสถิติ</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("💪 เริ่มออกกำลังกายตอนนี้", type="primary"):
            st.session_state.current_page = "เลือกท่าออกกำลังกาย"
            st.rerun()
        return
        
    df = pd.DataFrame(histories)
    
    total_sessions = len(df)
    total_reps_all = df['reps'].sum() if 'reps' in df.columns else 0
    total_cals_all = df['calories'].sum() if 'calories' in df.columns else 0.0
    best_acc = df['accuracy'].max() if 'accuracy' in df.columns else 0.0
    
    k1, k2, k3, k4 = st.columns(4)
    with k1:
        st.markdown(f"""
        <div class='hud-card'>
            <div class='hud-label'>🏆 เซสชันทั้งหมด</div>
            <div class='hud-value lime digital-num'>{total_sessions}</div>
            <div class='hud-sub'>Total Workouts Logged</div>
        </div>
        """, unsafe_allow_html=True)
    with k2:
        st.markdown(f"""
        <div class='hud-card cyan'>
            <div class='hud-label'>🏋️ จำนวนรอบสะสม</div>
            <div class='hud-value digital-num'>{total_reps_all}</div>
            <div class='hud-sub' style='color: var(--neon-cyan);'>Lifetime Total Reps</div>
        </div>
        """, unsafe_allow_html=True)
    with k3:
        st.markdown(f"""
        <div class='hud-card amber'>
            <div class='hud-label'>🔥 แคลอรี่เผาผลาญรวม</div>
            <div class='hud-value amber digital-num'>{total_cals_all:.1f}</div>
            <div class='hud-sub' style='color: var(--neon-amber);'>Total kcal Burned</div>
        </div>
        """, unsafe_allow_html=True)
    with k4:
        st.markdown(f"""
        <div class='hud-card purple'>
            <div class='hud-label'>🎯 ความแม่นยำสูงสุด</div>
            <div class='hud-value digital-num' style='color: #60EFFF;'>{best_acc:.1f}%</div>
            <div class='hud-sub' style='color: var(--neon-purple);'>Personal Best Accuracy</div>
        </div>
        """, unsafe_allow_html=True)

    df['date_fmt'] = pd.to_datetime(df['date']).dt.strftime('%d/%m/%Y %H:%M')
    display_df = df[['date_fmt', 'exercise_name', 'reps', 'duration', 'calories', 'accuracy']].copy()
    display_df.columns = ['วันที่/เวลา', 'ชื่อท่าออกกำลังกาย', 'จำนวนรอบ (ครั้ง)', 'ระยะเวลา (วินาที)', 'แคลอรี่ (kcal)', 'ความแม่นยำ (%)']
    
    st.markdown("<h3 style='margin: 16px 0 10px 0;'>📋 ตารางบันทึกกิจกรรมย้อนหลัง</h3>", unsafe_allow_html=True)
    st.dataframe(display_df, use_container_width=True, height=340)
    
    col_exp1, col_exp2 = st.columns([1, 3])
    with col_exp1:
        csv_data = display_df.to_csv(index=False).encode('utf-8-sig')
        st.download_button(
            label="📥 ดาวน์โหลดประวัติ (CSV)",
            data=csv_data,
            file_name=f"ai_exercise_history_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv",
            use_container_width=True
        )

# ---------------------------------------------------------------------------
# PAGE 6: Leaderboard & Achievements
# ---------------------------------------------------------------------------
def page_leaderboard_achievements():
    st.markdown("""
    <div style='margin-bottom: 16px;'>
        <div style='display: flex; align-items: center; gap: 8px;'>
            <span class='badge' style='background: rgba(0, 255, 135, 0.15); color: var(--neon-lime); border: 1px solid rgba(0, 255, 135, 0.3); font-family: "Orbitron";'>COMMUNITY & RANKS</span>
        </div>
        <h1 style='margin: 4px 0 4px 0; font-size: 2.2rem;'>กระดานจัดอันดับ <span style='background: linear-gradient(90deg, #00FF87 0%, #60EFFF 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent;'>& ความสำเร็จ</span></h1>
        <p style='color: #94A3B8; font-size: 0.92rem;'>ติดตามอันดับนักกีฬาและปลดล็อกเหรียญตราความสำเร็จจากการฝึกซ้อม</p>
    </div>
    """, unsafe_allow_html=True)
    
    tab_rank, tab_badge = st.tabs(["🏆 กระดานจัดอันดับ (Leaderboard)", "🎖️ เหรียญรางวัลความสำเร็จ (Achievements)"])
    
    with tab_rank:
        leaderboard = api_get("leaderboard")
        if leaderboard:
            df_lead = pd.DataFrame(leaderboard)
            df_lead['medal'] = df_lead['rank'].apply(lambda r: "🥇" if r == 1 else ("🥈" if r == 2 else ("🥉" if r == 3 else f"#{r}")))
            display_lead = df_lead[['medal', 'full_name', 'username', 'total_reps', 'total_calories', 'total_workouts', 'avg_accuracy']].copy()
            display_lead.columns = ['อันดับ', 'ชื่อนักกีฬา', 'Username', 'จำนวนครั้งสะสม', 'แคลอรี่รวม (kcal)', 'เซสชันทั้งหมด', 'ความแม่นยำเฉลี่ย (%)']
            st.dataframe(display_lead, use_container_width=True, height=360)
        else:
            st.info("ยังไม่มีข้อมูลในกระดานอันดับ")
            
    with tab_badge:
        badges = api_get("achievements")
        if badges:
            b_cols = st.columns(2)
            for i, badge in enumerate(badges):
                with b_cols[i % 2]:
                    locked_cls = "" if badge['unlocked'] else "locked"
                    status_str = "🟢 ปลดล็อกแล้ว!" if badge['unlocked'] else f"🔒 ความคืบหน้า: {badge['progress']}/{badge['target']}"
                    pct = min(int((badge['progress'] / badge['target']) * 100), 100) if badge['target'] > 0 else 0
                    
                    st.markdown(f"""
                    <div class='achievement-card {locked_cls}'>
                        <div class='achievement-icon'>{badge['title'].split()[0]}</div>
                        <div style='flex: 1;'>
                            <div style='font-weight: 700; font-size: 1rem; color: #FFF;'>{badge['title']}</div>
                            <div style='font-size: 0.8rem; color: #94A3B8;'>{badge['description']}</div>
                            <div style='margin-top: 6px;'>
                                <div style='font-size: 0.72rem; color: var(--neon-lime); margin-bottom: 2px;'>{status_str}</div>
                                <div style='background: rgba(255,255,255,0.1); border-radius: 4px; height: 5px; overflow: hidden;'>
                                    <div style='background: linear-gradient(90deg, #00FF87, #60EFFF); width: {pct}%; height: 100%;'></div>
                                </div>
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# PAGE 7: Athlete Profile & Health Calculator
# ---------------------------------------------------------------------------
def page_profile():
    user = st.session_state.user
    if not user:
        return
        
    st.markdown("""
    <div style='margin-bottom: 16px;'>
        <div style='display: flex; align-items: center; gap: 8px;'>
            <span class='badge' style='background: rgba(0, 255, 135, 0.15); color: var(--neon-lime); border: 1px solid rgba(0, 255, 135, 0.3); font-family: "Orbitron";'>ATHLETE PROFILE</span>
        </div>
        <h1 style='margin: 4px 0 4px 0; font-size: 2.2rem;'>ข้อมูลส่วนตัว <span style='background: linear-gradient(90deg, #00FF87 0%, #60EFFF 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent;'>& สุขภาพอัจฉริยะ</span></h1>
        <p style='color: #94A3B8; font-size: 0.92rem;'>คำนวณอัตราการเผาผลาญพลังงาน (BMR / TDEE) และปริมาณน้ำที่แนะนำต่อวัน</p>
    </div>
    """, unsafe_allow_html=True)
    
    col_p1, col_p2 = st.columns([1.2, 1], gap="large")
    
    with col_p1:
        st.markdown("### 📝 แก้ไขข้อมูลส่วนตัว")
        with st.form("edit_profile_form"):
            new_name = st.text_input("ชื่อ-นามสกุล", value=user.get('full_name', ''))
            col_a, col_b = st.columns(2)
            with col_a:
                new_age = st.number_input("อายุ (ปี)", min_value=10, max_value=100, value=int(user.get('age', 25)))
                new_height = st.number_input("ส่วนสูง (ซม.)", min_value=100.0, max_value=230.0, value=float(user.get('height', 175.0)), step=0.5)
            with col_b:
                new_gender = st.selectbox("เพศ", ["ชาย", "หญิง", "อื่นๆ"], index=0 if user.get('gender') == 'ชาย' else 1)
                new_weight = st.number_input("น้ำหนัก (กก.)", min_value=30.0, max_value=250.0, value=float(user.get('weight', 68.0)), step=0.5)
                
            save_submit = st.form_submit_button("💾 บันทึกการเปลี่ยนแปลง", use_container_width=True)
            
            if save_submit:
                payload = {
                    "full_name": new_name, "age": new_age,
                    "gender": new_gender, "height": new_height,
                    "weight": new_weight
                }
                res = api_put("profile", payload)
                if res and res.status_code == 200:
                    st.session_state.user = res.json()
                    st.success("🎉 บันทึกข้อมูลส่วนตัวเรียบร้อยแล้ว!")
                    st.rerun()
                else:
                    st.error("❌ ไม่สามารถบันทึกข้อมูลได้")

    with col_p2:
        st.markdown("### 🧬 ดัชนีสุขภาพเฉพาะบุคคล (AI Health Metrics)")
        
        w = float(user.get('weight', 68.0))
        h = float(user.get('height', 175.0))
        a = int(user.get('age', 25))
        g = user.get('gender', 'ชาย')
        bmi = float(user.get('bmi', 22.0))
        
        bmr = calculate_bmr(w, h, a, g)
        tdee = calculate_tdee(bmr)
        water = calculate_daily_water(w)
        bmi_status, bmi_c = get_bmi_status(bmi)
        
        st.markdown(f"""
        <div class='hud-card' style='margin-bottom: 12px;'>
            <div class='hud-label'>🎯 ค่า BMI สุขภาพ</div>
            <div class='hud-value digital-num' style='color: {bmi_c};'>{bmi:.1f}</div>
            <div style='font-size: 0.8rem; color: {bmi_c}; font-weight: 600;'>{bmi_status}</div>
        </div>
        
        <div class='hud-card cyan' style='margin-bottom: 12px;'>
            <div class='hud-label'>🔥 BMR (อัตราเผาผลาญพื้นฐาน)</div>
            <div class='hud-value digital-num'>{bmr} <span style='font-size: 1rem;'>kcal/วัน</span></div>
            <div style='font-size: 0.75rem; color: #94A3B8;'>พลังงานขั้นต่ำที่ร่างกายต้องการขณะพักผ่อน</div>
        </div>
        
        <div class='hud-card amber' style='margin-bottom: 12px;'>
            <div class='hud-label'>⚡ TDEE (พลังงานที่เผาผลาญต่อวัน)</div>
            <div class='hud-value amber digital-num'>{tdee} <span style='font-size: 1rem;'>kcal/วัน</span></div>
            <div style='font-size: 0.75rem; color: #94A3B8;'>พลังงานที่ใช้ทั้งหมดรวมการออกกำลังกายระดับปานกลาง</div>
        </div>
        
        <div class='hud-card purple'>
            <div class='hud-label'>💧 ปริมาณน้ำดื่มที่แนะนำต่อวัน</div>
            <div class='hud-value digital-num' style='color: #60EFFF;'>{water} <span style='font-size: 1rem;'>ลิตร/วัน</span></div>
            <div style='font-size: 0.75rem; color: #94A3B8;'>ช่วยเพิ่มประสิทธิภาพการทำงานของกล้ามเนื้อและการฟื้นฟู</div>
        </div>
        """, unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# MAIN APPLICATION ROUTER & SIDEBAR
# ---------------------------------------------------------------------------
if st.session_state.token is None:
    page_login_register()
elif st.session_state.user is None:
    st.session_state.token = None
    st.session_state.current_page = "เข้าสู่ระบบ"
    st.error("⚠️ เซสชันหมดอายุ กรุณาเข้าสู่ระบบใหม่อีกครั้ง")
    st.rerun()
else:
    user = st.session_state.user
    full_name = user.get('full_name', 'Athlete')
    username = user.get('username', 'user')
    initials = "".join([part[0].upper() for part in full_name.split()[:2]]) if full_name else "AI"
    bmi = user.get('bmi', 0)
    
    with st.sidebar:
        st.markdown(f"""
        <div class='sidebar-brand'>
            <div class='sidebar-brand-title'>⚡ AI FIT PRO</div>
            <div class='sidebar-brand-subtitle'>Next-Gen Vision HUD</div>
        </div>
        
        <div class='athlete-card'>
            <div class='athlete-header'>
                <div class='athlete-avatar'>{initials}</div>
                <div class='athlete-info'>
                    <div class='athlete-name'>{full_name}</div>
                    <div class='athlete-tag'>@{username} • PRO</div>
                </div>
            </div>
            <div style='margin-top: 8px; padding-top: 6px; border-top: 1px solid var(--border-subtle); display: flex; justify-content: space-between; align-items: center;'>
                <span style='font-size: 0.72rem; color: #94A3B8;'>ค่า BMI: <b style='color: #00FF87;'>{bmi:.1f}</b></span>
                <span class='status-pill' style='padding: 1px 7px; font-size: 0.62rem;'><span class='status-dot'></span> ONLINE</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<div style='margin-bottom: 6px; font-size: 0.72rem; color: #64748B; letter-spacing: 0.1em; text-transform: uppercase; font-weight: 700;'>NAVIGATION MENU</div>", unsafe_allow_html=True)
        
        if st.button("📊 แดชบอร์ด & สถิติ", use_container_width=True, type="primary" if st.session_state.current_page == "Dashboard" else "secondary"):
            st.session_state.current_page = "Dashboard"
            st.session_state.last_workout_summary = None
            st.rerun()
            
        if st.button("💪 เลือกท่าออกกำลังกาย", use_container_width=True, type="primary" if st.session_state.current_page in ["เลือกท่าออกกำลังกาย", "Exercise_Active"] else "secondary"):
            st.session_state.current_page = "เลือกท่าออกกำลังกาย"
            st.session_state.last_workout_summary = None
            st.rerun()
            
        if st.button("📅 ประวัติ & รายงาน", use_container_width=True, type="primary" if st.session_state.current_page == "History" else "secondary"):
            st.session_state.current_page = "History"
            st.session_state.last_workout_summary = None
            st.rerun()

        if st.button("🏆 อันดับ & ความสำเร็จ", use_container_width=True, type="primary" if st.session_state.current_page == "Leaderboard" else "secondary"):
            st.session_state.current_page = "Leaderboard"
            st.session_state.last_workout_summary = None
            st.rerun()

        if st.button("🧬 โปรไฟล์ & ดัชนีสุขภาพ", use_container_width=True, type="primary" if st.session_state.current_page == "Profile" else "secondary"):
            st.session_state.current_page = "Profile"
            st.session_state.last_workout_summary = None
            st.rerun()
            
        st.markdown("---")
        
        # Audio voice toggle switch in sidebar
        voice_on = st.toggle("🔊 โค้ชเสียงภาษาไทย (Voice)", value=st.session_state.voice_enabled)
        if voice_on != st.session_state.voice_enabled:
            st.session_state.voice_enabled = voice_on
            voice_alert.set_enabled(voice_on)
            
        if st.button("🚪 ออกจากระบบ (Logout)", use_container_width=True):
            st.session_state.token = None
            st.session_state.user = None
            st.session_state.last_workout_summary = None
            st.session_state.current_page = "เข้าสู่ระบบ"
            st.rerun()

    # Routing
    if st.session_state.current_page == "Dashboard":
        page_dashboard()
    elif st.session_state.current_page == "เลือกท่าออกกำลังกาย":
        page_exercise_selection()
    elif st.session_state.current_page == "Exercise_Active":
        page_exercise_active()
    elif st.session_state.current_page == "History":
        page_history()
    elif st.session_state.current_page == "Leaderboard":
        page_leaderboard_achievements()
    elif st.session_state.current_page == "Profile":
        page_profile()
    else:
        page_dashboard()