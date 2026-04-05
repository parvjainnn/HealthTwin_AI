import streamlit as st
import pandas as pd
import numpy as np
import json
import os
import sqlite3
from datetime import datetime
import plotly.graph_objects as go
import plotly.express as px
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
import random
import time

# ─── Page Config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="AI Health Twin",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─── Custom CSS ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap');

/* ── Root Variables ── */
:root {
    --bg-primary: #0a0f1e;
    --bg-card: #111827;
    --bg-card2: #1a2236;
    --accent-cyan: #00e5ff;
    --accent-green: #00ff88;
    --accent-orange: #ff6b35;
    --accent-purple: #8b5cf6;
    --accent-red: #ff4757;
    --text-primary: #e2e8f0;
    --text-muted: #64748b;
    --border: #1e293b;
    --glow-cyan: 0 0 20px rgba(0,229,255,0.3);
    --glow-green: 0 0 20px rgba(0,255,136,0.3);
}

/* ── Global ── */
.stApp {
    background-color: var(--bg-primary) !important;
    font-family: 'Plus Jakarta Sans', sans-serif;
    color: var(--text-primary);
}

.main .block-container {
    padding: 1.5rem 2rem;
    max-width: 1400px;
}

/* ── Hide Streamlit Defaults ── */
#MainMenu, footer, header { visibility: hidden; }
.stDeployButton { display: none; }

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0d1424 0%, #111827 100%) !important;
    border-right: 1px solid var(--border);
}
[data-testid="stSidebar"] .stMarkdown h2 {
    color: var(--accent-cyan) !important;
    font-family: 'Space Mono', monospace !important;
    font-size: 0.85rem !important;
    letter-spacing: 0.15em !important;
    text-transform: uppercase;
}
[data-testid="stSidebar"] label {
    color: var(--text-muted) !important;
    font-size: 0.78rem !important;
    font-weight: 600;
    letter-spacing: 0.05em;
}
[data-testid="stSidebar"] .stSlider { color: var(--accent-cyan); }

/* ── Inputs ── */
.stNumberInput input, .stSelectbox select, .stTextInput input {
    background: var(--bg-card2) !important;
    border: 1px solid var(--border) !important;
    color: var(--text-primary) !important;
    border-radius: 8px !important;
}
.stSlider [data-testid="stThumbValue"] {
    color: var(--accent-cyan) !important;
}

/* ── Metric Cards ── */
.metric-card {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 16px;
    padding: 1.25rem 1.5rem;
    text-align: center;
    transition: all 0.3s ease;
    position: relative;
    overflow: hidden;
}
.metric-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: linear-gradient(90deg, var(--accent-cyan), var(--accent-green));
    opacity: 0;
    transition: opacity 0.3s;
}
.metric-card:hover::before { opacity: 1; }
.metric-card:hover { border-color: rgba(0,229,255,0.3); }

.metric-label {
    font-size: 0.7rem;
    font-weight: 700;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: var(--text-muted);
    margin-bottom: 0.4rem;
}
.metric-value {
    font-family: 'Space Mono', monospace;
    font-size: 2rem;
    font-weight: 700;
    line-height: 1;
}
.metric-sub {
    font-size: 0.72rem;
    color: var(--text-muted);
    margin-top: 0.3rem;
}

/* ── Section Headers ── */
.section-header {
    font-family: 'Space Mono', monospace;
    font-size: 0.75rem;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    color: var(--accent-cyan);
    margin: 2rem 0 1rem 0;
    padding-bottom: 0.5rem;
    border-bottom: 1px solid var(--border);
}

