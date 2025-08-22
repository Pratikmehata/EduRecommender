from flask import Blueprint, request, jsonify
import json
from datetime import datetime

analytics_bp = Blueprint('analytics', __name__)

# In production, use a proper database
analytics_data = []

@analytics_bp.route('/track', methods=['POST'])
def track_analytics():
    try:
        data = request.get_json()
        
        # Add timestamp and store analytics data
        analytics_record = {
            'timestamp': datetime.now().isoformat(),
            'event_type': data.get('event_type'),
            'user_data': data.get('user_data', {}),
            'recommendation_data': data.get('recommendation_data', {})
        }
        
        analytics_data.append(analytics_record)
        
        return jsonify({'success': True, 'message': 'Analytics tracked successfully'})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@analytics_bp.route('/summary', methods=['GET'])
def get_analytics_summary():
    try:
        # Generate basic analytics summary
        summary = {
            'total_recommendations': len(analytics_data),
            'popular_categories': get_popular_categories(),
            'time_based_analysis': get_time_based_analysis()
        }
        
        return jsonify({'success': True, 'summary': summary})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

def get_popular_categories():
    """Get most recommended categories"""
    categories = [record['recommendation_data'].get('category') for record in analytics_data]
    from collections import Counter
    return dict(Counter(categories).most_common(5))

def get_time_based_analysis():
    """Get recommendations by time of day"""
    time_analysis = {'morning': 0, 'afternoon': 0, 'evening': 0, 'night': 0}
    
    for record in analytics_data:
        hour = datetime.fromisoformat(record['timestamp']).hour
        if 6 <= hour < 12:
            time_analysis['morning'] += 1
        elif 12 <= hour < 17:
            time_analysis['afternoon'] += 1
        elif 17 <= hour < 22:
            time_analysis['evening'] += 1
        else:
            time_analysis['night'] += 1
    
    return time_analysis