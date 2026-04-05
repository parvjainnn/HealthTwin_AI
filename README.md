# HealthTwin

HealthTwin is a Flask-based health platform that combines:

- health vitals tracking and scoring
- disease prediction modules
- AI-powered health chat
- smartwatch simulation
- patient document storage for bills and prescriptions

The goal is to give patients a single place to monitor wellness signals, explore risk predictions, and keep important health records available for future visits.

## Current Features

- User registration and login
- Health dashboard with vitals analysis
- Historical health logs and charts
- AI health advisor chat
- Disease prediction pages for diabetes, heart disease, Parkinson's, and brain tumor workflows
- Medical records vault for uploading bills and prescriptions

## Run Locally

Use PowerShell from the project root:

```powershell
cd C:\Users\preet\OneDrive\Desktop\healthtwin
Set-ExecutionPolicy -Scope Process Bypass
.\venv\Scripts\Activate.ps1
python run.py
```

Open:

```text
http://127.0.0.1:5000
```

If the virtual environment is not ready yet:

```powershell
python -m venv venv
Set-ExecutionPolicy -Scope Process Bypass
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
python run.py
```

## Main Project Areas

- `flask_app/` - Flask app factory, routes, auth, prediction logic, and database helpers
- `templates/` - Jinja templates for dashboard, history, predictions, login, and records
- `static_flask/` - shared CSS and JavaScript
- `healthtwin-mobile/` - Expo React Native mobile app scaffold for dashboard, chat, and predictions
- `Models/` and disease folders - ML assets and notebooks/scripts for prediction modules
- `healthtwin_flask.db` - SQLite app database

## Reference Projects

These projects are useful benchmarks for where HealthTwin can grow next:

1. Fasten Health
   Personal/family health record aggregation, provider connectivity, and patient-controlled records.
   GitHub: https://github.com/fastenhealth/fasten-onprem
   Docs: https://docs.fastenhealth.com/

2. OpenMRS
   A mature open-source medical record ecosystem with strong modular design and standards-based interoperability.
   GitHub: https://github.com/openmrs
   Website: https://openmrs.org/

3. OpenEMR
   A large open-source EHR and patient portal reference for appointments, billing, messaging, and downloadable reports.
   GitHub: https://github.com/openemr/openemr
   Patient portal docs: https://www.open-emr.org/wiki/index.php/Patient_Portal

4. LibreHealth EHR
   A clinically focused open-source EHR with emphasis on extensibility and healthcare workflows.
   GitHub: https://github.com/LibreHealthIO/lh-ehr
   Website: https://librehealth.io/

## Improvement Ideas Inspired By Similar Projects

- Add a structured patient timeline that combines health logs, prescriptions, bills, reports, and model results
- Introduce document categories beyond bills and prescriptions, such as lab reports and discharge summaries
- Add patient reminders for medication, follow-ups, hydration, sleep, and appointments
- Move document storage from local disk to cloud-backed storage for better durability
- Add role-based views for patient, caregiver, and doctor access
- Add standards-friendly export or import support such as FHIR-style resource mapping
- Add secure messaging and appointment workflows inspired by patient portal systems
- Add OCR extraction for prescriptions and bills so uploaded files become searchable

## Suggested Next Milestones

1. Build a unified patient record timeline page
2. Add OCR and metadata extraction for uploaded medical documents
3. Improve data model for medications, visits, and lab results
4. Add notifications and reminder scheduling
5. Add a cleaner API layer for future mobile or React frontend support

## Notes

- This project currently uses SQLite for local development.
- Uploaded patient documents are stored on disk under `uploads/patient_documents`.
- HealthTwin is for learning and prototyping, not for clinical diagnosis or production medical use.
