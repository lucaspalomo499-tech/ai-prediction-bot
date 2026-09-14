"""Main predictor class that orchestrates predictions"""
import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class Predictor:
    """Main predictor for sports betting and prediction markets"""
    
    def __init__(self, model, feature_engineer, confidence_threshold: float = 0.65):
        self.model = model
        self.feature_engineer = feature_engineer
        self.confidence_threshold = confidence_threshold
        self.prediction_history = []
    
    def predict_event(self, event_data: pd.DataFrame) -> Dict:
        """
        Make a prediction for a specific event.
        
        Returns:
            Dict with prediction, confidence, and reasoning
        """
        try:
            # Add technical indicators
            event_data = self.feature_engineer.add_technical_indicators(event_data.copy())
            event_data = self.feature_engineer.add_statistical_features(event_data)
            
            # Get latest data point
            latest_data = event_data.iloc[-1:]
            
            # Select features
            feature_cols = [col for col in event_data.columns if col not in 
                          ['date', 'time', 'result', 'team', 'opponent']]
            X = latest_data[feature_cols].fillna(0)
            
            # Scale features
            X_scaled = self.model.scaler.transform(X)
            
            # Make prediction
            y_pred = self.model.predict_proba(X_scaled)
            prediction_prob = y_pred[0][1] if len(y_pred.shape) > 1 else y_pred[0]
            
            # Determine confidence
            confidence = abs(prediction_prob - 0.5) * 2
            is_confident = confidence >= self.confidence_threshold
            
            result = {
                'prediction': 'Win' if prediction_prob > 0.5 else 'Loss',
                'probability': float(prediction_prob),
                'confidence': float(confidence),
                'is_confident': bool(is_confident),
                'timestamp': datetime.now().isoformat(),
                'threshold': self.confidence_threshold
            }
            
            self.prediction_history.append(result)
            logger.info(f"Prediction made: {result}")
            
            return result
        except Exception as e:
            logger.error(f"Error making prediction: {e}")
            return {'error': str(e)}
    
    def predict_multiple_events(self, events: List[pd.DataFrame]) -> List[Dict]:
        """
        Make predictions for multiple events.
        """
        predictions = []
        for event_data in events:
            pred = self.predict_event(event_data)
            predictions.append(pred)
        
        return predictions
    
    def predict_betting_markets(self, market_data: pd.DataFrame) -> Dict:
        """
        Predict outcomes in betting markets.
        """
        try:
            predictions = {}
            
            # Group by market/event
            for event_id, group in market_data.groupby('event_id'):
                event_pred = self.predict_event(group)
                
                # Calculate implied odds
                prob = event_pred.get('probability', 0.5)
                implied_odds = 1 / prob if prob > 0 else 0
                
                predictions[event_id] = {
                    'prediction': event_pred.get('prediction'),
                    'probability': event_pred.get('probability'),
                    'implied_odds': implied_odds,
                    'confidence': event_pred.get('confidence'),
                    'recommended_action': self._get_betting_recommendation(
                        event_pred, implied_odds, market_data[market_data['event_id'] == event_id]
                    )
                }
            
            return predictions
        except Exception as e:
            logger.error(f"Error predicting betting markets: {e}")
            return {}
    
    def _get_betting_recommendation(self, prediction: Dict, implied_odds: float,
                                   market_data: pd.DataFrame) -> str:
        """
        Get betting recommendation based on model prediction vs market odds.
        """
        try:
            if not prediction.get('is_confident'):
                return 'PASS'
            
            # Get market odds for the prediction
            if prediction['prediction'] == 'Win':
                market_odds = market_data.iloc[0]['odds_for'] if 'odds_for' in market_data.columns else 1.5
            else:
                market_odds = market_data.iloc[0]['odds_against'] if 'odds_against' in market_data.columns else 2.0
            
            # If implied odds are better than market odds, recommend bet
            if implied_odds > market_odds:
                return f'BUY (Value: {(implied_odds/market_odds - 1)*100:.1f}%)'
            else:
                return 'PASS (No Edge)'
        except:
            return 'PASS'
    
    def get_performance_stats(self) -> Dict:
        """
        Get prediction performance statistics.
        """
        if not self.prediction_history:
            return {}
        
        df = pd.DataFrame(self.prediction_history)
        
        stats = {
            'total_predictions': len(df),
            'confident_predictions': len(df[df['is_confident']]),
            'average_confidence': df['confidence'].mean(),
            'predictions_by_outcome': df['prediction'].value_counts().to_dict()
        }
        
        return stats
