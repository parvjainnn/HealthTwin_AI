# HealthTwin — Build Walkthrough

## What Was Built

A unified **FastAPI + modern HTML/CSS/JS** web application combining 3 disease prediction models and an Ollama-powered medical chatbot.

### Files Created

| Component | File | Purpose |
|-----------|------|---------|
| **Backend** | [main.py](file:///c:/Users/ASUS/Documents/WebD/HackathonProject/healthtwin/app/main.py) | FastAPI app, CORS, static files, routes |
| | [schemas.py](file:///c:/Users/ASUS/Documents/WebD/HackathonProject/healthtwin/app/models/schemas.py) | Pydantic models for all 3 diseases + chat |
| | [prediction.py](file:///c:/Users/ASUS/Documents/WebD/HackathonProject/healthtwin/app/services/prediction.py) | Cached model loading + inference |
| | [chatbot.py](file:///c:/Users/ASUS/Documents/WebD/HackathonProject/healthtwin/app/services/chatbot.py) | Ollama HTTP client with medical system prompt |
| | [predictions.py](file:///c:/Users/ASUS/Documents/WebD/HackathonProject/healthtwin/app/routers/predictions.py) | API routes: `/api/predict/{disease}` |
| | [chatbot.py](file:///c:/Users/ASUS/Documents/WebD/HackathonProject/healthtwin/app/routers/chatbot.py) | API route: `/api/chat` |
| **Frontend** | [index.html](file:///c:/Users/ASUS/Documents/WebD/HackathonProject/healthtwin/app/static/index.html) | SPA with 5 sections |
| | [styles.css](file:///c:/Users/ASUS/Documents/WebD/HackathonProject/healthtwin/app/static/css/styles.css) | Dark glassmorphism design system |
| | [app.js](file:///c:/Users/ASUS/Documents/WebD/HackathonProject/healthtwin/app/static/js/app.js) | SPA routing, forms, chat |

## Verification Results

### ✅ All 3 Prediction Endpoints Working

| Endpoint | Test Input | Result | Confidence |
|----------|-----------|--------|------------|
| `POST /api/predict/diabetes` | Pregnancies=6, Glucose=148, etc. | **High Risk** (prediction=1) | — |
| `POST /api/predict/heart` | Age=55, ChestPain=3, BP=140, etc. | **No Heart Disease** (prediction=0) | 57.4% |
| `POST /api/predict/parkinsons` | Fo=119.99, Fhi=157.30, etc. | **Parkinson's Detected** (prediction=1) | 99.9% |

### ✅ Frontend Serving
- `GET /` → Returns [index.html](file:///c:/Users/ASUS/Documents/WebD/HackathonProject/healthtwin/app/static/index.html) (200 OK, `text/html`)
- `GET /health` → Returns `{"status": "healthy", "app": "HealthTwin"}`

## How to Run

```bash
cd c:\Users\ASUS\Documents\WebD\HackathonProject\healthtwin
python -m uvicorn app.main:app --reload
# Open http://localhost:8000
```

### For the chatbot to work:
```bash
ollama serve          # Start Ollama
ollama pull llama3.2  # Pull a model
```

> [!NOTE]
> Existing project files (Diabetes/, Heart_disease/, Parkinson_disease/, medical-chatbot/) were **not modified**. Only their [.pkl](file:///c:/Users/ASUS/Documents/WebD/HackathonProject/healthtwin/Diabetes/diabetes_model.pkl) model files are loaded by the new backend.
