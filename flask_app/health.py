"""Health dashboard blueprint."""
import os
import uuid
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, send_from_directory
from flask_login import login_required, current_user
from datetime import datetime
from werkzeug.utils import secure_filename
from .database import (
    save_health_log,
    get_health_history,
    get_latest_log,
    delete_all_health_logs,
    save_patient_document,
    get_patient_documents,
    get_patient_document_by_id,
)
from .ml_models import (
    calc_bmi, bmi_category, calc_health_score, predict_risks, simulate_watch_data
)
from .ai_advisor import get_ai_response
from .document_ocr import extract_document_text

health_bp = Blueprint('health', __name__)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UPLOAD_DIR = os.path.join(BASE_DIR, 'uploads', 'patient_documents')
ALLOWED_DOCUMENT_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg', 'webp'}


def _ensure_upload_dir():
    os.makedirs(UPLOAD_DIR, exist_ok=True)


def _allowed_document(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_DOCUMENT_EXTENSIONS


@health_bp.route('/')
def index():
    return render_template('index.html')


@health_bp.route('/dashboard')
@login_required
def dashboard():
    history = get_health_history(current_user.id, limit=50)
    latest = get_latest_log(current_user.id)
    documents = get_patient_documents(current_user.id, limit=10)
    return render_template('dashboard.html', history=history, latest=latest, documents=documents)


@health_bp.route('/api/analyze', methods=['POST'])
@login_required
def analyze():
    data = request.get_json()
    try:
        age = int(data.get('age', 28))
        gender = data.get('gender', 'Male')
        weight = float(data.get('weight', 72))
        height = float(data.get('height', 175))
        steps = int(data.get('steps', 6500))
        sleep = float(data.get('sleep', 6.5))
        water = float(data.get('water', 2.0))
        heart_rate = int(data.get('heart_rate', 72))

        bmi = calc_bmi(weight, height)
        bmi_cat, bmi_color = bmi_category(bmi)
        health_score, bmi_pts, sleep_pts, step_pts, water_pts, hr_pts = calc_health_score(
            bmi, sleep, steps, water, heart_rate
        )
        ob_risk, fat_risk, ob_prob, fat_prob = predict_risks(bmi, sleep, steps, water, age)

        overall_risk = "Low" if health_score > 75 else "Medium" if health_score > 50 else "High"

        return jsonify({
            'bmi': bmi,
            'bmi_cat': bmi_cat,
            'bmi_color': bmi_color,
            'health_score': health_score,
            'bmi_pts': bmi_pts,
            'sleep_pts': sleep_pts,
            'step_pts': step_pts,
            'water_pts': water_pts,
            'hr_pts': hr_pts,
            'obesity_risk': ob_risk,
            'fatigue_risk': fat_risk,
            'ob_prob': round(ob_prob * 100),
            'fat_prob': round(fat_prob * 100),
            'overall_risk': overall_risk,
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@health_bp.route('/api/save_log', methods=['POST'])
@login_required
def save_log():
    data = request.get_json()
    try:
        age = int(data.get('age', 28))
        gender = data.get('gender', 'Male')
        weight = float(data.get('weight', 72))
        height = float(data.get('height', 175))
        steps = int(data.get('steps', 6500))
        sleep = float(data.get('sleep', 6.5))
        water = float(data.get('water', 2.0))
        heart_rate = int(data.get('heart_rate', 72))

        bmi = calc_bmi(weight, height)
        health_score, *_ = calc_health_score(bmi, sleep, steps, water, heart_rate)
        ob_risk, fat_risk, *_ = predict_risks(bmi, sleep, steps, water, age)

        record = {
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'age': age, 'gender': gender, 'weight': weight, 'height': height,
            'steps': steps, 'sleep': sleep, 'water': water, 'heart_rate': heart_rate,
            'bmi': bmi, 'health_score': health_score,
            'obesity_risk': ob_risk, 'fatigue_risk': fat_risk
        }
        save_health_log(current_user.id, record)
        return jsonify({'success': True, 'message': 'Health log saved!'})
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@health_bp.route('/api/history')
@login_required
def history_api():
    limit = int(request.args.get('limit', 50))
    rows = get_health_history(current_user.id, limit=limit)
    return jsonify(rows)


@health_bp.route('/api/clear_logs', methods=['POST'])
@login_required
def clear_logs():
    delete_all_health_logs(current_user.id)
    return jsonify({'success': True})


@health_bp.route('/api/watch')
@login_required
def watch_data():
    base_hr = int(request.args.get('base_hr', 72))
    return jsonify(simulate_watch_data(base_hr))


@health_bp.route('/api/advisor', methods=['POST'])
@login_required
def advisor():
    data = request.get_json()
    question = data.get('question', '')
    user_data = data.get('user_data', {})
    history = data.get('history', [])
    if not question:
        return jsonify({'error': 'No question provided'}), 400
    from .rag_chatbot import chat as ai_chat

    result = ai_chat(question, history=history, user_profile=user_data)
    return jsonify({
        'response': result['answer'],
        'mental_health': result['mental_health'],
        'sources': result['sources']
    })


@health_bp.route('/history')
@login_required
def history_page():
    history = get_health_history(current_user.id, limit=100)
    documents = get_patient_documents(current_user.id, limit=100)
    return render_template('history.html', history=history, documents=documents)


@health_bp.route('/watch')
@login_required
def watch_page():
    return render_template('watch.html')


@health_bp.route('/records/upload', methods=['POST'])
@login_required
def upload_record():
    _ensure_upload_dir()

    document_type = request.form.get('document_type', '').strip().lower()
    title = request.form.get('title', '').strip()
    notes = request.form.get('notes', '').strip()
    uploaded_file = request.files.get('document_file')

    if document_type not in {'bill', 'prescription'}:
        flash('Please choose either bill or prescription.', 'error')
        return redirect(url_for('health.dashboard'))

    if not title:
        flash('Please add a title for this document.', 'error')
        return redirect(url_for('health.dashboard'))

    if not uploaded_file or not uploaded_file.filename:
        flash('Please choose a file to upload.', 'error')
        return redirect(url_for('health.dashboard'))

    if not _allowed_document(uploaded_file.filename):
        flash('Only PDF, PNG, JPG, JPEG, and WEBP files are allowed.', 'error')
        return redirect(url_for('health.dashboard'))

    original_filename = secure_filename(uploaded_file.filename)
    extension = original_filename.rsplit('.', 1)[1].lower()
    stored_filename = f"user{current_user.id}_{uuid.uuid4().hex}.{extension}"
    stored_path = os.path.join(UPLOAD_DIR, stored_filename)
    uploaded_file.save(stored_path)

    ocr_result = extract_document_text(stored_path)

    save_patient_document(
        current_user.id,
        document_type,
        title,
        notes,
        original_filename,
        stored_filename,
        ocr_text=ocr_result.get('text', ''),
        ocr_engine=ocr_result.get('engine'),
        ocr_status=ocr_result.get('status', 'pending')
    )
    if ocr_result.get('status') == 'completed' and ocr_result.get('text'):
        flash(f'{document_type.title()} saved and text extracted successfully.', 'success')
    elif ocr_result.get('message'):
        flash(f"{document_type.title()} saved. OCR status: {ocr_result['message']}", 'info')
    else:
        flash(f'{document_type.title()} saved successfully for future access.', 'success')
    return redirect(url_for('health.dashboard'))


@health_bp.route('/records')
@login_required
def records_page():
    documents = get_patient_documents(current_user.id, limit=200)
    return render_template('records.html', documents=documents)


@health_bp.route('/records/<int:document_id>/download')
@login_required
def download_record(document_id):
    document = get_patient_document_by_id(document_id, current_user.id)
    if not document:
        flash('Document not found.', 'error')
        return redirect(url_for('health.records_page'))

    return send_from_directory(
        UPLOAD_DIR,
        document['stored_filename'],
        as_attachment=True,
        download_name=document['original_filename']
    )
