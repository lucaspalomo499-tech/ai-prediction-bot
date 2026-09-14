"""Machine learning models for predictions"""
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score
import xgboost as xgb
import tensorflow as tf
from tensorflow import keras
import logging
import joblib
from typing import Tuple, Dict, List, Optional

logger = logging.getLogger(__name__)

class PredictionModel:
    """Base prediction model class"""
    
    def __init__(self, model_type: str = 'ensemble'):
        self.model_type = model_type
        self.model = None
        self.scaler = StandardScaler()
        self.label_encoder = LabelEncoder()
        self.feature_names = []
    
    def build_ensemble_model(self):
        """Build ensemble model combining multiple algorithms"""
        from sklearn.ensemble import VotingClassifier
        
        rf = RandomForestClassifier(n_estimators=100, max_depth=10, random_state=42)
        gb = GradientBoostingClassifier(n_estimators=100, learning_rate=0.1, random_state=42)
        lr = LogisticRegression(max_iter=1000, random_state=42)
        
        self.model = VotingClassifier(
            estimators=[('rf', rf), ('gb', gb), ('lr', lr)],
            voting='soft'
        )
        logger.info("Ensemble model built successfully")
    
    def build_xgboost_model(self):
        """Build XGBoost model"""
        self.model = xgb.XGBClassifier(
            n_estimators=200,
            learning_rate=0.05,
            max_depth=6,
            subsample=0.8,
            colsample_bytree=0.8,
            random_state=42,
            eval_metric='logloss'
        )
        logger.info("XGBoost model built successfully")
    
    def build_neural_network(self, input_dim: int):
        """Build neural network model"""
        self.model = keras.Sequential([
            keras.layers.Dense(128, activation='relu', input_dim=input_dim),
            keras.layers.Dropout(0.3),
            keras.layers.Dense(64, activation='relu'),
            keras.layers.Dropout(0.3),
            keras.layers.Dense(32, activation='relu'),
            keras.layers.Dropout(0.2),
            keras.layers.Dense(16, activation='relu'),
            keras.layers.Dense(1, activation='sigmoid')
        ])
        
        self.model.compile(
            optimizer=keras.optimizers.Adam(learning_rate=0.001),
            loss='binary_crossentropy',
            metrics=['accuracy', keras.metrics.AUC()]
        )
        logger.info("Neural network model built successfully")
    
    def prepare_data(self, X: pd.DataFrame, y: pd.Series, test_size: float = 0.2,
                    validation_size: float = 0.1) -> Tuple:
        """
        Prepare and split data for training.
        """
        self.feature_names = X.columns.tolist()
        
        # Remove NaN values
        mask = ~(X.isna().any(axis=1) | y.isna())
        X = X[mask]
        y = y[mask]
        
        # Encode labels if necessary
        if y.dtype == 'object':
            y = self.label_encoder.fit_transform(y)
        
        # Split into train and test
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=42
        )
        
        # Further split train into train and validation
        val_size = validation_size / (1 - test_size)
        X_train, X_val, y_train, y_val = train_test_split(
            X_train, y_train, test_size=val_size, random_state=42
        )
        
        # Scale features
        X_train = self.scaler.fit_transform(X_train)
        X_val = self.scaler.transform(X_val)
        X_test = self.scaler.transform(X_test)
        
        logger.info(f"Data prepared: Train={X_train.shape}, Val={X_val.shape}, Test={X_test.shape}")
        
        return X_train, X_val, X_test, y_train, y_val, y_test
    
    def train(self, X_train: np.ndarray, y_train: np.ndarray,
             X_val: Optional[np.ndarray] = None, y_val: Optional[np.ndarray] = None):
        """
        Train the model.
        """
        if self.model is None:
            raise ValueError("Model not built. Call build_*_model() first.")
        
        if isinstance(self.model, keras.Model):
            self.model.fit(
                X_train, y_train,
                validation_data=(X_val, y_val) if X_val is not None else None,
                epochs=50,
                batch_size=32,
                verbose=1
            )
        else:
            self.model.fit(X_train, y_train)
        
        logger.info("Model training completed")
    
    def predict(self, X: np.ndarray) -> np.ndarray:
        """
        Make predictions.
        """
        if self.model is None:
            raise ValueError("Model not trained yet.")
        
        if isinstance(self.model, keras.Model):
            return self.model.predict(X)
        else:
            return self.model.predict(X)
    
    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        """
        Get prediction probabilities.
        """
        if self.model is None:
            raise ValueError("Model not trained yet.")
        
        if isinstance(self.model, keras.Model):
            return self.model.predict(X)
        else:
            return self.model.predict_proba(X)
    
    def evaluate(self, X_test: np.ndarray, y_test: np.ndarray) -> Dict:
        """
        Evaluate model performance.
        """
        y_pred = self.predict(X_test)
        y_pred_binary = (y_pred > 0.5).astype(int).flatten()
        
        metrics = {
            'accuracy': accuracy_score(y_test, y_pred_binary),
            'precision': precision_score(y_test, y_pred_binary, zero_division=0),
            'recall': recall_score(y_test, y_pred_binary, zero_division=0),
            'f1': f1_score(y_test, y_pred_binary, zero_division=0),
        }
        
        try:
            metrics['auc'] = roc_auc_score(y_test, y_pred)
        except:
            metrics['auc'] = 0
        
        logger.info(f"Model evaluation metrics: {metrics}")
        return metrics
    
    def save(self, filepath: str):
        """Save model to disk"""
        if isinstance(self.model, keras.Model):
            self.model.save(filepath)
        else:
            joblib.dump(self.model, filepath)
        logger.info(f"Model saved to {filepath}")
    
    def load(self, filepath: str):
        """Load model from disk"""
        try:
            self.model = keras.models.load_model(filepath)
        except:
            self.model = joblib.load(filepath)
        logger.info(f"Model loaded from {filepath}")
