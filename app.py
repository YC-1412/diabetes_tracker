from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import os
from dotenv import load_dotenv

# Import our modules
from modules.database import DataManager
# from modules.ai_recommendations import AIRecommendationEngine
from modules.auth import AuthManager

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)

# Initialize modules
data_manager = DataManager()
# ai_engine = AIRecommendationEngine()
auth_manager = AuthManager()

@app.route('/')
def index():
    """Serve the main application page"""
    return render_template('index.html')

@app.route('/api/register', methods=['POST'])
def register():
    """Register a new user"""
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return jsonify({'error': 'Username and password are required'}), 400
        
        success = auth_manager.register_user(username, password)
        if success:
            return jsonify({'message': 'User registered successfully'}), 201
        else:
            return jsonify({'error': 'Username already exists'}), 409
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/login', methods=['POST'])
def login():
    """Login user"""
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return jsonify({'error': 'Username and password are required'}), 400
        
        success = auth_manager.login_user(username, password)
        if success:
            return jsonify({'message': 'Login successful', 'username': username}), 200
        else:
            return jsonify({'error': 'Invalid credentials'}), 401
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/log-entry', methods=['POST'])
def log_entry():
    """Log a new diabetes entry"""
    try:
        data = request.get_json()
        username = data.get('username')
        blood_sugar = data.get('blood_sugar')
        meal = data.get('meal')
        exercise = data.get('exercise')
        date = data.get('date')
        
        if not all([username, blood_sugar, meal, exercise, date]):
            return jsonify({'error': 'All fields are required'}), 400
        
        # Save the entry
        entry_id = data_manager.save_entry(username, blood_sugar, meal, exercise, date)
        
        # Get AI recommendation
        # recommendation = ai_engine.get_recommendation(username, blood_sugar, meal, exercise)
        
        return jsonify({
            'message': 'Entry logged successfully',
            'entry_id': entry_id,
            # 'recommendation': recommendation
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/history/<username>', methods=['GET'])
def get_history(username):
    """Get user's diabetes history"""
    try:
        if not username:
            return jsonify({'error': 'Username is required'}), 400
        
        history = data_manager.get_user_history(username)
        return jsonify({'history': history}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# @app.route('/api/recommendation/<username>', methods=['GET'])
# def get_recommendation(username):
#     """Get AI recommendation for user"""
#     try:
#         if not username:
#             return jsonify({'error': 'Username is required'}), 400
        
#         # Get user's recent data for context
#         recent_data = data_manager.get_recent_entries(username, limit=5)
        
#         if not recent_data:
#             return jsonify({'recommendation': 'Start logging your daily data to receive personalized recommendations!'}), 200
        
#         # Generate recommendation based on recent data
#         latest_entry = recent_data[0]
#         recommendation = ai_engine.get_recommendation(
#             username, 
#             latest_entry['blood_sugar'], 
#             latest_entry['meal'], 
#             latest_entry['exercise']
#         )
        
#         return jsonify({'recommendation': recommendation}), 200
        
#     except Exception as e:
#         return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000) 