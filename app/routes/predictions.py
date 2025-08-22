from flask import Blueprint, request, jsonify
import pickle
import os
import json

predictions_bp = Blueprint('predictions', __name__)

# Load the simple model
model = None
model_info = {}

try:
    # Try loading the simple model
    with open('models/simple_model.pkl', 'rb') as f:
        model = pickle.load(f)
    print("Simple model loaded successfully")
    
    # Try loading model info
    try:
        with open('models/model_info.json', 'r') as f:
            model_info = json.load(f)
    except FileNotFoundError:
        model_info = {
            'model_type': 'SimpleEducationalModel',
            'features_used': ['math_score', 'science_score', 'reading_score', 
                             'learning_style', 'interest_level', 'previous_performance']
        }
        
except FileNotFoundError:
    # Create a simple model if none exists
    try:
        from models.simple_model import SimpleEducationalModel
        model = SimpleEducationalModel()
        model_info = {
            'model_type': 'SimpleEducationalModel',
            'features_used': ['math_score', 'science_score', 'reading_score', 
                             'learning_style', 'interest_level', 'previous_performance']
        }
        print("Using in-memory simple model")
    except ImportError:
        # Final fallback - create a basic mock model
        class MockModel:
            def __init__(self):
                self.categories = ['Math_Intermediate', 'Science_Intermediate', 'General_Studies']
            
            def predict(self, features):
                return 'Math_Intermediate'
            
            def predict_proba(self, features):
                return [0.6, 0.3, 0.1]
            
            def get_top_categories(self, probabilities, top_n=3):
                return self.categories[:top_n], probabilities[:top_n]
            
            def get_recommendations(self, categories, probabilities, max_recommendations=9):
                return [{
                    'title': 'Sample Math Course', 
                    'type': 'course', 
                    'difficulty': 'intermediate',
                    'category': 'Math_Intermediate',
                    'confidence': 0.6
                }]
        
        model = MockModel()
        model_info = {'model_type': 'MockModel', 'features_used': []}
        print("Using mock model")

@predictions_bp.route('/recommend', methods=['POST'])
def recommend():
    try:
        data = request.get_json()
        
        # Extract features from request
        features = extract_features(data)
        
        if model:
            # Make prediction
            prediction = model.predict(features)
            probabilities = model.predict_proba(features)
            
            # Get top categories
            if hasattr(model, 'get_top_categories'):
                top_categories, top_probabilities = model.get_top_categories(probabilities, top_n=3)
            else:
                # Fallback for mock model
                top_categories = model.categories[:3]
                top_probabilities = probabilities[:3]
            
            # Get recommendations
            if hasattr(model, 'get_recommendations'):
                recommendations = model.get_recommendations(top_categories, top_probabilities)
            else:
                recommendations = generate_recommendations(top_categories, top_probabilities)
        else:
            # Mock prediction for development
            top_categories = ['Math_Advanced', 'Science_Intermediate', 'General_Studies']
            top_probabilities = [0.6, 0.25, 0.15]
            recommendations = generate_recommendations(top_categories, top_probabilities)
        
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

