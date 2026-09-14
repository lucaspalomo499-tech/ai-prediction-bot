import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Base configuration"""
    DEBUG = False
    TESTING = False
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key')
    
    # API Configuration
    SPORTS_API_KEY = os.getenv('SPORTS_API_KEY')
    WEATHER_API_KEY = os.getenv('WEATHER_API_KEY')
    FINNHUB_API_KEY = os.getenv('FINNHUB_API_KEY')
    
    # Database
    DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://localhost/prediction_bot')
    REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
    
    # Model Configuration
    MODEL_TYPE = os.getenv('MODEL_TYPE', 'ensemble')  # ensemble, neural_net, xgboost
    TEST_SIZE = 0.2
    VALIDATION_SIZE = 0.1
    RANDOM_STATE = 42
    
    # Prediction Markets
    PREDICTION_CONFIDENCE_THRESHOLD = 0.65
    MIN_DATA_POINTS = 100
    
    # Features
    TECHNICAL_INDICATORS = ['RSI', 'MACD', 'BB', 'SMA', 'EMA']
    LOOKBACK_PERIOD = 30  # days

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    TESTING = False

class TestingConfig(Config):
    """Testing configuration"""
    DEBUG = False
    TESTING = True
    DATABASE_URL = 'sqlite:///:memory:'

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    TESTING = False

config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}