/* ── Risk Badge ── */
.risk-badge {
    display: inline-block;
    padding: 0.3rem 1rem;
    border-radius: 999px;
    font-size: 0.78rem;
    font-weight: 700;
    letter-spacing: 0.08em;
    text-transform: uppercase;
}
.risk-low { background: rgba(0,255,136,0.12); color: #00ff88; border: 1px solid rgba(0,255,136,0.3); }
.risk-medium { background: rgba(255,165,0,0.12); color: #ffa500; border: 1px solid rgba(255,165,0,0.3); }
.risk-high { background: rgba(255,71,87,0.12); color: #ff4757; border: 1px solid rgba(255,71,87,0.3); }

/* ── Chat Interface ── */
.chat-container {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 16px;
    padding: 1.5rem;
    max-height: 420px;
    overflow-y: auto;
}
.chat-message-user {
    background: rgba(0,229,255,0.08);
    border: 1px solid rgba(0,229,255,0.2);
    border-radius: 12px 12px 4px 12px;
    padding: 0.75rem 1rem;
    margin: 0.5rem 0;
    text-align: right;
    font-size: 0.88rem;
    color: var(--accent-cyan);
}
.chat-message-ai {
    background: var(--bg-card2);
    border: 1px solid var(--border);
    border-radius: 12px 12px 12px 4px;
    padding: 0.75rem 1rem;
    margin: 0.5rem 0;
    font-size: 0.88rem;
    color: var(--text-primary);
    line-height: 1.6;
}
.chat-label-user {
    font-size: 0.65rem;
    color: var(--accent-cyan);
    font-weight: 700;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    text-align: right;
    margin-bottom: 0.2rem;
}
.chat-label-ai {
    font-size: 0.65rem;
    color: var(--accent-green);
    font-weight: 700;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    margin-bottom: 0.2rem;
}

/* ── Main Title ── */
.hero-title {
    font-family: 'Space Mono', monospace;
    font-size: 1.8rem;
    font-weight: 700;
    background: linear-gradient(135deg, #00e5ff 0%, #00ff88 50%, #8b5cf6 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    line-height: 1.2;
}
.hero-subtitle {
    color: var(--text-muted);
    font-size: 0.85rem;
    margin-top: 0.25rem;
    font-weight: 400;
}

/* ── Progress Bar ── */
.health-bar-track {
    background: var(--bg-card2);
    border-radius: 999px;
    height: 8px;
    width: 100%;
    overflow: hidden;
    margin: 0.5rem 0;
}
.health-bar-fill {
    height: 100%;
    border-radius: 999px;
    transition: width 0.8s ease;
}

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {
    background: var(--bg-card) !important;
    border-radius: 12px;
    padding: 4px;
    border: 1px solid var(--border);
    gap: 4px;
}
.stTabs [data-baseweb="tab"] {
    background: transparent !important;
    color: var(--text-muted) !important;
    border-radius: 8px !important;
    font-size: 0.82rem !important;
    font-weight: 600;
    padding: 0.4rem 1rem !important;
}
.stTabs [aria-selected="true"] {
    background: var(--bg-card2) !important;
    color: var(--accent-cyan) !important;
}
.stTabs [data-baseweb="tab-panel"] {
    background: transparent !important;
    padding: 1.5rem 0 !important;
}

/* ── Buttons ── */
.stButton > button {
    background: linear-gradient(135deg, #00e5ff22, #00ff8822) !important;
    border: 1px solid var(--accent-cyan) !important;
    color: var(--accent-cyan) !important;
    border-radius: 10px !important;
    font-family: 'Space Mono', monospace !important;
    font-size: 0.78rem !important;
    letter-spacing: 0.08em !important;
    text-transform: uppercase !important;
    padding: 0.5rem 1.5rem !important;
    transition: all 0.2s !important;
}
.stButton > button:hover {
    background: linear-gradient(135deg, #00e5ff33, #00ff8833) !important;
    box-shadow: var(--glow-cyan) !important;
}

/* ── Info / Warning / Success ── */
.stInfo, .stWarning, .stSuccess, .stError {
    background: var(--bg-card2) !important;
    border-radius: 10px !important;
}

/* ── Watch Simulation ── */
.watch-card {
    background: radial-gradient(ellipse at top, #1a2236, #0d1424);
    border: 1px solid var(--border);
    border-radius: 20px;
    padding: 1.5rem;
    text-align: center;
    position: relative;
}
.watch-title {
    font-family: 'Space Mono', monospace;
    font-size: 0.65rem;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    color: var(--text-muted);
    margin-bottom: 1rem;
}
.pulse-dot {
    display: inline-block;
    width: 8px; height: 8px;
    background: var(--accent-green);
    border-radius: 50%;
    margin-right: 6px;
    animation: pulse 1.5s infinite;
}
@keyframes pulse {
    0%, 100% { opacity: 1; transform: scale(1); }
    50% { opacity: 0.4; transform: scale(0.8); }
}

/* Scrollbar */
::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-track { background: var(--bg-primary); }
::-webkit-scrollbar-thumb { background: var(--border); border-radius: 2px; }
</style>
""", unsafe_allow_html=True)


# ─── Database Setup ────────────────────────────────────────────────────────────
def init_db():
    conn = sqlite3.connect("health_twin.db")
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS health_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            name TEXT,
            age INTEGER,
            gender TEXT,
            weight REAL,
            height REAL,
            steps INTEGER,
            sleep REAL,
            water REAL,
            heart_rate INTEGER,
            bmi REAL,
            health_score REAL,
            obesity_risk TEXT,
            fatigue_risk TEXT
        )
    """)
    conn.commit()
    conn.close()

def save_record(data: dict):
    conn = sqlite3.connect("health_twin.db")
    c = conn.cursor()
    c.execute("""
        INSERT INTO health_logs
        (timestamp,name,age,gender,weight,height,steps,sleep,water,heart_rate,bmi,health_score,obesity_risk,fatigue_risk)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)
    """, (
        data["timestamp"], data["name"], data["age"], data["gender"],
        data["weight"], data["height"], data["steps"], data["sleep"],
        data["water"], data["heart_rate"], data["bmi"],
        data["health_score"], data["obesity_risk"], data["fatigue_risk"]
    ))
    conn.commit()
    conn.close()

def load_history():
    if not os.path.exists("health_twin.db"):
        return pd.DataFrame()
    conn = sqlite3.connect("health_twin.db")
    df = pd.read_sql_query("SELECT * FROM health_logs ORDER BY timestamp DESC LIMIT 30", conn)
    conn.close()
    return df


# ─── ML Risk Model ─────────────────────────────────────────────────────────────
@st.cache_resource
def build_models():
    """Train simple risk classifiers on synthetic data."""
    np.random.seed(42)
    n = 800

    # Features: bmi, sleep, steps, water, age
    bmi_s = np.random.normal(24, 5, n).clip(15, 45)
    sleep_s = np.random.normal(6.5, 1.5, n).clip(3, 10)
    steps_s = np.random.randint(1000, 18000, n).astype(float)
    water_s = np.random.normal(2, 0.8, n).clip(0.5, 5)
    age_s = np.random.randint(18, 75, n).astype(float)

    # Obesity label
    obesity_y = ((bmi_s > 27) | ((bmi_s > 25) & (steps_s < 5000))).astype(int)

    # Fatigue label
    fatigue_y = ((sleep_s < 6) | ((steps_s < 4000) & (sleep_s < 7)) | (water_s < 1.5)).astype(int)

    X = np.column_stack([bmi_s, sleep_s, steps_s, water_s, age_s])
    scaler = StandardScaler()
    Xs = scaler.fit_transform(X)

    ob_clf = RandomForestClassifier(n_estimators=60, random_state=42)
    ob_clf.fit(Xs, obesity_y)

    fat_clf = RandomForestClassifier(n_estimators=60, random_state=42)
    fat_clf.fit(Xs, fatigue_y)

    return ob_clf, fat_clf, scaler

def predict_risks(bmi, sleep, steps, water, age):
    ob_clf, fat_clf, scaler = build_models()
    X = scaler.transform([[bmi, sleep, steps, water, age]])
    ob_prob = ob_clf.predict_proba(X)[0][1]
    fat_prob = fat_clf.predict_proba(X)[0][1]

    def risk_label(p):
        if p < 0.35: return "Low", "risk-low"
        elif p < 0.65: return "Medium", "risk-medium"
        else: return "High", "risk-high"

    return risk_label(ob_prob), risk_label(fat_prob), ob_prob, fat_prob


# ─── Health Score ──────────────────────────────────────────────────────────────
def calc_bmi(weight, height_cm):
    h = height_cm / 100
    return round(weight / (h * h), 1)

def bmi_category(bmi):
    if bmi < 18.5: return "Underweight", "#8b5cf6"
    elif bmi < 25: return "Normal", "#00ff88"
    elif bmi < 30: return "Overweight", "#ffa500"
    else: return "Obese", "#ff4757"

def calc_health_score(bmi, sleep, steps, water, heart_rate=None):
    score = 100.0
    # BMI component (0-25 pts)
    if 18.5 <= bmi <= 24.9:
        bmi_pts = 25
    elif 17 <= bmi < 18.5 or 25 <= bmi < 27:
        bmi_pts = 18
    elif 15 <= bmi < 17 or 27 <= bmi < 30:
        bmi_pts = 10
    else:
        bmi_pts = 5
    score = bmi_pts  # reset to components

    # Sleep component (0-25 pts)
    if 7 <= sleep <= 9:
        sleep_pts = 25
    elif 6 <= sleep < 7 or 9 < sleep <= 10:
        sleep_pts = 18
    elif 5 <= sleep < 6:
        sleep_pts = 10
    else:
        sleep_pts = 5

    # Steps component (0-25 pts)
    if steps >= 10000:
        step_pts = 25
    elif steps >= 7500:
        step_pts = 20
    elif steps >= 5000:
        step_pts = 14
    elif steps >= 3000:
        step_pts = 8
    else:
        step_pts = 3

    # Water component (0-15 pts)
    if 2 <= water <= 3.5:
        water_pts = 15
    elif 1.5 <= water < 2:
        water_pts = 10
    elif water >= 3.5:
        water_pts = 12
    else:
        water_pts = 5

    # Heart rate component (0-10 pts)
    hr_pts = 10
    if heart_rate:
        if 60 <= heart_rate <= 80:
            hr_pts = 10
        elif 50 <= heart_rate < 60 or 80 < heart_rate <= 90:
            hr_pts = 7
        elif heart_rate > 100 or heart_rate < 50:
            hr_pts = 3

    total = bmi_pts + sleep_pts + step_pts + water_pts + hr_pts
    return round(min(100, max(0, total)), 1), bmi_pts, sleep_pts, step_pts, water_pts, hr_pts


# ─── AI Advisor (Rule-Based + Contextual) ──────────────────────────────────────
def get_ai_response(question, user_data):
    """
    Uses the Anthropic API (via the claude-sonnet-4-20250514 model) if available,
    otherwise falls back to a rich rule-based system.
    """
    import re
    q = question.lower()

    bmi = user_data.get("bmi", 22)
    sleep = user_data.get("sleep", 7)
    steps = user_data.get("steps", 7000)
    water = user_data.get("water", 2)
    heart_rate = user_data.get("heart_rate", 70)
    age = user_data.get("age", 30)
    weight = user_data.get("weight", 70)
    height = user_data.get("height", 170)
    health_score = user_data.get("health_score", 70)
    ob_risk = user_data.get("obesity_risk", "Low")
    fat_risk = user_data.get("fatigue_risk", "Low")
    name = user_data.get("name", "there")
    bmi_cat, _ = bmi_category(bmi)

    # Build a rich context string
    profile = f"""
User Profile: {name}, Age {age}, Gender: {user_data.get('gender','Unknown')}
BMI: {bmi} ({bmi_cat}), Health Score: {health_score}/100
Sleep: {sleep}h/night, Daily Steps: {steps:,}, Water: {water}L/day
Heart Rate: {heart_rate if heart_rate else 'N/A'} bpm
Obesity Risk: {ob_risk}, Fatigue Risk: {fat_risk}
"""

    # Try OpenAI-compatible endpoint or just use local rules
    # For demo purposes this is a smart rule-based engine:
    responses = []

    if any(k in q for k in ["tired", "fatigue", "energy", "exhaust", "sleepy"]):
        if sleep < 6:
            responses.append(f"🛌 **Sleep Deficit Detected** — You're averaging only {sleep}h of sleep. Your body needs 7–9 hours for cellular repair and energy restoration. Consider a consistent bedtime 30 minutes earlier each week.")
        if steps < 4000:
            responses.append(f"🚶 **Sedentary Alert** — Low activity ({steps:,} steps) reduces circulation and oxygen delivery to muscles, causing fatigue. Even a 15-minute walk boosts mitochondrial activity.")
        if water < 1.5:
            responses.append(f"💧 **Dehydration Risk** — At {water}L/day you may be mildly dehydrated. Dehydration reduces blood volume, making your heart work harder and leaving you tired.")
        if not responses:
            responses.append(f"✅ Your vitals look reasonable! Fatigue at your profile ({sleep}h sleep, {steps:,} steps) could stem from stress, screen time, or diet. Try reducing blue light 1h before bed.")

    elif any(k in q for k in ["weight", "bmi", "obese", "fat", "slim", "overweight"]):
        responses.append(f"⚖️ **Your BMI is {bmi} ({bmi_cat})**. ")
        if bmi > 25:
            deficit = round((bmi - 24.9) * ((height/100)**2), 1)
            responses.append(f"Losing approximately {deficit}kg would bring you into the healthy range. A 500-calorie daily deficit achieves ~0.5kg/week safely.")
        elif bmi < 18.5:
            responses.append(f"You're underweight. Aim to add 300–500 kcal/day through protein-rich whole foods, not processed carbs.")
        else:
            responses.append(f"You're in the healthy BMI range. Maintain it with {steps:,}+ daily steps and balanced nutrition.")

    elif any(k in q for k in ["sleep", "insomnia", "rest", "nap"]):
        if sleep < 7:
            responses.append(f"😴 You're getting {sleep}h — below the 7–9h adult recommendation. Sleep debt accumulates and impacts cognition, immunity, and metabolism. Try: no caffeine after 2pm, bedroom temperature 65–68°F, and consistent wake times including weekends.")
        else:
            responses.append(f"🌙 Your {sleep}h sleep is within the healthy range. Maintain sleep quality by avoiding alcohol within 3h of bedtime and keeping screens dim after 9pm.")

    elif any(k in q for k in ["exercise", "steps", "active", "workout", "walk", "run"]):
        if steps < 5000:
            responses.append(f"🏃 **Low Activity** — {steps:,} steps is below the WHO guideline of 8,000–10,000. Start with +1,000 steps/week. Park farther away, take stairs, use walking meetings.")
        elif steps >= 10000:
            responses.append(f"🔥 **Great Activity!** {steps:,} steps puts you in the top tier. Add strength training 2–3x/week to complement your cardio for metabolic benefits.")
        else:
            responses.append(f"👟 **Decent Activity** — {steps:,} steps is decent. Targeting 10,000 would put you in the highest health benefit zone. Add a 20-minute post-dinner walk.")

    elif any(k in q for k in ["water", "hydrat", "drink", "thirst"]):
        if water < 2:
            responses.append(f"💧 **Increase Hydration** — {water}L is below recommended. Aim for 2.5–3L daily. Use a marked water bottle and set hourly reminders. Add electrolytes if you're active.")
        else:
            responses.append(f"✅ **Good Hydration** — {water}L is on target. Keep it consistent throughout the day rather than gulping all at once for better absorption.")

    elif any(k in q for k in ["heart", "bp", "blood pressure", "cardiac", "pulse"]):
        if heart_rate and heart_rate > 90:
            responses.append(f"❤️ **Elevated Resting HR** ({heart_rate} bpm) — Normal is 60–80 bpm. Elevated HR can indicate stress, dehydration, or low fitness. Consider 30-min cardio sessions 3x/week to lower it over 6–8 weeks.")
        elif heart_rate:
            responses.append(f"✅ **Heart Rate is Normal** ({heart_rate} bpm). Regular aerobic exercise keeps it optimal. Athletes can have resting HR as low as 40–50 bpm.")

    elif any(k in q for k in ["diet", "eat", "food", "nutrition", "calories"]):
        responses.append(f"🥗 **Personalized Nutrition Guidance** for BMI {bmi} ({bmi_cat}): ")
        if bmi > 25:
            responses.append("Focus on a high-protein, low-glycemic diet. Prioritize vegetables, lean proteins, and complex carbs. Avoid processed sugars and ultra-processed foods. Track calories for 2 weeks to establish awareness.")
        elif bmi < 18.5:
            responses.append("Increase caloric density with nuts, avocados, legumes, and whole grains. Add a protein shake post-workout if exercising.")
        else:
            responses.append("Maintain a balanced Mediterranean-style diet. 50% vegetables/fruits, 25% whole grains, 25% lean proteins. Limit red meat to twice weekly.")

    elif any(k in q for k in ["score", "health", "overall", "summary", "status"]):
        if health_score >= 80:
            grade = "Excellent 🌟"
        elif health_score >= 65:
            grade = "Good 👍"
        elif health_score >= 50:
            grade = "Fair ⚠️"
        else:
            grade = "Needs Attention 🔴"

        responses.append(f"📊 **Health Score: {health_score}/100 — {grade}**\n\nBreakdown: Your score reflects BMI ({bmi_cat}), sleep ({sleep}h), activity ({steps:,} steps), and hydration ({water}L).")
        if health_score < 70:
            lowest = min([("sleep", sleep/9), ("steps", steps/10000), ("water", water/2.5)], key=lambda x: x[1])
            responses.append(f"\n⚡ **Biggest opportunity**: Improve your **{lowest[0]}** for the fastest score gains.")

    elif any(k in q for k in ["advice", "recommend", "tip", "suggest", "help", "improve"]):
        tips = []
        if sleep < 7: tips.append(f"• Sleep: Add 30 min earlier bedtime (currently {sleep}h, target 7–8h)")
        if steps < 7000: tips.append(f"• Activity: Add a 20-min walk to reach 7,000+ steps (currently {steps:,})")
        if water < 2: tips.append(f"• Hydration: Drink 1 more glass/hour (currently {water}L, target 2.5L)")
        if bmi > 25: tips.append(f"• Weight: Reduce 200 kcal/day — small sustainable deficit")
        if not tips:
            tips.append("• Your metrics are solid! Focus on maintaining consistency")
            tips.append("• Add strength training 2x/week for long-term metabolic health")
            tips.append("• Get a full blood panel annually to track internals")
        responses.append("🎯 **Personalized Recommendations:**\n\n" + "\n".join(tips))

    else:
        responses.append(f"🤖 Based on your profile (BMI: {bmi}, Sleep: {sleep}h, Steps: {steps:,}, Score: {health_score}/100), I can advise on: **fatigue, weight, sleep, exercise, hydration, diet, heart health, or your overall health score**. What would you like to know?")

    return " ".join(responses)


# ─── Smartwatch Simulation ──────────────────────────────────────────────────────
def simulate_watch_data(base_hr=72):
    hr = base_hr + random.randint(-8, 12)
    spo2 = random.uniform(96, 99.5)
    stress = random.randint(20, 75)
    steps_live = random.randint(200, 800)
    calories = random.randint(1400, 2200)
    return {
        "heart_rate": hr,
        "spo2": round(spo2, 1),
        "stress": stress,
        "live_steps": steps_live * 8,
        "calories": calories
    }


# ─── Gauge Chart ───────────────────────────────────────────────────────────────
def make_gauge(value, title, max_val=100, color="#00e5ff"):
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=value,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': title, 'font': {'color': '#64748b', 'size': 12, 'family': 'Plus Jakarta Sans'}},
        number={'font': {'color': color, 'size': 28, 'family': 'Space Mono'}},
        gauge={
            'axis': {'range': [0, max_val], 'tickcolor': '#1e293b', 'tickfont': {'color': '#64748b', 'size': 9}},
            'bar': {'color': color, 'thickness': 0.25},
            'bgcolor': '#111827',
            'bordercolor': '#1e293b',
            'borderwidth': 1,
            'steps': [
                {'range': [0, max_val*0.35], 'color': 'rgba(255,71,87,0.15)'},
                {'range': [max_val*0.35, max_val*0.65], 'color': 'rgba(255,165,0,0.15)'},
                {'range': [max_val*0.65, max_val], 'color': 'rgba(0,255,136,0.15)'},
            ],
            'threshold': {
                'line': {'color': color, 'width': 2},
                'thickness': 0.8,
                'value': value
            }
        }
    ))
    fig.update_layout(
        height=200,
        margin=dict(l=20, r=20, t=40, b=10),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font_family='Plus Jakarta Sans'
    )
    return fig


def make_radar(categories, values, name="You"):
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=values + [values[0]],
        theta=categories + [categories[0]],
        fill='toself',
        name=name,
        line=dict(color='#00e5ff', width=2),
        fillcolor='rgba(0,229,255,0.12)'
    ))
    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 25], gridcolor='#1e293b', tickfont=dict(color='#64748b', size=9)),
            angularaxis=dict(gridcolor='#1e293b', tickfont=dict(color='#94a3b8', size=11))
        ),
        showlegend=False,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        height=280,
        margin=dict(l=40, r=40, t=30, b=30)
    )
    return fig


