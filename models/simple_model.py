import pickle
import os
import json
from datetime import datetime

class SimpleEducationalModel:
    def __init__(self):
        self.categories = [
            'Math_Basic', 'Math_Intermediate', 'Math_Advanced',
            'Science_Basic', 'Science_Intermediate', 'Science_Advanced',
            'Language_Intermediate', 'Language_Advanced', 'General_Studies'
        ]
        
        # Predefined recommendation database (same as before)
        self.recommendation_db = {
            # ... (same as before)
        }
    
    # ... (other methods: predict, predict_proba, get_recommendations)
    
    def get_top_categories(self, probabilities, top_n=3):
        """Get top N categories based on probabilities"""
        # Create list of (probability, category) tuples
        prob_cat = [(prob, category) for prob, category in zip(probabilities, self.categories)]
        
        # Sort by probability (descending)
        prob_cat.sort(key=lambda x: x[0], reverse=True)
        
        # Return top N
        top_categories = [cat for _, cat in prob_cat[:top_n]]
        top_probabilities = [prob for prob, _ in prob_cat[:top_n]]
        
        return top_categories, top_probabilities

def train_simple_model():
    """Train and save the simple model"""
    model = SimpleEducationalModel()
    
    os.makedirs('models', exist_ok=True)
    
    with open('models/simple_model.pkl', 'wb') as f:
        pickle.dump(model, f)
    
    # Also save model info as JSON for frontend
    model_info = {
        'model_type': 'SimpleEducationalModel',
        'categories': model.categories,
        'features_used': ['math_score', 'science_score', 'reading_score', 
                         'learning_style', 'interest_level', 'previous_performance'],
        'trained_at': datetime.now().isoformat()
    }
    
    with open('models/model_info.json', 'w') as f:
        json.dump(model_info, f, indent=2)
    
    print("Simple model saved to 'models/simple_model.pkl'")
    print("Model info saved to 'models/model_info.json'")
    return model

if __name__ == "__main__":
    train_simple_model()
