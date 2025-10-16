from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from sqlalchemy.exc import SQLAlchemyError
import os

# Import our modules
from .modules.database import DataManager
from .modules.ai_recommendations import AIRecommendationEngine
from .modules.auth import AuthManager
from .modules.unit_converter import UnitConverter

# Load environment variables
load_dotenv()

# Get the directory where this file is located
current_dir = os.path.dirname(os.path.abspath(__file__))

app = Flask(__name__, 
            template_folder=os.path.join(current_dir, 'templates'),
            static_folder=os.path.join(current_dir, 'static'))
CORS(app)

# Initialize modules
data_manager = DataManager()
ai_engine = AIRecommendationEngine()
auth_manager = AuthManager(data_manager)


@app.route("/")
def index():
    """Serve the main application page"""
    return render_template("index.html")


@app.route("/api/register", methods=["POST"])
def register():
    """Register a new user"""
    try:
        data = request.get_json()
        username = data.get("username")
        password = data.get("password")

        if not username or not password:
            return jsonify({"error": "Username and password are required"}), 400

        success = auth_manager.register_user(username, password)
        if success:
            return jsonify({"message": "User registered successfully"}), 201
        else:
            return jsonify({"error": "Username already exists"}), 409

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/login", methods=["POST"])
def login():
    """Login user"""
    try:
        data = request.get_json()
        username = data.get("username")
        password = data.get("password")

        if not username or not password:
            return jsonify({"error": "Username and password are required"}), 400

        success = auth_manager.login_user(username, password)
        if success:
            return jsonify({"message": "Login successful", "username": username}), 200
        else:
            return jsonify({"error": "Invalid credentials"}), 401

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/log-entry", methods=["POST"])
def log_entry():
    """Log a new diabetes entry"""
    try:
        data = request.get_json()
        username = data.get("username")
        blood_sugar = data.get("blood_sugar")
        meal = data.get("meal")
        exercise = data.get("exercise")
        date = data.get("date")
        input_units = data.get("units", "mg/dL")  # Default to mg/dL if not specified

        if not all([username, blood_sugar, meal, exercise, date]):
            return jsonify({"error": "All fields are required"}), 400

        # Get user's preferred units
        user_units = data_manager.get_user_preferred_units(username)
        
        # Convert blood sugar to mg/dL for storage (we always store in mg/dL)
        if input_units != "mg/dL":
            blood_sugar_mg_dl = UnitConverter.convert_to_user_units(blood_sugar, input_units, "mg/dL")
        else:
            blood_sugar_mg_dl = blood_sugar

        # Validate blood sugar range in mg/dL
        min_val, max_val = UnitConverter.get_validation_range("mg/dL")
        if blood_sugar_mg_dl < min_val or blood_sugar_mg_dl > max_val:
            return jsonify({"error": f"Blood sugar should be between {min_val} and {max_val} mg/dL"}), 400

        # Save the entry (always store in mg/dL)
        entry_id = data_manager.save_entry(username, blood_sugar_mg_dl, meal, exercise, date)

        # Get AI recommendation (convert back to user's preferred units for display)
        if user_units != "mg/dL":
            blood_sugar_for_ai = UnitConverter.convert_to_user_units(blood_sugar_mg_dl, "mg/dL", user_units)
        else:
            blood_sugar_for_ai = blood_sugar_mg_dl
            
        recommendation = ai_engine.get_recommendation(username, blood_sugar_for_ai, meal, exercise)

        return (
            jsonify(
                {
                    "message": "Entry logged successfully",
                    "entry_id": entry_id,
                    'recommendation': recommendation
                }
            ),
            201,
        )

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/history/<username>", methods=["GET"])
def get_history(username):
    """Get user's diabetes history"""
    try:
        if not username:
            return jsonify({"error": "Username is required"}), 400

        # Get user's preferred units
        user_units = data_manager.get_user_preferred_units(username)
        
        # Get raw history (stored in mg/dL)
        raw_history = data_manager.get_user_history(username)
        
        # Convert blood sugar values to user's preferred units
        history = []
        for entry in raw_history:
            converted_entry = entry.copy()
            if user_units != "mg/dL":
                converted_entry["blood_sugar"] = UnitConverter.convert_to_user_units(
                    entry["blood_sugar"], "mg/dL", user_units
                )
            history.append(converted_entry)
        
        return jsonify({"history": history, "units": user_units}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/chart-data/<username>", methods=["GET"])
def get_chart_data(username):
    """Get blood sugar data formatted for charting"""
    try:
        if not username:
            return jsonify({"error": "Username is required"}), 400

        # Get user's preferred units
        user_units = data_manager.get_user_preferred_units(username)
        
        # Get raw chart data (stored in mg/dL)
        raw_chart_data = data_manager.get_chart_data(username)
        
        # Convert blood sugar values to user's preferred units
        chart_data = raw_chart_data.copy()
        if user_units != "mg/dL" and raw_chart_data["data"]:
            chart_data["data"] = [
                UnitConverter.convert_to_user_units(value, "mg/dL", user_units)
                for value in raw_chart_data["data"]
            ]
        
        chart_data["units"] = user_units
        return jsonify({"chart_data": chart_data}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/recommendation/<username>', methods=['GET'])
def get_recommendation(username):
    """Get AI recommendation for user"""
    try:
        if not username:
            return jsonify({'error': 'Username is required'}), 400

        # Get user's recent data for context
        recent_data = data_manager.get_recent_entries(username, limit=5)

        if not recent_data:
            return jsonify({
                'recommendation': 'Start logging your daily data to receive personalized recommendations!'
            }), 200

        # Generate recommendation based on recent data
        latest_entry = recent_data[0]
        
        # Convert blood sugar to user's preferred units for AI recommendation
        user_units = data_manager.get_user_preferred_units(username)
        blood_sugar_for_ai = latest_entry['blood_sugar']
        if user_units != "mg/dL":
            blood_sugar_for_ai = UnitConverter.convert_to_user_units(
                latest_entry['blood_sugar'], "mg/dL", user_units
            )
            
        recommendation = ai_engine.get_recommendation(
            username,
            blood_sugar_for_ai,
            latest_entry['meal'],
            latest_entry['exercise']
        )

        return jsonify({'recommendation': recommendation}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/meal-suggestions', methods=['POST'])
def get_meal_suggestions():
    """Get AI meal suggestions based on blood sugar level"""
    try:
        data = request.get_json()
        blood_sugar = data.get('blood_sugar')
        preferences = data.get('preferences', '')

        if not blood_sugar:
            return jsonify({'error': 'Blood sugar level is required'}), 400

        suggestions = ai_engine.get_meal_suggestions(blood_sugar, preferences)
        return jsonify({'suggestions': suggestions}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/exercise-recommendations', methods=['POST'])
def get_exercise_recommendations():
    """Get AI exercise recommendations based on blood sugar level"""
    try:
        data = request.get_json()
        blood_sugar = data.get('blood_sugar')
        current_exercise = data.get('current_exercise', '')

        if not blood_sugar:
            return jsonify({'error': 'Blood sugar level is required'}), 400

        recommendations = ai_engine.get_exercise_recommendations(blood_sugar, current_exercise)
        return jsonify({'recommendations': recommendations}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/change-password', methods=['POST'])
def change_password():
    """Change user password"""
    try:
        data = request.get_json()
        username = data.get('username')
        old_password = data.get('old_password')
        new_password = data.get('new_password')

        if not all([username, old_password, new_password]):
            return jsonify({'error': 'Username, old password, and new password are required'}), 400

        # Validate new password length
        if len(new_password) < 6:
            return jsonify({'error': 'New password must be at least 6 characters long'}), 400

        success = auth_manager.change_password(username, old_password, new_password)
        if success:
            return jsonify({'message': 'Password changed successfully'}), 200
        else:
            return jsonify({'error': 'Invalid old password or user not found'}), 401

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/update-units', methods=['POST'])
def update_units():
    """Update user's preferred units"""
    try:
        data = request.get_json()
        username = data.get('username')
        units = data.get('units')

        if not all([username, units]):
            return jsonify({'error': 'Username and units are required'}), 400

        # Validate units
        if units not in ['mg/dL', 'mmol/L']:
            return jsonify({'error': 'Units must be either mg/dL or mmol/L'}), 400

        success = data_manager.update_user_preferred_units(username, units)
        
        if success:
            return jsonify({'message': 'Units updated successfully'}), 200
        else:
            return jsonify({'error': 'Failed to update units'}), 500

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/user-preferences/<username>', methods=['GET'])
def get_user_preferences(username):
    """Get user's preferences including preferred units"""
    try:
        if not username:
            return jsonify({'error': 'Username is required'}), 400

        units = data_manager.get_user_preferred_units(username)
        return jsonify({'preferred_units': units}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/user-stats/<username>', methods=['GET'])
def get_user_stats(username):
    """Get user's statistics with unit conversion"""
    try:
        if not username:
            return jsonify({'error': 'Username is required'}), 400

        # Get user's preferred units
        user_units = data_manager.get_user_preferred_units(username)
        
        # Get raw stats (calculated in mg/dL)
        raw_stats = data_manager.get_user_stats(username)
        
        # Convert average blood sugar to user's preferred units
        stats = raw_stats.copy()
        if user_units != "mg/dL" and raw_stats["avg_blood_sugar"] > 0:
            stats["avg_blood_sugar"] = UnitConverter.convert_to_user_units(
                raw_stats["avg_blood_sugar"], "mg/dL", user_units
            )
        
        stats["units"] = user_units
        return jsonify({'stats': stats}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5001)
