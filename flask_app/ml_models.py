"""ML models for health risk analysis and disease prediction."""
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler

# ─── Singleton cache ────────────────────────────────────────────────────────
_risk_models = None


def _build_risk_models():
    global _risk_models
    if _risk_models is not None:
        return _risk_models

    np.random.seed(42)
    n = 800

    bmi_s = np.random.normal(24, 5, n).clip(15, 45)
    sleep_s = np.random.normal(6.5, 1.5, n).clip(3, 10)
    steps_s = np.random.randint(1000, 18000, n).astype(float)
    water_s = np.random.normal(2, 0.8, n).clip(0.5, 5)
    age_s = np.random.randint(18, 75, n).astype(float)

    obesity_y = ((bmi_s > 27) | ((bmi_s > 25) & (steps_s < 5000))).astype(int)
    fatigue_y = ((sleep_s < 6) | ((steps_s < 4000) & (sleep_s < 7)) | (water_s < 1.5)).astype(int)

    X = np.column_stack([bmi_s, sleep_s, steps_s, water_s, age_s])
    scaler = StandardScaler()
    Xs = scaler.fit_transform(X)

    ob_clf = RandomForestClassifier(n_estimators=60, random_state=42)
    ob_clf.fit(Xs, obesity_y)

    fat_clf = RandomForestClassifier(n_estimators=60, random_state=42)
    fat_clf.fit(Xs, fatigue_y)

    _risk_models = (ob_clf, fat_clf, scaler)
    return _risk_models


def predict_risks(bmi, sleep, steps, water, age):
    ob_clf, fat_clf, scaler = _build_risk_models()
    X = scaler.transform([[bmi, sleep, steps, water, age]])
    ob_prob = ob_clf.predict_proba(X)[0][1]
    fat_prob = fat_clf.predict_proba(X)[0][1]

    def risk_label(p):
        if p < 0.35:
            return "Low"
        elif p < 0.65:
            return "Medium"
        else:
            return "High"

    return risk_label(ob_prob), risk_label(fat_prob), round(ob_prob, 4), round(fat_prob, 4)


# ─── Health Score ────────────────────────────────────────────────────────────
def calc_bmi(weight, height_cm):
    h = height_cm / 100
    return round(weight / (h * h), 1)


def bmi_category(bmi):
    if bmi < 18.5:
        return "Underweight", "#8b5cf6"
    elif bmi < 25:
        return "Normal", "#00ff88"
    elif bmi < 30:
        return "Overweight", "#ffa500"
    else:
        return "Obese", "#ff4757"


def calc_health_score(bmi, sleep, steps, water, heart_rate=None):
    if 18.5 <= bmi <= 24.9:
        bmi_pts = 25
    elif 17 <= bmi < 18.5 or 25 <= bmi < 27:
        bmi_pts = 18
    elif 15 <= bmi < 17 or 27 <= bmi < 30:
        bmi_pts = 10
    else:
        bmi_pts = 5

    if 7 <= sleep <= 9:
        sleep_pts = 25
    elif 6 <= sleep < 7 or 9 < sleep <= 10:
        sleep_pts = 18
    elif 5 <= sleep < 6:
        sleep_pts = 10
    else:
        sleep_pts = 5

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

    if 2 <= water <= 3.5:
        water_pts = 15
    elif 1.5 <= water < 2:
        water_pts = 10
    elif water >= 3.5:
        water_pts = 12
    else:
        water_pts = 5

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


# ─── Disease Prediction ──────────────────────────────────────────────────────
import os
import pickle

MODELS_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    'Models'
)

BRAIN_TUMOR_MODEL_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    'brain_tumor', 'model.h5'
)

_brain_tumor_model = None
_brain_tumor_labels = ['Glioma', 'Meningioma', 'No Tumor', 'Pituitary']


def _load_model(filename):
    path = os.path.join(MODELS_DIR, filename)
    if os.path.exists(path):
        with open(path, 'rb') as f:
            return pickle.load(f)
    return None


def _get_brain_tumor_model():
    global _brain_tumor_model
    if _brain_tumor_model is not None:
        return _brain_tumor_model
    if not os.path.exists(BRAIN_TUMOR_MODEL_PATH):
        return None
    try:
        import os as _os
        # Suppress TF/absl logging noise
        _os.environ.setdefault('TF_CPP_MIN_LOG_LEVEL', '3')
        import warnings
        warnings.filterwarnings('ignore')

        import tensorflow as tf  # type: ignore
        # compile=False avoids optimizer version mismatches
        _brain_tumor_model = tf.keras.models.load_model(
            BRAIN_TUMOR_MODEL_PATH, compile=False
        )
        return _brain_tumor_model
    except Exception as e:
        # Store a sentinel so we don't retry on every request
        _brain_tumor_model = False
        return None


def predict_diabetes(features):
    model = _load_model('diabetes_model.sav')
    if model is None:
        return {"prediction": "Model not found", "confidence": 0, "risk_level": "Unknown"}
    pred = model.predict([features])[0]
    try:
        prob = model.predict_proba([features])[0][1]
        confidence = round(prob * 100, 1)
    except Exception:
        confidence = 100 if pred else 0
    return {
        "prediction": "Diabetic" if pred else "Not Diabetic",
        "confidence": confidence,
        "risk_level": "High" if pred else "Low"
    }


def predict_heart_disease(features):
    model = _load_model('heart_disease_model.sav')
    if model is None:
        return {"prediction": "Model not found", "confidence": 0, "risk_level": "Unknown"}
    pred = model.predict([features])[0]
    try:
        prob = model.predict_proba([features])[0][1]
        confidence = round(prob * 100, 1)
    except Exception:
        confidence = 100 if pred else 0
    return {
        "prediction": "Heart Disease Detected" if pred else "No Heart Disease",
        "confidence": confidence,
        "risk_level": "High" if pred else "Low"
    }


def predict_brain_tumor(image_bytes):
    """Classify a brain MRI image. image_bytes: raw bytes from uploaded file."""
    model = _get_brain_tumor_model()
    if not model:  # None or False sentinel
        return {"prediction": "Model not available", "confidence": 0,
                "risk_level": "Unknown", "all_probs": {}}
    try:
        import numpy as np
        from PIL import Image
        import io
        img = Image.open(io.BytesIO(image_bytes)).convert('RGB').resize((128, 128))
        arr = np.array(img, dtype='float32') / 255.0
        arr = np.expand_dims(arr, axis=0)  # shape (1,128,128,3)
        probs = model.predict(arr, verbose=0)[0]
        idx = int(np.argmax(probs))
        label = _brain_tumor_labels[idx]
        confidence = round(float(probs[idx]) * 100, 1)
        all_probs = {_brain_tumor_labels[i]: round(float(probs[i]) * 100, 1)
                     for i in range(len(_brain_tumor_labels))}
        risk_level = 'Low' if label == 'No Tumor' else 'High'
        return {
            "prediction": label,
            "confidence": confidence,
            "risk_level": risk_level,
            "all_probs": all_probs
        }
    except Exception as e:
        return {"prediction": f"Error: {e}", "confidence": 0,
                "risk_level": "Unknown", "all_probs": {}}


# ─── Smartwatch simulation ───────────────────────────────────────────────────
import random


def simulate_watch_data(base_hr=72):
    return {
        "heart_rate": base_hr + random.randint(-8, 12),
        "spo2": round(random.uniform(96, 99.5), 1),
        "stress": random.randint(20, 75),
        "live_steps": random.randint(200, 800) * 8,
        "calories": random.randint(1400, 2200),
        "hr_series": [base_hr + random.randint(-10, 10) for _ in range(30)]
    }
