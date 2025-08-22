from flask import Blueprint, request, jsonify
import pickle
import numpy as np
import pandas as pd
import os

predictions_bp = Blueprint('predictions', __name__)

# Load model and scaler
try:
    with open('models/model.pkl', 'rb') as f:
        model = pickle.load(f)
    with open('models/scaler.pkl', 'rb') as f:
        scaler = pickle.load(f)
    print("Model and scaler loaded successfully")
except FileNotFoundError:
    model = None
    scaler = None
    print("Warning: Model or scaler file not found. Using mock predictions.")

@predictions_bp.route('/recommend', methods=['POST'])
def recommend():
    try:
        data = request.get_json()
        
        # Extract features from request
        features = extract_features(data)
        
        if model and scaler:
            # Scale features and make prediction
            features_scaled = scaler.transform([features])
            prediction = model.predict(features_scaled)
            probabilities = model.predict_proba(features_scaled)[0] if hasattr(model, 'predict_proba') else None
            
            # Get top 3 categories with highest probabilities
            if probabilities is not None:
                top_indices = np.argsort(probabilities)[-3:][::-1]
                top_categories = model.classes_[top_indices]
                top_probabilities = probabilities[top_indices]
            else:
                top_categories = [prediction[0]]
                top_probabilities = [1.0]
        else:
            # Mock prediction for development
            prediction = ['Math_Advanced']
            top_categories = ['Math_Advanced', 'Science_Intermediate', 'General_Studies']
            top_probabilities = [0.6, 0.25, 0.15]
        
        recommendations = generate_recommendations(top_categories, top_probabilities)
        
        return jsonify({
            'success': True,
            'recommendations': recommendations,
            'predicted_categories': top_categories,
            'probabilities': [float(p) for p in top_probabilities]  # Convert numpy floats to Python floats
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400

def extract_features(data):
    """Extract and preprocess features from request data"""
    features = [
        data.get('math_score', 0),
        data.get('science_score', 0),
        data.get('reading_score', 0),
        data.get('learning_style', 0),  # 0: visual, 1: auditory, 2: kinesthetic
        data.get('interest_level', 0),   # 0: low, 1: medium, 2: high
        data.get('previous_performance', 0)
    ]
    return features

def generate_recommendations(categories, probabilities):
    """Generate educational recommendations based on predicted categories"""
    all_recommendations = []
    
    # Define recommendations for each category
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
    
    # Generate recommendations for each category with their probability
    for i, category in enumerate(categories):
        recs = recommendation_db.get(category, [])
        for rec in recs:
            rec_with_meta = rec.copy()
            rec_with_meta['category'] = category
            rec_with_meta['confidence'] = float(probabilities[i])
            all_recommendations.append(rec_with_meta)
    
    # Sort by confidence score (highest first)
    all_recommendations.sort(key=lambda x: x['confidence'], reverse=True)
    
    return all_recommendations[:9]  # Return top 9 recommendations (3 per category)

@predictions_bp.route('/model_info', methods=['GET'])
def model_info():
    """Get information about the loaded model"""
    if model:
        info = {
            'model_type': type(model).__name__,
            'n_classes': len(model.classes_) if hasattr(model, 'classes_') else 'Unknown',
            'features_used': ['math_score', 'science_score', 'reading_score', 
                             'learning_style', 'interest_level', 'previous_performance']
        }
        return jsonify({'success': True, 'model_info': info})
    else:
        return jsonify({'success': False, 'error': 'Model not loaded'})