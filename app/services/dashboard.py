"""
Dashboard service — health analytics, smartwatch sim, history, and AI advisor.
Ported from the Streamlit dashboard reference.
"""

import os
import random
import sqlite3
from datetime import datetime
from pathlib import Path

# ── Database ────────────────────────────────────────────────────────────────────
DB_PATH = Path(__file__).resolve().parent.parent.parent / "health_twin.db"


def _get_conn():
    return sqlite3.connect(str(DB_PATH))


def init_db():
    conn = _get_conn()
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


# Init DB on import
init_db()


# ── BMI helpers ─────────────────────────────────────────────────────────────────
def calc_bmi(weight: float, height_cm: float) -> float:
    h = height_cm / 100
    return round(weight / (h * h), 1)


def bmi_category(bmi: float) -> tuple[str, str]:
    if bmi < 18.5:
        return "Underweight", "#8b5cf6"
    elif bmi < 25:
        return "Normal", "#00ff88"
    elif bmi < 30:
        return "Overweight", "#ffa500"
    else:
        return "Obese", "#ff4757"


# ── Health score ────────────────────────────────────────────────────────────────
def calc_health_score(bmi, sleep, steps, water, heart_rate=None):
    # BMI component (0-25)
    if 18.5 <= bmi <= 24.9:
        bmi_pts = 25
    elif 17 <= bmi < 18.5 or 25 <= bmi < 27:
        bmi_pts = 18
    elif 15 <= bmi < 17 or 27 <= bmi < 30:
        bmi_pts = 10
    else:
        bmi_pts = 5

    # Sleep component (0-25)
    if 7 <= sleep <= 9:
        sleep_pts = 25
    elif 6 <= sleep < 7 or 9 < sleep <= 10:
        sleep_pts = 18
    elif 5 <= sleep < 6:
        sleep_pts = 10
    else:
        sleep_pts = 5

    # Steps component (0-25)
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

    # Water component (0-15)
    if 2 <= water <= 3.5:
        water_pts = 15
    elif 1.5 <= water < 2:
        water_pts = 10
    elif water >= 3.5:
        water_pts = 12
    else:
        water_pts = 5

    # Heart rate component (0-10)
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


# ── Risk assessment (rule-based) ────────────────────────────────────────────────
def _risk_label(prob: float) -> str:
    if prob < 0.35:
        return "Low"
    elif prob < 0.65:
        return "Medium"
    else:
        return "High"


def predict_risks(bmi, sleep, steps, water, age):
    """Simplified rule-based risk. Mirrors the RF model's decision boundaries."""
    # Obesity risk
    ob_score = 0.0
    if bmi > 30:
        ob_score += 0.45
    elif bmi > 27:
        ob_score += 0.30
    elif bmi > 25:
        ob_score += 0.15
    if steps < 3000:
        ob_score += 0.25
    elif steps < 5000:
        ob_score += 0.15
    if water < 1.5:
        ob_score += 0.10
    if age > 50:
        ob_score += 0.05
    ob_score = min(1.0, ob_score)

    # Fatigue risk
    fat_score = 0.0
    if sleep < 5:
        fat_score += 0.45
    elif sleep < 6:
        fat_score += 0.30
    elif sleep < 7:
        fat_score += 0.15
    if steps < 3000:
        fat_score += 0.20
    elif steps < 4000:
        fat_score += 0.15
    if water < 1.0:
        fat_score += 0.20
    elif water < 1.5:
        fat_score += 0.10
    fat_score = min(1.0, fat_score)

    return {
        "obesity_risk": _risk_label(ob_score),
        "obesity_prob": int(ob_score * 100),
        "fatigue_risk": _risk_label(fat_score),
        "fatigue_prob": int(fat_score * 100),
    }


# ── Full analysis ───────────────────────────────────────────────────────────────
def analyze(data: dict) -> dict:
    bmi = calc_bmi(data["weight"], data["height"])
    cat, color = bmi_category(bmi)
    score, bmi_pts, sleep_pts, step_pts, water_pts, hr_pts = calc_health_score(
        bmi, data["sleep"], data["steps"], data["water"], data.get("heart_rate")
    )
    risks = predict_risks(bmi, data["sleep"], data["steps"], data["water"], data["age"])
    return {
        "bmi": bmi,
        "bmi_category": cat,
        "bmi_color": color,
        "health_score": score,
        "breakdown": {
            "bmi_pts": bmi_pts,
            "sleep_pts": sleep_pts,
            "step_pts": step_pts,
            "water_pts": water_pts,
            "hr_pts": hr_pts,
        },
        **risks,
    }