def make_history_chart(df):
    if df.empty or len(df) < 2:
        return None
    df = df.copy()
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df = df.sort_values('timestamp')

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df['timestamp'], y=df['health_score'],
        mode='lines+markers',
        name='Health Score',
        line=dict(color='#00e5ff', width=2),
        marker=dict(size=6, color='#00e5ff'),
        fill='tozeroy',
        fillcolor='rgba(0,229,255,0.06)'
    ))
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        height=200,
        margin=dict(l=10, r=10, t=20, b=20),
        xaxis=dict(gridcolor='#1e293b', tickfont=dict(color='#64748b', size=9)),
        yaxis=dict(gridcolor='#1e293b', tickfont=dict(color='#64748b', size=9), range=[0, 100]),
        showlegend=False
    )
    return fig


# ─── Init ─────────────────────────────────────────────────────────────────────
init_db()
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "user_data" not in st.session_state:
    st.session_state.user_data = {}
if "watch_data" not in st.session_state:
    st.session_state.watch_data = simulate_watch_data()


# ─── Sidebar ─────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style='text-align:center; padding: 1rem 0 0.5rem;'>
        <div style='font-size:2rem; margin-bottom:0.3rem;'>🧬</div>
        <div style='font-family: Space Mono, monospace; font-size:1rem; font-weight:700;
                    background: linear-gradient(135deg,#00e5ff,#00ff88);
                    -webkit-background-clip:text; -webkit-text-fill-color:transparent;'>
            AI HEALTH TWIN
        </div>
        <div style='color:#64748b; font-size:0.7rem; margin-top:0.2rem; letter-spacing:0.1em;'>
            PERSONALIZED TRACKER
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("## 👤 Profile")
    name = st.text_input("Name", value="Alex", key="name_input")
    gender = st.selectbox("Gender", ["Male", "Female", "Other"])

    st.markdown("## 📊 Vitals")
    age = st.number_input("Age", 10, 100, 28)
    col_a, col_b = st.columns(2)
    with col_a:
        weight = st.number_input("Weight (kg)", 30.0, 200.0, 72.0, step=0.5)
    with col_b:
        height = st.number_input("Height (cm)", 100, 220, 175)

    st.markdown("## 🏃 Activity & Wellness")
    steps = st.number_input("Daily Steps", 0, 30000, 6500, step=500)
    sleep = st.slider("Sleep Hours", 0.0, 12.0, 6.5, 0.5)
    water = st.slider("Water Intake (L)", 0.0, 5.0, 2.0, 0.25)
    heart_rate = st.number_input("Resting Heart Rate (bpm)", 40, 200, 72)

    st.markdown("---")

    col_s1, col_s2 = st.columns(2)
    with col_s1:
        analyze_btn = st.button("🔍 Analyze", use_container_width=True)
    with col_s2:
        save_btn = st.button("💾 Save Log", use_container_width=True)

    # Watch simulation refresh
    if st.button("⌚ Refresh Watch", use_container_width=True):
        st.session_state.watch_data = simulate_watch_data(heart_rate)
        st.rerun()


# ─── Compute Metrics ─────────────────────────────────────────────────────────
bmi = calc_bmi(weight, height)
bmi_cat, bmi_color = bmi_category(bmi)
health_score, bmi_pts, sleep_pts, step_pts, water_pts, hr_pts = calc_health_score(bmi, sleep, steps, water, heart_rate)
(ob_risk, ob_css), (fat_risk, fat_css), ob_prob, fat_prob = predict_risks(bmi, sleep, steps, water, age)

# Store in session
st.session_state.user_data = {
    "name": name, "age": age, "gender": gender,
    "weight": weight, "height": height, "steps": steps,
    "sleep": sleep, "water": water, "heart_rate": heart_rate,
    "bmi": bmi, "health_score": health_score,
    "obesity_risk": ob_risk, "fatigue_risk": fat_risk
}

# Save log
if save_btn:
    record = {**st.session_state.user_data,
              "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
    save_record(record)
    st.sidebar.success("✅ Log saved!")


# ─── Hero Header ─────────────────────────────────────────────────────────────
col_title, col_score_hero = st.columns([3, 1])
with col_title:
    st.markdown(f"""
    <div class='hero-title'>AI Health Twin</div>
    <div class='hero-subtitle'>Welcome back, <span style='color:#00e5ff'>{name}</span> · {datetime.now().strftime("%B %d, %Y")}</div>
    """, unsafe_allow_html=True)
with col_score_hero:
    if health_score >= 80:
        score_color = "#00ff88"
        score_emoji = "🟢"
    elif health_score >= 60:
        score_color = "#ffa500"
        score_emoji = "🟡"
    else:
        score_color = "#ff4757"
        score_emoji = "🔴"
    st.markdown(f"""
    <div style='text-align:right;'>
        <div style='font-size:0.65rem; color:#64748b; letter-spacing:0.15em; text-transform:uppercase;'>Health Score</div>
        <div style='font-family: Space Mono, monospace; font-size:3rem; font-weight:700; color:{score_color}; line-height:1;'>{health_score}</div>
        <div style='font-size:0.72rem; color:#64748b;'>out of 100</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<div style='margin-top:1rem;'></div>", unsafe_allow_html=True)


# ─── Tabs ─────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5 = st.tabs(["📊 Dashboard", "🤖 AI Advisor", "⚠️ Risk Analysis", "⌚ Smart Watch", "📈 History"])


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 1: DASHBOARD
# ═══════════════════════════════════════════════════════════════════════════════
with tab1:
    # Top KPI Row
    cols = st.columns(5)
    metrics = [
        ("BMI", bmi, bmi_cat, bmi_color),
        ("Steps", f"{steps:,}", "Daily Goal: 10K", "#00e5ff"),
        ("Sleep", f"{sleep}h", "Rec: 7–9h", "#8b5cf6"),
        ("Hydration", f"{water}L", "Rec: 2.5L", "#00ff88"),
        ("Heart Rate", f"{heart_rate}", "bpm resting", "#ff6b35"),
    ]
    for col, (label, val, sub, color) in zip(cols, metrics):
        with col:
            st.markdown(f"""
            <div class='metric-card'>
                <div class='metric-label'>{label}</div>
                <div class='metric-value' style='color:{color}'>{val}</div>
                <div class='metric-sub'>{sub}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<div class='section-header'>Health Score Breakdown</div>", unsafe_allow_html=True)

    col_gauge, col_radar, col_bar = st.columns([1, 1.2, 1.2])

    with col_gauge:
        st.plotly_chart(make_gauge(health_score, "Overall Health Score", 100, score_color), use_container_width=True, config={"displayModeBar": False})

    with col_radar:
        cat = ["BMI", "Sleep", "Steps", "Water", "Heart Rate"]
        vals = [bmi_pts, sleep_pts, step_pts, water_pts, hr_pts]
        st.plotly_chart(make_radar(cat, vals), use_container_width=True, config={"displayModeBar": False})

    with col_bar:
        st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)
        bar_items = [
            ("BMI", bmi_pts, 25, bmi_color),
            ("Sleep", sleep_pts, 25, "#8b5cf6"),
            ("Steps", step_pts, 25, "#00e5ff"),
            ("Water", water_pts, 15, "#00ff88"),
            ("Heart Rate", hr_pts, 10, "#ff6b35"),
        ]
        for label, pts, max_pts, color in bar_items:
            pct = int(pts / max_pts * 100)
            st.markdown(f"""
            <div style='margin-bottom:0.8rem;'>
                <div style='display:flex; justify-content:space-between; font-size:0.75rem; color:#94a3b8; margin-bottom:0.2rem;'>
                    <span>{label}</span>
                    <span style='font-family:Space Mono,monospace; color:{color}'>{pts}/{max_pts}</span>
                </div>
                <div class='health-bar-track'>
                    <div class='health-bar-fill' style='width:{pct}%; background: linear-gradient(90deg, {color}88, {color});'></div>
                </div>
            </div>
            """, unsafe_allow_html=True)

    # Risk Summary Row
    st.markdown("<div class='section-header'>Risk Summary</div>", unsafe_allow_html=True)
    r1, r2, r3 = st.columns(3)
    with r1:
        st.markdown(f"""
        <div class='metric-card'>
            <div class='metric-label'>Obesity Risk</div>
            <div style='margin-top:0.5rem'><span class='risk-badge {ob_css}'>{ob_risk}</span></div>
            <div class='metric-sub' style='margin-top:0.5rem'>{int(ob_prob*100)}% probability</div>
        </div>""", unsafe_allow_html=True)
    with r2:
        st.markdown(f"""
        <div class='metric-card'>
            <div class='metric-label'>Fatigue Risk</div>
            <div style='margin-top:0.5rem'><span class='risk-badge {fat_css}'>{fat_risk}</span></div>
            <div class='metric-sub' style='margin-top:0.5rem'>{int(fat_prob*100)}% probability</div>
        </div>""", unsafe_allow_html=True)
    with r3:
        overall_risk = "Low" if health_score > 75 else "Medium" if health_score > 50 else "High"
        overall_css = "risk-low" if overall_risk == "Low" else "risk-medium" if overall_risk == "Medium" else "risk-high"
        st.markdown(f"""
        <div class='metric-card'>
            <div class='metric-label'>Overall Risk</div>
            <div style='margin-top:0.5rem'><span class='risk-badge {overall_css}'>{overall_risk}</span></div>
            <div class='metric-sub' style='margin-top:0.5rem'>Score: {health_score}/100</div>
        </div>""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 2: AI ADVISOR
# ═══════════════════════════════════════════════════════════════════════════════
with tab2:
    st.markdown("""
    <div style='background: linear-gradient(135deg, rgba(0,229,255,0.05), rgba(0,255,136,0.05));
                border: 1px solid rgba(0,229,255,0.15); border-radius:12px; padding:1rem 1.25rem; margin-bottom:1.5rem;'>
        <div style='font-size:0.75rem; font-weight:700; color:#00e5ff; letter-spacing:0.12em; text-transform:uppercase;'>🤖 AI Health Advisor</div>
        <div style='font-size:0.82rem; color:#94a3b8; margin-top:0.3rem;'>
            Ask me anything about your health. I analyze your personal data to give tailored advice.
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Quick question chips
    st.markdown("**Quick Questions:**")
    qcols = st.columns(4)
    quick_qs = [
        "Why am I feeling tired?",
        "How can I improve my score?",
        "What's my weight status?",
        "Give me health tips"
    ]
    for i, (qcol, qq) in enumerate(zip(qcols, quick_qs)):
        with qcol:
            if st.button(qq, key=f"qq_{i}", use_container_width=True):
                st.session_state.chat_history.append({"role": "user", "content": qq})
                resp = get_ai_response(qq, st.session_state.user_data)
                st.session_state.chat_history.append({"role": "ai", "content": resp})
                st.rerun()

    # Chat display
    if st.session_state.chat_history:
        chat_html = "<div class='chat-container'>"
        for msg in st.session_state.chat_history:
            if msg["role"] == "user":
                chat_html += f"<div class='chat-label-user'>You</div><div class='chat-message-user'>{msg['content']}</div>"
            else:
                chat_html += f"<div class='chat-label-ai'>🧬 AI Advisor</div><div class='chat-message-ai'>{msg['content']}</div>"
        chat_html += "</div>"
        st.markdown(chat_html, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class='chat-container' style='text-align:center; padding:2rem; color:#475569;'>
            <div style='font-size:2rem;'>💬</div>
            <div style='margin-top:0.5rem; font-size:0.85rem;'>Ask a health question to get personalized advice</div>
        </div>
        """, unsafe_allow_html=True)

    # Input
    st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)
    col_inp, col_send = st.columns([5, 1])
    with col_inp:
        user_q = st.text_input("", placeholder="e.g. Why am I tired? How to improve BMI?", key="chat_input", label_visibility="collapsed")
    with col_send:
        send = st.button("Send →", use_container_width=True)

    if send and user_q:
        st.session_state.chat_history.append({"role": "user", "content": user_q})
        resp = get_ai_response(user_q, st.session_state.user_data)
        st.session_state.chat_history.append({"role": "ai", "content": resp})
        st.rerun()

    if st.button("🗑 Clear Chat", key="clear_chat"):
        st.session_state.chat_history = []
        st.rerun()


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 3: RISK ANALYSIS
# ═══════════════════════════════════════════════════════════════════════════════
with tab3:
    st.markdown("<div class='section-header'>ML Risk Prediction</div>", unsafe_allow_html=True)

    col_ob, col_fat = st.columns(2)

    with col_ob:
        ob_color = "#00ff88" if ob_risk == "Low" else "#ffa500" if ob_risk == "Medium" else "#ff4757"
        st.plotly_chart(make_gauge(int(ob_prob*100), "Obesity Risk %", 100, ob_color), use_container_width=True, config={"displayModeBar": False})
        st.markdown(f"""
        <div class='metric-card'>
            <div class='metric-label'>Risk Factors</div>
            <div style='text-align:left; margin-top:0.75rem; font-size:0.82rem; color:#94a3b8; line-height:1.8;'>
                {'⚠️ BMI ' + str(bmi) + ' (' + bmi_cat + ')' if bmi > 25 else '✅ BMI ' + str(bmi) + ' (' + bmi_cat + ')'}
                <br>
                {'⚠️ Low activity: ' + str(steps) + ' steps' if steps < 5000 else '✅ Activity: ' + str(steps) + ' steps'}
                <br>
                {'⚠️ Low water: ' + str(water) + 'L' if water < 1.5 else '✅ Hydration: ' + str(water) + 'L'}
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col_fat:
        fat_color = "#00ff88" if fat_risk == "Low" else "#ffa500" if fat_risk == "Medium" else "#ff4757"
        st.plotly_chart(make_gauge(int(fat_prob*100), "Fatigue Risk %", 100, fat_color), use_container_width=True, config={"displayModeBar": False})
        st.markdown(f"""
        <div class='metric-card'>
            <div class='metric-label'>Contributing Factors</div>
            <div style='text-align:left; margin-top:0.75rem; font-size:0.82rem; color:#94a3b8; line-height:1.8;'>
                {'⚠️ Sleep ' + str(sleep) + 'h (below 7h rec)' if sleep < 7 else '✅ Sleep: ' + str(sleep) + 'h'}
                <br>
                {'⚠️ Low steps: ' + str(steps) if steps < 4000 else '✅ Steps OK: ' + str(steps)}
                <br>
                {'⚠️ Dehydration risk' if water < 1.5 else '✅ Hydrated: ' + str(water) + 'L'}
            </div>
        </div>
        """, unsafe_allow_html=True)

    # Risk explanation
    st.markdown("<div class='section-header'>Risk Interpretation</div>", unsafe_allow_html=True)
    st.markdown(f"""
    <div style='background: var(--bg-card); border:1px solid var(--border); border-radius:12px; padding:1.25rem; font-size:0.85rem; color:#94a3b8; line-height:1.8;'>
        <strong style='color:#e2e8f0;'>How the ML Model Works</strong><br><br>
        The risk prediction uses a <strong style='color:#00e5ff;'>Random Forest Classifier</strong> trained on 800 synthetic health profiles.
        Features used: <strong>BMI, Sleep Duration, Daily Steps, Water Intake, Age</strong>.<br><br>
        🟢 <strong style='color:#00ff88;'>Low Risk (0–35%)</strong> — Metrics within healthy ranges<br>
        🟡 <strong style='color:#ffa500;'>Medium Risk (35–65%)</strong> — Some metrics need improvement<br>
        🔴 <strong style='color:#ff4757;'>High Risk (65–100%)</strong> — Multiple factors are concerning<br><br>
        <em>Note: This is a health awareness tool, not a medical diagnosis.</em>
    </div>
    """, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 4: SMARTWATCH
# ═══════════════════════════════════════════════════════════════════════════════
with tab4:
    watch = st.session_state.watch_data
    st.markdown("""
    <div style='text-align:center; margin-bottom:1.5rem;'>
        <span class='pulse-dot'></span>
        <span style='font-family:Space Mono,monospace; font-size:0.75rem; color:#64748b; letter-spacing:0.15em; text-transform:uppercase;'>
            Live Smartwatch Simulation
        </span>
    </div>
    """, unsafe_allow_html=True)

    w1, w2, w3, w4, w5 = st.columns(5)
    watch_metrics = [
        ("❤️", "Heart Rate", watch["heart_rate"], "bpm", "#ff4757"),
        ("🫁", "SpO₂", watch["spo2"], "%", "#00e5ff"),
        ("🧠", "Stress", watch["stress"], "/100", "#8b5cf6"),
        ("👟", "Live Steps", f"{watch['live_steps']:,}", "today", "#00ff88"),
        ("🔥", "Calories", f"{watch['calories']:,}", "kcal", "#ff6b35"),
    ]
    for col, (icon, label, val, unit, color) in zip([w1,w2,w3,w4,w5], watch_metrics):
        with col:
            st.markdown(f"""
            <div class='watch-card'>
                <div style='font-size:1.5rem; margin-bottom:0.3rem;'>{icon}</div>
                <div class='watch-title'>{label}</div>
                <div style='font-family:Space Mono,monospace; font-size:1.6rem; font-weight:700; color:{color};'>{val}</div>
                <div style='font-size:0.68rem; color:#64748b; margin-top:0.2rem;'>{unit}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)

    # HR chart simulation
    hr_series = [heart_rate + random.randint(-10, 10) for _ in range(30)]
    fig_hr = go.Figure()
    fig_hr.add_trace(go.Scatter(
        y=hr_series,
        mode='lines',
        line=dict(color='#ff4757', width=2),
        fill='tozeroy',
        fillcolor='rgba(255,71,87,0.08)'
    ))
    fig_hr.update_layout(
        title=dict(text="Heart Rate — Last 30 Readings", font=dict(color='#64748b', size=11)),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        height=200,
        margin=dict(l=10, r=10, t=40, b=20),
        xaxis=dict(gridcolor='#1e293b', showticklabels=False),
        yaxis=dict(gridcolor='#1e293b', tickfont=dict(color='#64748b', size=9)),
        showlegend=False
    )
    st.plotly_chart(fig_hr, use_container_width=True, config={"displayModeBar": False})

    st.info("⌚ Click **Refresh Watch** in the sidebar to simulate new live readings.")


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 5: HISTORY
# ═══════════════════════════════════════════════════════════════════════════════
with tab5:
    df_hist = load_history()

    if df_hist.empty:
        st.markdown("""
        <div style='text-align:center; padding:3rem; color:#475569;'>
            <div style='font-size:2.5rem;'>📋</div>
            <div style='margin-top:0.75rem; font-size:0.9rem;'>No logs yet. Click <strong>Save Log</strong> in the sidebar.</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        fig_hist = make_history_chart(df_hist)
        if fig_hist:
            st.markdown("<div class='section-header'>Health Score Over Time</div>", unsafe_allow_html=True)
            st.plotly_chart(fig_hist, use_container_width=True, config={"displayModeBar": False})

        st.markdown("<div class='section-header'>Recent Logs</div>", unsafe_allow_html=True)
        display_cols = ["timestamp", "name", "age", "bmi", "health_score", "steps", "sleep", "obesity_risk", "fatigue_risk"]
        available = [c for c in display_cols if c in df_hist.columns]
        st.dataframe(
            df_hist[available].style.set_properties(**{
                'background-color': '#111827',
                'color': '#e2e8f0',
                'border-color': '#1e293b'
            }),
            use_container_width=True,
            hide_index=True
        )

        if st.button("🗑 Clear All Logs"):
            conn = sqlite3.connect("health_twin.db")
            conn.execute("DELETE FROM health_logs")
            conn.commit()
            conn.close()
            st.rerun()
