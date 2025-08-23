
from flask import Blueprint, request, jsonify, render_template
import os
import json

# Import the model class
from models.simple_model import SimpleEducationalModel

predictions_bp = Blueprint('predictions', __name__)

# ... (rest of your existing routes)
# Always create a new model instance (no persistence needed)
model = SimpleEducationalModel()
model_info = {
    'model_type': 'SimpleEducationalModel',
    'features_used': ['math_score', 'science_score', 'reading_score', 
                     'learning_style', 'interest_level', 'previous_performance'],
    'categories': model.categories
}

print("Simple educational model initialized")

@predictions_bp.route('/', methods=['GET'])
def index():
    """Serve the main HTML page"""
    return render_template('index.html')
    
@predictions_bp.route('/recommend', methods=['POST'])
def recommend():
    try:
        data = request.get_json()
        
        # Extract features from request
        features = extract_features(data)
        
        # Make prediction
        prediction = model.predict(features)
        probabilities = model.predict_proba(features)
        
        # Get top categories
        top_categories, top_probabilities = model.get_top_categories(probabilities, top_n=3)
        
        # Get recommendations
        recommendations = model.get_recommendations(top_categories, top_probabilities)
        
        return jsonify({
            'success': True,
            'recommendations': recommendations,
            'predicted_categories': top_categories,
            'probabilities': [float(p) for p in top_probabilities]
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400

def extract_features(data):
    """Extract and preprocess features from request data"""
    features = [
        float(data.get('math_score', 0)),
        float(data.get('science_score', 0)),
        float(data.get('reading_score', 0)),
        int(data.get('learning_style', 0)),
        int(data.get('interest_level', 0)),
        int(data.get('previous_performance', 0))
    ]
    return features

@predictions_bp.route('/model_info', methods=['GET'])
def get_model_info():
    """Get information about the loaded model"""
    return jsonify({
        'success': True, 
        'model_info': model_info
    })

@predictions_bp.route('/train_model', methods=['POST'])
def train_model():
    """Endpoint to train the model - not needed for simple model"""
    return jsonify({
        'success': True,
        'message': 'Simple model does not require training',
        'model_info': model_info
    })