# ── Smartwatch simulation ──────────────────────────────────────────────────────
def simulate_watch(base_hr: int = 72) -> dict:
    hr = base_hr + random.randint(-8, 12)
    spo2 = round(random.uniform(96, 99.5), 1)
    stress = random.randint(20, 75)
    live_steps = random.randint(200, 800) * 8
    calories = random.randint(1400, 2200)
    return {
        "heart_rate": hr,
        "spo2": spo2,
        "stress": stress,
        "live_steps": live_steps,
        "calories": calories,
    }


# ── History ─────────────────────────────────────────────────────────────────────
def save_log(data: dict):
    conn = _get_conn()
    c = conn.cursor()
    c.execute("""
        INSERT INTO health_logs
        (timestamp,name,age,gender,weight,height,steps,sleep,water,heart_rate,bmi,health_score,obesity_risk,fatigue_risk)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)
    """, (
        data.get("timestamp", datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
        data["name"], data["age"], data["gender"],
        data["weight"], data["height"], data["steps"], data["sleep"],
        data["water"], data["heart_rate"], data["bmi"],
        data["health_score"], data["obesity_risk"], data["fatigue_risk"],
    ))
    conn.commit()
    conn.close()


def get_history(limit: int = 30) -> list[dict]:
    if not DB_PATH.exists():
        return []
    conn = _get_conn()
    conn.row_factory = sqlite3.Row
    rows = conn.execute(
        "SELECT * FROM health_logs ORDER BY timestamp DESC LIMIT ?", (limit,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def clear_history():
    conn = _get_conn()
    conn.execute("DELETE FROM health_logs")
    conn.commit()
    conn.close()


# ── AI Advisor (rule-based contextual) ──────────────────────────────────────────
def get_advisor_response(question: str, user_data: dict) -> str:
    q = question.lower()

    bmi = user_data.get("bmi", 22)
    sleep = user_data.get("sleep", 7)
    steps = user_data.get("steps", 7000)
    water = user_data.get("water", 2)
    heart_rate = user_data.get("heart_rate", 70)
    age = user_data.get("age", 30)
    health_score = user_data.get("health_score", 70)
    ob_risk = user_data.get("obesity_risk", "Low")
    fat_risk = user_data.get("fatigue_risk", "Low")
    name = user_data.get("name", "there")
    bmi_cat, _ = bmi_category(bmi) if isinstance(bmi, (int, float)) else ("Unknown", "#ccc")

    responses = []

    if any(k in q for k in ["tired", "fatigue", "energy", "exhaust", "sleepy"]):
        if sleep < 6:
            responses.append(f"🛌 Sleep Deficit Detected — You're averaging only {sleep}h. Your body needs 7–9 hours. Consider a consistent bedtime 30 minutes earlier each week.")
        if steps < 4000:
            responses.append(f"🚶 Sedentary Alert — Low activity ({steps:,} steps) reduces circulation. Even a 15-minute walk boosts energy.")
        if water < 1.5:
            responses.append(f"💧 Dehydration Risk — At {water}L/day you may be mildly dehydrated, causing fatigue.")
        if not responses:
            responses.append(f"✅ Your vitals look reasonable! Fatigue could stem from stress, screen time, or diet. Try reducing blue light 1h before bed.")

    elif any(k in q for k in ["weight", "bmi", "obese", "fat", "slim", "overweight"]):
        responses.append(f"⚖️ Your BMI is {bmi} ({bmi_cat}). ")
        if bmi > 25:
            deficit = round((bmi - 24.9) * ((user_data.get("height", 170) / 100) ** 2), 1)
            responses.append(f"Losing ~{deficit}kg would bring you into the healthy range. A 500-calorie daily deficit achieves ~0.5kg/week.")
        elif bmi < 18.5:
            responses.append("You're underweight. Aim to add 300–500 kcal/day through protein-rich whole foods.")
        else:
            responses.append("You're in the healthy BMI range — maintain it with regular activity and balanced nutrition.")

    elif any(k in q for k in ["sleep", "insomnia", "rest", "nap"]):
        if sleep < 7:
            responses.append(f"😴 You're getting {sleep}h — below the 7–9h recommendation. Try: no caffeine after 2pm, bedroom temperature 65–68°F, consistent wake times.")
        else:
            responses.append(f"🌙 Your {sleep}h sleep is within the healthy range. Maintain quality by avoiding alcohol within 3h of bedtime.")

    elif any(k in q for k in ["exercise", "steps", "active", "workout", "walk", "run"]):
        if steps < 5000:
            responses.append(f"🏃 Low Activity — {steps:,} steps is below WHO guidelines. Start with +1,000 steps/week.")
        elif steps >= 10000:
            responses.append(f"🔥 Great Activity! {steps:,} steps is excellent. Add strength training 2–3x/week.")
        else:
            responses.append(f"👟 Decent Activity — {steps:,} steps. Targeting 10,000 would maximize health benefits.")

    elif any(k in q for k in ["water", "hydrat", "drink", "thirst"]):
        if water < 2:
            responses.append(f"💧 Increase Hydration — {water}L is below recommended. Aim for 2.5–3L daily.")
        else:
            responses.append(f"✅ Good Hydration — {water}L is on target. Keep it consistent throughout the day.")

    elif any(k in q for k in ["heart", "bp", "blood pressure", "cardiac", "pulse"]):
        if heart_rate and heart_rate > 90:
            responses.append(f"❤️ Elevated Resting HR ({heart_rate} bpm) — Normal is 60–80 bpm. Consider 30-min cardio 3x/week.")
        elif heart_rate:
            responses.append(f"✅ Heart Rate Normal ({heart_rate} bpm). Regular aerobic exercise keeps it optimal.")

    elif any(k in q for k in ["diet", "eat", "food", "nutrition", "calories"]):
        responses.append(f"🥗 Nutrition for BMI {bmi} ({bmi_cat}): ")
        if bmi > 25:
            responses.append("Focus on high-protein, low-glycemic diet. Prioritize vegetables, lean proteins, complex carbs.")
        elif bmi < 18.5:
            responses.append("Increase caloric density with nuts, avocados, legumes, and whole grains.")
        else:
            responses.append("Maintain a balanced Mediterranean-style diet. 50% vegetables, 25% whole grains, 25% lean proteins.")

    elif any(k in q for k in ["score", "health", "overall", "summary", "status"]):
        grade = "Excellent 🌟" if health_score >= 80 else "Good 👍" if health_score >= 65 else "Fair ⚠️" if health_score >= 50 else "Needs Attention 🔴"
        responses.append(f"📊 Health Score: {health_score}/100 — {grade}. Reflects BMI ({bmi_cat}), sleep ({sleep}h), activity ({steps:,} steps), hydration ({water}L).")
        if health_score < 70:
            lowest = min([("sleep", sleep / 9), ("steps", steps / 10000), ("water", water / 2.5)], key=lambda x: x[1])
            responses.append(f"⚡ Biggest opportunity: improve your {lowest[0]}.")

    elif any(k in q for k in ["advice", "recommend", "tip", "suggest", "help", "improve"]):
        tips = []
        if sleep < 7:
            tips.append(f"• Sleep: add 30 min earlier bedtime (currently {sleep}h, target 7–8h)")
        if steps < 7000:
            tips.append(f"• Activity: add a 20-min walk to reach 7,000+ steps (currently {steps:,})")
        if water < 2:
            tips.append(f"• Hydration: drink 1 more glass/hour (currently {water}L, target 2.5L)")
        if bmi > 25:
            tips.append("• Weight: reduce 200 kcal/day for sustainable deficit")
        if not tips:
            tips.append("• Your metrics are solid — maintain consistency")
            tips.append("• Add strength training 2x/week for metabolic health")
        responses.append("🎯 Personalized Recommendations:\n\n" + "\n".join(tips))

    else:
        responses.append(f"🤖 Based on your profile (BMI: {bmi}, Sleep: {sleep}h, Steps: {steps:,}, Score: {health_score}/100), I can advise on: fatigue, weight, sleep, exercise, hydration, diet, heart health, or your overall health score. What would you like to know?")

    return " ".join(responses)