def generate_recommendations(categories, probabilities):
    """Fallback function to generate recommendations"""
    recommendation_db = {
        'Math_Basic': [
            {'title': 'Basic Arithmetic Fundamentals', 'type': 'course', 'difficulty': 'beginner', 'duration': '4 weeks'},
            {'title': 'Number Sense Workbook', 'type': 'book', 'difficulty': 'beginner', 'pages': 120},
            {'title': 'Math Games for Beginners', 'type': 'activity', 'difficulty': 'beginner', 'time_required': '30 mins'}
        ],
        'Math_Intermediate': [
            {'title': 'Algebra Foundations', 'type': 'course', 'difficulty': 'intermediate', 'duration': '6 weeks'},
            {'title': 'Geometry Concepts', 'type': 'book', 'difficulty': 'intermediate', 'pages': 200},
            {'title': 'Problem Solving Strategies', 'type': 'activity', 'difficulty': 'intermediate', 'time_required': '45 mins'}
        ],
        'Math_Advanced': [
            {'title': 'Advanced Calculus', 'type': 'course', 'difficulty': 'advanced', 'duration': '8 weeks'},
            {'title': 'Linear Algebra Concepts', 'type': 'book', 'difficulty': 'advanced', 'pages': 350},
            {'title': 'Math Olympiad Preparation', 'type': 'activity', 'difficulty': 'advanced', 'time_required': '60 mins'}
        ],
        'Science_Basic': [
            {'title': 'Introduction to Biology', 'type': 'course', 'difficulty': 'beginner', 'duration': '4 weeks'},
            {'title': 'Basic Chemistry Principles', 'type': 'book', 'difficulty': 'beginner', 'pages': 150},
            {'title': 'Simple Science Experiments', 'type': 'activity', 'difficulty': 'beginner', 'time_required': '30 mins'}
        ],
        'Science_Intermediate': [
            {'title': 'Chemistry in Daily Life', 'type': 'course', 'difficulty': 'intermediate', 'duration': '6 weeks'},
            {'title': 'Physics Fundamentals', 'type': 'book', 'difficulty': 'intermediate', 'pages': 250},
            {'title': 'Intermediate Lab Techniques', 'type': 'activity', 'difficulty': 'intermediate', 'time_required': '45 mins'}
        ],
        'Science_Advanced': [
            {'title': 'Advanced Physics', 'type': 'course', 'difficulty': 'advanced', 'duration': '8 weeks'},
            {'title': 'Organic Chemistry', 'type': 'book', 'difficulty': 'advanced', 'pages': 400},
            {'title': 'Research Project Guidance', 'type': 'activity', 'difficulty': 'advanced', 'time_required': '60 mins'}
        ],
        'Language_Intermediate': [
            {'title': 'Reading Comprehension', 'type': 'course', 'difficulty': 'intermediate', 'duration': '5 weeks'},
            {'title': 'Vocabulary Builder', 'type': 'book', 'difficulty': 'intermediate', 'pages': 180},
            {'title': 'Writing Practice', 'type': 'activity', 'difficulty': 'intermediate', 'time_required': '40 mins'}
        ],
        'Language_Advanced': [
            {'title': 'Advanced Literature', 'type': 'course', 'difficulty': 'advanced', 'duration': '7 weeks'},
            {'title': 'Critical Analysis Guide', 'type': 'book', 'difficulty': 'advanced', 'pages': 300},
            {'title': 'Debate and Discussion', 'type': 'activity', 'difficulty': 'advanced', 'time_required': '50 mins'}
        ],
        'General_Studies': [
            {'title': 'Study Skills Mastery', 'type': 'course', 'difficulty': 'beginner', 'duration': '3 weeks'},
            {'title': 'Learning Strategies Guide', 'type': 'book', 'difficulty': 'beginner', 'pages': 100},
            {'title': 'Time Management Workshop', 'type': 'activity', 'difficulty': 'beginner', 'time_required': '30 mins'}
        ]
    }
    
    all_recommendations = []
    
    for i, category in enumerate(categories):
        if category in recommendation_db:
            recs = recommendation_db[category]
            for rec in recs:
                rec_with_meta = rec.copy()
                rec_with_meta['category'] = category
                rec_with_meta['confidence'] = float(probabilities[i])
                all_recommendations.append(rec_with_meta)
    
    # Sort by confidence score (highest first)
    all_recommendations.sort(key=lambda x: x['confidence'], reverse=True)
    
    return all_recommendations[:9]

@predictions_bp.route('/model_info', methods=['GET'])
def get_model_info():
    """Get information about the loaded model"""
    return jsonify({
        'success': True, 
        'model_info': model_info
    })

@predictions_bp.route('/train_model', methods=['POST'])
def train_model():
    """Endpoint to train the model"""
    try:
        from models.simple_model import train_simple_model
        
        # Train the model
        global model, model_info
        model = train_simple_model()
        
        # Load model info
        try:
            with open('models/model_info.json', 'r') as f:
                model_info = json.load(f)
        except FileNotFoundError:
            model_info = {
                'model_type': 'SimpleEducationalModel',
                'features_used': ['math_score', 'science_score', 'reading_score', 
                                 'learning_style', 'interest_level', 'previous_performance']
            }
        
        return jsonify({
            'success': True,
            'message': 'Simple model trained successfully',
            'model_info': model_info
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
