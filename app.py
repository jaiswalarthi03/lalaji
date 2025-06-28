import os
import logging
import requests
import pymongo

from flask import Flask, render_template, jsonify, request
from config import ULTRAVOX_API_KEY, ULTRAVOX_API_URL, DEFAULT_VOICE, ERROR_MESSAGES, VOICE_OPTIONS
from flask_session import Session
from services.ultravox_service import create_ultravox_call

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create the app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev_secret_key")

# Server-side session configuration
app.config['SESSION_TYPE'] = 'mongodb'
app.config['SESSION_MONGODB'] = pymongo.MongoClient('mongodb+srv://root:root@preventive.i7rpqdb.mongodb.net/?retryWrites=true&w=majority&appName=preventive')
app.config['SESSION_MONGODB_DB'] = 'inventory_master'
app.config['SESSION_MONGODB_COLLECT'] = 'sessions'

# Initialize server-side session handling
Session(app)

# Register blueprint always (for Vercel and local)
from routes import main_bp
app.register_blueprint(main_bp)

def ultravox_request(method, path, **kwargs):
    if not path.startswith('/'):
        path = '/' + path
    
    url = ULTRAVOX_API_URL + path
    headers = {"X-API-Key": ULTRAVOX_API_KEY}
    
    if 'headers' in kwargs:
        kwargs['headers'].update(headers)
    else:
        kwargs['headers'] = headers
    
    kwargs['verify'] = False
    
    try:
        response = requests.request(method, url, **kwargs)
        if response.status_code >= 400:
            app.logger.error(f"API error response: {response.text}")
        return response
    except requests.exceptions.RequestException as e:
        app.logger.error(f"API request error: {e}")
        return None

@app.route('/start_call', methods=['POST'])
def start_call():
    try:
        data = request.json or {}
        selected_voice = data.get('voice', DEFAULT_VOICE)
        response = create_ultravox_call(selected_voice)
        if response and response.status_code == 201:
            return jsonify(response.json())
        else:
            if response:
                status_code = response.status_code
                try:
                    error_data = response.json()
                    api_detail = error_data.get('detail', '')
                except Exception:
                    api_detail = response.text
                error_message = f"API Error: {ERROR_MESSAGES.get(status_code, f'Unknown error (status code: {status_code})')}"
                if api_detail:
                    error_message += f" - {api_detail}"
                if status_code == 402:
                    return jsonify({
                        "error": "API limit reached. Please check your subscription.",
                        "detail": api_detail,
                        "status": "payment_required"
                    }), 402
                return jsonify({"error": error_message}), status_code
            else:
                return jsonify({"error": "Failed to connect to Ultravox API"}), 500
    except Exception as e:
        app.logger.exception("Error starting call")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    with app.app_context():
        # Initialize MongoDB connection
        from mongodb import db
        
        logger.info("MongoDB connection initialized successfully")
        
    app.run(host="0.0.0.0", port=5000, debug=True)
