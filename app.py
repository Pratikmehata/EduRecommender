from app import create_app

app = create_app()

if __name__ == '__main__':
    # Create models directory if it doesn't exist
    import os
    os.makedirs('models', exist_ok=True)
    
    # Try to load or create model
    try:
        with open('models/simple_model.pkl', 'rb') as f:
            import pickle
            model = pickle.load(f)
        print("Model loaded successfully")
    except:
        print("No model found. Run models/simple_model.py to train a model.")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
