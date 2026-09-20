"""Disease prediction blueprint."""
from flask import Blueprint, request, jsonify, render_template
from flask_login import login_required
from .ml_models import predict_diabetes, predict_heart_disease, predict_brain_tumor

pred_bp = Blueprint('predictions', __name__)


@pred_bp.route('/api/predict/diabetes', methods=['POST'])
@login_required
def diabetes():
    d = request.get_json()
    try:
        features = [
            float(d['pregnancies']), float(d['glucose']),
            float(d['blood_pressure']), float(d['skin_thickness']),
            float(d['insulin']), float(d['bmi']),
            float(d['diabetes_pedigree_function']), float(d['age'])
        ]
        return jsonify(predict_diabetes(features))
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@pred_bp.route('/api/predict/heart', methods=['POST'])
@login_required
def heart():
    d = request.get_json()
    try:
        features = [
            float(d['age']), float(d['sex']), float(d['chest_pain_type']),
            float(d['resting_bp']), float(d['cholesterol']), float(d['fasting_bs']),
            float(d['resting_ecg']), float(d['max_hr']),
            float(d['exercise_angina']), float(d['oldpeak'])
        ]
        return jsonify(predict_heart_disease(features))
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@pred_bp.route('/api/predict/brain_tumor', methods=['POST'])
@login_required
def brain_tumor():
    if 'image' not in request.files:
        return jsonify({'error': 'No image file provided'}), 400
    file = request.files['image']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    allowed = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp'}
    ext = file.filename.rsplit('.', 1)[-1].lower() if '.' in file.filename else ''
    if ext not in allowed:
        return jsonify({'error': 'Invalid file type. Please upload an MRI image.'}), 400
    try:
        image_bytes = file.read()
        return jsonify(predict_brain_tumor(image_bytes))
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@pred_bp.route('/diabetes')
@login_required
def diabetes_page():
    return render_template('diabetes.html')


@pred_bp.route('/heart')
@login_required
def heart_page():
    return render_template('heart.html')


@pred_bp.route('/brain-tumor')
@login_required
def brain_tumor_page():
    return render_template('brain_tumor.html')
