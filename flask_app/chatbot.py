"""Chatbot blueprint — RAG-powered medical chatbot with mental health detection."""
from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required

chat_bp = Blueprint('chatbot', __name__)


@chat_bp.route('/chatbot')
@login_required
def chatbot_page():
    return render_template('chatbot.html')


@chat_bp.route('/api/chat', methods=['POST'])
@login_required
def chat():
    """Conversational medical chatbot endpoint."""
    from .rag_chatbot import chat as rag_chat
    data = request.get_json()
    message = data.get('message', '').strip()
    history = data.get('history', [])
    user_data = data.get('user_data', {})

    if not message:
        return jsonify({'error': 'No message provided'}), 400

    result = rag_chat(message, history=history, user_profile=user_data)
    return jsonify({
        'response': result['answer'],
        'mental_health': result['mental_health'],
        'sources': result['sources']
    })
