"""Main entry point for the AI Prediction Bot"""
import logging
import pandas as pd
from config import config
from src.data_fetcher import DataFetcher
from src.feature_engineering import FeatureEngineer
from src.model import PredictionModel
from src.predictor import Predictor
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def initialize_model(config_obj):
    """
    Initialize the prediction model.
    """
    logger.info("Initializing prediction model...")
    
    # Create model
    model = PredictionModel(model_type=config_obj.MODEL_TYPE)
    
    if config_obj.MODEL_TYPE == 'ensemble':
        model.build_ensemble_model()
    elif config_obj.MODEL_TYPE == 'xgboost':
        model.build_xgboost_model()
    elif config_obj.MODEL_TYPE == 'neural_net':
        model.build_neural_network(input_dim=50)  # Adjust based on feature count
    else:
        raise ValueError(f"Unknown model type: {config_obj.MODEL_TYPE}")
    
    return model

def main():
    """
    Main entry point.
    """
    logger.info("Starting AI Prediction Bot...")
    
    # Get configuration
    env = os.getenv('FLASK_ENV', 'development')
    config_obj = config[env]
    
    # Initialize components
    data_fetcher = DataFetcher(config_obj)
    feature_engineer = FeatureEngineer(lookback_period=config_obj.LOOKBACK_PERIOD)
    model = initialize_model(config_obj)
    predictor = Predictor(
        model=model,
        feature_engineer=feature_engineer,
        confidence_threshold=config_obj.PREDICTION_CONFIDENCE_THRESHOLD
    )
    
    logger.info("AI Prediction Bot initialized successfully")
    logger.info(f"Model Type: {config_obj.MODEL_TYPE}")
    logger.info(f"Confidence Threshold: {config_obj.PREDICTION_CONFIDENCE_THRESHOLD}")
    
    # Example: Fetch and predict
    try:
        # This is a placeholder - replace with actual data fetching
        logger.info("Ready for predictions. Use the API endpoints or import this module.")
    except Exception as e:
        logger.error(f"Error in main execution: {e}")

if __name__ == '__main__':
    main()
