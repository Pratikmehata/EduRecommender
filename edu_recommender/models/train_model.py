import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.metrics import classification_report, accuracy_score
import pickle
import os

def generate_synthetic_data(num_samples=1000):
    """Generate synthetic educational data for training"""
    np.random.seed(42)
    
    data = {
        'math_score': np.random.randint(40, 100, num_samples),
        'science_score': np.random.randint(40, 100, num_samples),
        'reading_score': np.random.randint(40, 100, num_samples),
        'learning_style': np.random.choice([0, 1, 2], num_samples),  # 0: visual, 1: auditory, 2: kinesthetic
        'interest_level': np.random.choice([0, 1, 2], num_samples),   # 0: low, 1: medium, 2: high
        'previous_performance': np.random.choice([0, 1, 2], num_samples)  # 0: below avg, 1: avg, 2: above avg
    }
    
    df = pd.DataFrame(data)
    
    # Create target variable based on features
    conditions = [
        (df['math_score'] >= 85) & (df['science_score'] >= 85),
        (df['math_score'] >= 70) & (df['math_score'] < 85) & (df['science_score'] >= 70),
        (df['science_score'] >= 85) & (df['math_score'] >= 70),
        (df['science_score'] >= 70) & (df['science_score'] < 85) & (df['math_score'] >= 70),
        (df['reading_score'] >= 85) & (df['math_score'] < 70),
        (df['reading_score'] >= 70) & (df['reading_score'] < 85) & (df['math_score'] < 70)
    ]
    
    choices = [
        'Math_Advanced',
        'Math_Intermediate',
        'Science_Advanced',
        'Science_Intermediate',
        'Language_Advanced',
        'Language_Intermediate'
    ]
    
    df['category'] = np.select(conditions, choices, default='General_Studies')
    
    return df

def train_educational_model():
    """Train the educational recommendation model"""
    print("Generating synthetic educational data...")
    df = generate_synthetic_data(2000)
    
    print("Data sample:")
    print(df.head())
    
    print("\nTarget distribution:")
    print(df['category'].value_counts())
    
    # Prepare features and target
    X = df[['math_score', 'science_score', 'reading_score', 
            'learning_style', 'interest_level', 'previous_performance']]
    y = df['category']
    
    # Split the data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    # Scale the features
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    # Train the model
    print("\nTraining Random Forest model...")
    model = RandomForestClassifier(
        n_estimators=100,
        max_depth=10,
        random_state=42,
        class_weight='balanced'
    )
    
    model.fit(X_train_scaled, y_train)
    
    # Evaluate the model
    y_pred = model.predict(X_test_scaled)
    accuracy = accuracy_score(y_test, y_pred)
    
    print(f"\nModel Accuracy: {accuracy:.2f}")
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred))
    
    # Save the model and scaler
    os.makedirs('models', exist_ok=True)
    
    with open('models/model.pkl', 'wb') as f:
        pickle.dump(model, f)
    
    with open('models/scaler.pkl', 'wb') as f:
        pickle.dump(scaler, f)
    
    print("Model and scaler saved to 'models/' directory")
    
    return model, scaler, accuracy

if __name__ == "__main__":
    train_educational_model()