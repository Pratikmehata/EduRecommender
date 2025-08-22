from flask import Flask
from flask_cors import CORS

def create_app():
    app = Flask(__name__)
    CORS(app)
    
    # Configuration
    app.config['SECRET_KEY'] = 'your-secret-key-here'
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
    
    # Register blueprints
    from app.routes.predictions import predictions_bp
    from app.routes.analytics import analytics_bp
    
    app.register_blueprint(predictions_bp, url_prefix='/api/predictions')
    app.register_blueprint(analytics_bp, url_prefix='/api/analytics')
    
    return app