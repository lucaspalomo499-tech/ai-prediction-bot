"""Flask API for the prediction bot"""
from flask import Flask, request, jsonify
from flask_cors import CORS
import logging
from config import config
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Load configuration
env = os.getenv('FLASK_ENV', 'development')
app.config.from_object(config[env])

# Initialize models and services
prediction_model = None
predictor = None

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'AI Prediction Bot'
    }), 200

@app.route('/api/v1/predict/event', methods=['POST'])
def predict_event():
    """
    Make a prediction for a specific event.
    
    Expected JSON:
    {
        "event_data": {...},
        "event_type": "sports|market|financial"
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'event_data' not in data:
            return jsonify({'error': 'Missing event_data'}), 400
        
        import pandas as pd
        event_df = pd.DataFrame([data['event_data']])
        
        prediction = predictor.predict_event(event_df)
        
        return jsonify(prediction), 200
    except Exception as e:
        logger.error(f"Error in predict_event: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/v1/predict/multiple', methods=['POST'])
def predict_multiple():
    """
    Make predictions for multiple events.
    
    Expected JSON:
    {
        "events": [{...}, {...}, ...]
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'events' not in data:
            return jsonify({'error': 'Missing events'}), 400
        
        import pandas as pd
        events = [pd.DataFrame([e]) for e in data['events']]
        
        predictions = predictor.predict_multiple_events(events)
        
        return jsonify({
            'predictions': predictions,
            'total': len(predictions)
        }), 200
    except Exception as e:
        logger.error(f"Error in predict_multiple: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/v1/predict/markets', methods=['POST'])
def predict_markets():
    """
    Predict betting market outcomes.
    
    Expected JSON:
    {
        "market_data": DataFrame-like structure
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'market_data' not in data:
            return jsonify({'error': 'Missing market_data'}), 400
        
        import pandas as pd
        market_df = pd.DataFrame(data['market_data'])
        
        predictions = predictor.predict_betting_markets(market_df)
        
        return jsonify(predictions), 200
    except Exception as e:
        logger.error(f"Error in predict_markets: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/v1/stats/performance', methods=['GET'])
def get_performance():
    """
    Get prediction performance statistics.
    """
    try:
        stats = predictor.get_performance_stats()
        return jsonify(stats), 200
    except Exception as e:
        logger.error(f"Error in get_performance: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/v1/model/status', methods=['GET'])
def model_status():
    """
    Get model status and information.
    """
    try:
        status = {
            'model_type': app.config.get('MODEL_TYPE'),
            'confidence_threshold': app.config.get('PREDICTION_CONFIDENCE_THRESHOLD'),
            'lookback_period': app.config.get('LOOKBACK_PERIOD'),
            'technical_indicators': app.config.get('TECHNICAL_INDICATORS'),
            'status': 'ready' if prediction_model else 'not_initialized'
        }
        return jsonify(status), 200
    except Exception as e:
        logger.error(f"Error in model_status: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=app.config['DEBUG'], host='0.0.0.0', port=5000)
