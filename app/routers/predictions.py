from fastapi import APIRouter, HTTPException
from app.models.schemas import (
    DiabetesInput,
    HeartDiseaseInput,
    ParkinsonsInput,
    PredictionResponse,
)
from app.services.prediction import (
    predict_diabetes,
    predict_heart_disease,
    predict_parkinsons,
)

router = APIRouter(prefix="/api/predict", tags=["predictions"])


@router.post("/diabetes", response_model=PredictionResponse)
async def diabetes_prediction(data: DiabetesInput):
    """Predict diabetes risk based on input features."""
    try:
        features = [
            data.pregnancies,
            data.glucose,
            data.blood_pressure,
            data.skin_thickness,
            data.insulin,
            data.bmi,
            data.diabetes_pedigree_function,
            data.age,
        ]
        result = predict_diabetes(features)
        return PredictionResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")


@router.post("/heart", response_model=PredictionResponse)
async def heart_disease_prediction(data: HeartDiseaseInput):
    """Predict heart disease based on input features."""
    try:
        features = [
            data.age,
            data.sex,
            data.chest_pain_type,
            data.resting_bp,
            data.cholesterol,
            data.fasting_bs,
            data.resting_ecg,
            data.max_hr,
            data.exercise_angina,
            data.oldpeak,
        ]
        result = predict_heart_disease(features)
        return PredictionResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")


@router.post("/parkinsons", response_model=PredictionResponse)
async def parkinsons_prediction(data: ParkinsonsInput):
    """Predict Parkinson's disease based on voice measurements."""
    try:
        features = [
            data.fo, data.fhi, data.flo,
            data.jitter_percent, data.jitter_abs,
            data.rap, data.ppq, data.ddp,
            data.shimmer, data.shimmer_db,
            data.apq3, data.apq5, data.apq, data.dda,
            data.nhr, data.hnr,
            data.rpde, data.dfa,
            data.spread1, data.spread2,
            data.d2, data.ppe,
        ]
        result = predict_parkinsons(features)
        return PredictionResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")
