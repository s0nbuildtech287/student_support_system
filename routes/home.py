from flask import Blueprint, render_template, redirect, url_for, session, request, jsonify
from routes.user import get_current_user
from services.groq_service import GroqService
from config import Config
import markdown
import requests

home_bp = Blueprint("home", __name__)

@home_bp.route("/")
def index():
    # Nếu chưa đăng nhập thì redirect sang login
    if 'user_id' not in session:
        return redirect(url_for('user.login'))
    
    user = get_current_user()
    return render_template("home.html", user=user, roadmap="", config={
        'DIFY_API_KEY': Config.DIFY_API_KEY,
        'DIFY_API_URL': Config.DIFY_API_URL
    })

@home_bp.route("/home")
def home():
    user = get_current_user()
    return render_template("home.html", user=user, roadmap="", config={
        'DIFY_API_KEY': Config.DIFY_API_KEY,
        'DIFY_API_URL': Config.DIFY_API_URL
    })


@home_bp.route("/recommend", methods=["POST"])
def recommend():
    """Get AI recommendation based on form data"""
    user = get_current_user()
    
    # Get form data
    user_data = {
        'year': request.form.get('year'),
        'gpa': request.form.get('gpa'),
        'study_time': request.form.get('study_time'),
        'goal': request.form.get('goal'),
        'custom_goal': request.form.get('custom_goal', ''),
        'learning_mode': request.form.get('learning_mode'),
        'resource': request.form.get('resource'),
        'level': request.form.get('level')
    }
    
    # Get AI recommendation
    ai_response = GroqService.recommend(user_data)
    
    # Convert markdown to HTML
    html_response = markdown.markdown(ai_response, extensions=['tables', 'fenced_code', 'nl2br'])
    
    # Store conversation in session for follow-up
    session['chat_history'] = [
        {"role": "user", "content": f"Gợi ý lộ trình cho sinh viên năm {user_data['year']}, GPA {user_data['gpa']}, mục tiêu: {user_data['goal']}"},
        {"role": "assistant", "content": ai_response}
    ]
    session['user_study_data'] = user_data
    
    return render_template("home.html", user=user, roadmap=html_response, user_data=user_data, config={
        'DIFY_API_KEY': Config.DIFY_API_KEY,
        'DIFY_API_URL': Config.DIFY_API_URL
    })


@home_bp.route("/chat", methods=["POST"])
def chat():
    """Continue conversation with AI"""
    data = request.get_json()
    user_message = data.get('message', '')
    
    if not user_message:
        return jsonify({'error': 'Message is required'}), 400
    
    # Get conversation history from session
    chat_history = session.get('chat_history', [])
    
    # Get AI response
    ai_response = GroqService.chat(user_message, chat_history)
    
    # Update conversation history
    chat_history.append({"role": "user", "content": user_message})
    chat_history.append({"role": "assistant", "content": ai_response})
    session['chat_history'] = chat_history
    
    # Convert markdown to HTML
    html_response = markdown.markdown(ai_response, extensions=['tables', 'fenced_code', 'nl2br'])
    
    return jsonify({
        'response': html_response,
        'raw': ai_response
    })


@home_bp.route("/dify-chat", methods=["POST"])
def dify_chat():
    """Chat with Dify AI"""
    data = request.get_json()
    user_message = data.get('message', '')
    
    if not user_message:
        return jsonify({'error': 'Message is required'}), 400
    
    # Get Dify conversation ID from session
    conversation_id = session.get('dify_conversation_id', '')
    
    # Check if Dify API key is configured
    if not Config.DIFY_API_KEY:
        return jsonify({'error': 'Dify API key not configured'}), 500
    
    try:
        response = requests.post(
            f"{Config.DIFY_API_URL}/chat-messages",
            headers={
                'Authorization': f'Bearer {Config.DIFY_API_KEY}',
                'Content-Type': 'application/json'
            },
            json={
                'inputs': {},
                'query': user_message,
                'response_mode': 'blocking',
                'conversation_id': conversation_id,
                'user': f'user-{session.get("user_id", "guest")}'
            },
            timeout=60
        )
        
        if response.status_code == 200:
            result = response.json()
            # Save conversation ID for follow-up
            session['dify_conversation_id'] = result.get('conversation_id', '')
            
            # Convert markdown to HTML
            answer = result.get('answer', '')
            html_response = markdown.markdown(answer, extensions=['tables', 'fenced_code', 'nl2br'])
            
            return jsonify({
                'response': html_response,
                'raw': answer,
                'conversation_id': result.get('conversation_id', '')
            })
        else:
            return jsonify({
                'error': f'Dify API error: {response.status_code}',
                'detail': response.text
            }), response.status_code
            
    except requests.exceptions.Timeout:
        return jsonify({'error': 'Request timeout'}), 504
    except Exception as e:
        return jsonify({'error': str(e)}), 500