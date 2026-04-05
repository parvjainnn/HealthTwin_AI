# 🧬 AI Health Twin — Personalized Health Tracker

A full-stack AI health dashboard built with Streamlit, scikit-learn, and a smart rule-based AI advisor.

---

## 🚀 Quick Start

### 1. Clone / download the project
```bash
cd ai_health_twin
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Run the app
```bash
streamlit run app.py
```

The app opens at **http://localhost:8501**

---

## ✨ Features

| Feature | Description |
|---|---|
| 📊 Dashboard | BMI, Health Score, Steps, Sleep, Hydration — all at a glance |
| 🤖 AI Advisor | Contextual chat using your personal health data |
| ⚠️ Risk Analysis | ML-powered Obesity + Fatigue risk (Random Forest) |
| ⌚ Smart Watch | Simulated live HR, SpO₂, stress, calories |
| 📈 History | SQLite log with health score trends over time |

---

## 🏗️ Architecture

```
app.py                  ← All-in-one Streamlit app
  ├── Sidebar           ← User input (age, weight, steps, sleep, water, HR)
  ├── Tab 1: Dashboard  ← KPIs, gauge, radar, bar breakdown
  ├── Tab 2: AI Advisor ← Chat with rule-based health AI
  ├── Tab 3: Risk       ← ML risk gauges + explanations
  ├── Tab 4: Watch      ← Simulated smartwatch live data
  └── Tab 5: History    ← SQLite logs + trend chart

health_twin.db          ← Auto-created SQLite database
```

---

## 🧠 Health Score Formula

| Component | Max Points | Criteria |
|---|---|---|
| BMI | 25 | 18.5–24.9 = full marks |
| Sleep | 25 | 7–9h = full marks |
| Steps | 25 | 10,000+ = full marks |
| Water | 15 | 2–3.5L = full marks |
| Heart Rate | 10 | 60–80 bpm = full marks |
| **Total** | **100** | |

---

## 🤖 AI Advisor Topics

Ask the advisor about:
- "Why am I feeling tired?"
- "What should I eat?"
- "How can I improve my health score?"
- "Tell me about my weight status"
- "Give me sleep tips"
- "Am I hydrated enough?"
- "What's my heart rate status?"

---

## 🔬 ML Risk Model

- Algorithm: **Random Forest Classifier**
- Training data: 800 synthetic health profiles
- Features: BMI, Sleep, Steps, Water, Age
- Outputs: Obesity Risk %, Fatigue Risk %

---

## 💾 Data Storage

- Health logs saved to `health_twin.db` (SQLite)
- View history in the **History** tab
- Clear logs anytime with the "Clear All Logs" button

---

## 📦 Optional Enhancements

To add OpenAI-powered AI responses, replace the `get_ai_response()` function in `app.py` with:

```python
import openai
openai.api_key = "your-key-here"

def get_ai_response(question, user_data):
    prompt = f"User health data: {user_data}\n\nQuestion: {question}\n\nProvide personalized health advice:"
    response = openai.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content
```

---

## 📋 Requirements

- Python 3.9+
- See `requirements.txt` for packages
