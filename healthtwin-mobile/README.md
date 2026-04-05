# HealthTwin Mobile

This folder contains a mobile app scaffold for HealthTwin built with Expo and React Native.

## What it includes

- Home overview screen for the HealthTwin product
- Dashboard screen for vitals analysis and smartwatch simulation
- AI chat screen wired to `/api/chat`
- Prediction screen wired to `/api/predict/diabetes` and `/api/predict/heart`
- Records screen placeholder for the next mobile phase
- Light and dark theme toggle inside the app

## Backend target

The mobile app is designed to talk to the FastAPI layer in `app/`, because those routes are already mobile-friendly and do not depend on Flask login sessions.

Useful routes:

- `/api/dashboard/analyze`
- `/api/dashboard/watch`
- `/api/chat`
- `/api/predict/diabetes`
- `/api/predict/heart`

## Start the API

From the project root:

```powershell
cd C:\Users\preet\OneDrive\Desktop\healthtwin
Set-ExecutionPolicy -Scope Process Bypass
.\venv\Scripts\Activate.ps1
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

## Start the mobile app

From this folder:

```powershell
cd C:\Users\preet\OneDrive\Desktop\healthtwin\healthtwin-mobile
npm install
npm start
```

## Notes

- On a physical phone, replace `http://127.0.0.1:8000` in the app with your computer's local IP address.
- The app includes fallback demo responses when the backend is unavailable so the UI remains usable during development.
- A good next step is adding token-based auth plus document/image picking for records and MRI upload flows.
