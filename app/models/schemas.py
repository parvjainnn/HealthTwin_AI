from pydantic import BaseModel, Field
from typing import Optional, List


# ── Diabetes ──────────────────────────────────────────────
class DiabetesInput(BaseModel):
    pregnancies: float = Field(..., description="Number of pregnancies")
    glucose: float = Field(..., description="Plasma glucose concentration")
    blood_pressure: float = Field(..., description="Diastolic blood pressure (mm Hg)")
    skin_thickness: float = Field(..., description="Triceps skin fold thickness (mm)")
    insulin: float = Field(..., description="2-Hour serum insulin (mu U/ml)")
    bmi: float = Field(..., description="Body mass index")
    diabetes_pedigree_function: float = Field(..., description="Diabetes pedigree function")
    age: float = Field(..., description="Age in years")


# ── Heart Disease ─────────────────────────────────────────
class HeartDiseaseInput(BaseModel):
    age: float = Field(..., description="Age of the patient")
    sex: float = Field(..., description="Sex (1 = male, 0 = female)")
    chest_pain_type: float = Field(..., description="Chest pain type (0-3)")
    resting_bp: float = Field(..., description="Resting blood pressure")
    cholesterol: float = Field(..., description="Serum cholesterol in mg/dl")
    fasting_bs: float = Field(..., description="Fasting blood sugar > 120 mg/dl (1=true, 0=false)")
    resting_ecg: float = Field(..., description="Resting ECG results (0-2)")
    max_hr: float = Field(..., description="Maximum heart rate achieved")
    exercise_angina: float = Field(..., description="Exercise induced angina (1=yes, 0=no)")
    oldpeak: float = Field(..., description="ST depression induced by exercise")


# ── Parkinson's Disease ───────────────────────────────────
class ParkinsonsInput(BaseModel):
    fo: float = Field(..., description="MDVP:Fo(Hz) - Average vocal fundamental frequency")
    fhi: float = Field(..., description="MDVP:Fhi(Hz) - Maximum vocal fundamental frequency")
    flo: float = Field(..., description="MDVP:Flo(Hz) - Minimum vocal fundamental frequency")
    jitter_percent: float = Field(..., description="MDVP:Jitter(%)")
    jitter_abs: float = Field(..., description="MDVP:Jitter(Abs)")
    rap: float = Field(..., description="MDVP:RAP")
    ppq: float = Field(..., description="MDVP:PPQ")
    ddp: float = Field(..., description="Jitter:DDP")
    shimmer: float = Field(..., description="MDVP:Shimmer")
    shimmer_db: float = Field(..., description="MDVP:Shimmer(dB)")
    apq3: float = Field(..., description="Shimmer:APQ3")
    apq5: float = Field(..., description="Shimmer:APQ5")
    apq: float = Field(..., description="MDVP:APQ")
    dda: float = Field(..., description="Shimmer:DDA")
    nhr: float = Field(..., description="NHR")
    hnr: float = Field(..., description="HNR")
    rpde: float = Field(..., description="RPDE")
    dfa: float = Field(..., description="DFA")
    spread1: float = Field(..., description="spread1")
    spread2: float = Field(..., description="spread2")
    d2: float = Field(..., description="D2")
    ppe: float = Field(..., description="PPE")


# ── Shared Response ───────────────────────────────────────
class PredictionResponse(BaseModel):
    disease: str
    prediction: int
    risk_label: str
    confidence: Optional[float] = None
    message: str


# ── Chatbot ───────────────────────────────────────────────
class ChatRequest(BaseModel):
    message: str = Field(..., description="User message")
    history: Optional[List[dict]] = Field(default=[], description="Chat history")


class SourceDocument(BaseModel):
    content: str = Field(..., description="Snippet of the source document")
    metadata: dict = Field(default={}, description="Source metadata (page, file, etc.)")


class ChatResponse(BaseModel):
    reply: str
    model: str
    sources: Optional[List[SourceDocument]] = Field(default=[], description="RAG source documents")


# ── Dashboard ─────────────────────────────────────────────
class DashboardInput(BaseModel):
    name: str = Field(default="User", description="User name")
    age: int = Field(..., ge=10, le=100, description="Age")
    gender: str = Field(default="Male", description="Gender")
    weight: float = Field(..., gt=0, description="Weight in kg")
    height: float = Field(..., gt=0, description="Height in cm")
    steps: int = Field(default=6500, ge=0, description="Daily steps")
    sleep: float = Field(default=6.5, ge=0, le=12, description="Sleep hours")
    water: float = Field(default=2.0, ge=0, le=10, description="Water intake in litres")
    heart_rate: int = Field(default=72, ge=30, le=220, description="Resting heart rate bpm")


class ScoreBreakdown(BaseModel):
    bmi_pts: int
    sleep_pts: int
    step_pts: int
    water_pts: int
    hr_pts: int


class DashboardAnalysis(BaseModel):
    bmi: float
    bmi_category: str
    bmi_color: str
    health_score: float
    breakdown: ScoreBreakdown
    obesity_risk: str
    obesity_prob: int
    fatigue_risk: str
    fatigue_prob: int


class WatchData(BaseModel):
    heart_rate: int
    spo2: float
    stress: int
    live_steps: int
    calories: int


class HealthLogEntry(BaseModel):
    timestamp: str
    name: str
    age: int
    gender: str
    weight: float
    height: float
    steps: int
    sleep: float
    water: float
    heart_rate: int
    bmi: float
    health_score: float
    obesity_risk: str
    fatigue_risk: str


class AdvisorRequest(BaseModel):
    question: str = Field(..., description="Health question")
    user_data: dict = Field(default={}, description="Current user vitals context")


class AdvisorResponse(BaseModel):
    reply: str
