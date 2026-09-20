import os
import pickle
import numpy as np
from functools import lru_cache
from pathlib import Path

# Base directory (project root)
BASE_DIR = Path(__file__).resolve().parent.parent.parent


@lru_cache(maxsize=6)
def _load_pickle(path: str):
    """Load a pickle file with caching."""
    with open(path, "rb") as f:
        return pickle.load(f)


def get_model_and_scaler(disease: str):
    """Return (model, scaler) for the given disease."""
    paths = {
        "diabetes": (
            BASE_DIR / "Models" / "diabetes_model.pkl",
            BASE_DIR / "Models" / "diabetes_scaler.pkl",
        ),
        "heart": (
            BASE_DIR / "Models" / "heart_disease_model.pkl",
            BASE_DIR / "Models" / "heart_disease_scaler.pkl",
        ),
        "parkinsons": (
            BASE_DIR / "Parkinson_disease" / "Parkinson_disease_model.pkl",
            BASE_DIR / "Parkinson_disease" / "Parkinson_disease_scaler.pkl",
        ),
    }
    model_path, scaler_path = paths[disease]
    model = _load_pickle(str(model_path))
    scaler = _load_pickle(str(scaler_path))
    return model, scaler


def predict_diabetes(features: list[float]) -> dict:
    model, scaler = get_model_and_scaler("diabetes")
    arr = np.array(features).reshape(1, -1)
    arr_scaled = scaler.transform(arr)
    prediction = int(model.predict(arr_scaled)[0])
    
    confidence = None
    if hasattr(model, "predict_proba"):
        proba = model.predict_proba(arr_scaled)[0]
        confidence = round(float(proba[prediction]) * 100, 1)
    
    risk_label = "High Risk" if prediction == 1 else "Low Risk"
    message = (
        "The model indicates a high risk of diabetes. Please consult a healthcare professional."
        if prediction == 1
        else "The model indicates a low risk of diabetes. Maintain a healthy lifestyle!"
    )
    return {
        "disease": "Diabetes",
        "prediction": prediction,
        "risk_label": risk_label,
        "confidence": confidence,
        "message": message,
    }


def predict_heart_disease(features: list[float]) -> dict:
    model, scaler = get_model_and_scaler("heart")
    arr = np.array(features).reshape(1, -1)
    arr_scaled = scaler.transform(arr)
    prediction = int(model.predict(arr_scaled)[0])
    
    confidence = None
    if hasattr(model, "predict_proba"):
        proba = model.predict_proba(arr_scaled)[0]
        confidence = round(float(proba[prediction]) * 100, 1)
    
    risk_label = "Heart Disease Detected" if prediction == 1 else "No Heart Disease"
    message = (
        "The model indicates signs of heart disease. Seek medical attention promptly."
        if prediction == 1
        else "The model shows no signs of heart disease. Keep up the healthy habits!"
    )
    return {
        "disease": "Heart Disease",
        "prediction": prediction,
        "risk_label": risk_label,
        "confidence": confidence,
        "message": message,
    }


def predict_parkinsons(features: list[float]) -> dict:
    model, scaler = get_model_and_scaler("parkinsons")
    arr = np.array(features).reshape(1, -1)
    arr_scaled = scaler.transform(arr)
    prediction = int(model.predict(arr_scaled)[0])
    
    confidence = None
    if hasattr(model, "predict_proba"):
        proba = model.predict_proba(arr_scaled)[0]
        confidence = round(float(proba[prediction]) * 100, 1)
    
    risk_label = "Parkinson's Detected" if prediction == 1 else "No Parkinson's"
    message = (
        "The model indicates signs of Parkinson's disease. Please consult a neurologist."
        if prediction == 1
        else "The model shows no signs of Parkinson's disease."
    )
    return {
        "disease": "Parkinson's Disease",
        "prediction": prediction,
        "risk_label": risk_label,
        "confidence": confidence,
        "message": message,
    }
