"""Feature engineering for prediction models"""
import pandas as pd
import numpy as np
from typing import Tuple, List
import logging

logger = logging.getLogger(__name__)

class FeatureEngineer:
    """Create and engineer features for ML models"""
    
    def __init__(self, lookback_period: int = 30):
        self.lookback_period = lookback_period
    
    def add_technical_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Add technical indicators to dataframe.
        Requires OHLCV data.
        """
        try:
            # Simple Moving Averages
            df['SMA_7'] = df['close'].rolling(window=7).mean()
            df['SMA_14'] = df['close'].rolling(window=14).mean()
            df['SMA_30'] = df['close'].rolling(window=30).mean()
            
            # Exponential Moving Average
            df['EMA_12'] = df['close'].ewm(span=12, adjust=False).mean()
            df['EMA_26'] = df['close'].ewm(span=26, adjust=False).mean()
            
            # Relative Strength Index (RSI)
            df['RSI'] = self._calculate_rsi(df['close'], period=14)
            
            # MACD
            df['MACD'], df['MACD_Signal'], df['MACD_Hist'] = self._calculate_macd(df['close'])
            
            # Bollinger Bands
            df['BB_Upper'], df['BB_Middle'], df['BB_Lower'] = self._calculate_bollinger_bands(df['close'])
            
            # Volume indicators
            if 'volume' in df.columns:
                df['Volume_SMA'] = df['volume'].rolling(window=14).mean()
                df['Volume_Change'] = df['volume'].pct_change()
            
            logger.info("Technical indicators added successfully")
            return df
        except Exception as e:
            logger.error(f"Error adding technical indicators: {e}")
            return df
    
    def add_statistical_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Add statistical features derived from price data.
        """
        try:
            # Returns
            df['Daily_Return'] = df['close'].pct_change()
            df['Log_Return'] = np.log(df['close'] / df['close'].shift(1))
            
            # Volatility
            df['Volatility_7'] = df['Daily_Return'].rolling(window=7).std()
            df['Volatility_14'] = df['Daily_Return'].rolling(window=14).std()
            df['Volatility_30'] = df['Daily_Return'].rolling(window=30).std()
            
            # Skewness and Kurtosis
            df['Skewness'] = df['Daily_Return'].rolling(window=14).skew()
            df['Kurtosis'] = df['Daily_Return'].rolling(window=14).kurt()
            
            # Price momentum
            df['Momentum_5'] = df['close'] - df['close'].shift(5)
            df['Momentum_10'] = df['close'] - df['close'].shift(10)
            
            # Rate of Change
            df['ROC_14'] = ((df['close'] - df['close'].shift(14)) / df['close'].shift(14)) * 100
            
            logger.info("Statistical features added successfully")
            return df
        except Exception as e:
            logger.error(f"Error adding statistical features: {e}")
            return df
    
    def add_team_performance_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Add team-specific features for sports predictions.
        """
        try:
            # Win/Loss streaks
            df['Recent_Wins'] = (df['result'] == 'W').rolling(window=5).sum()
            df['Recent_Losses'] = (df['result'] == 'L').rolling(window=5).sum()
            
            # Scoring averages
            df['Avg_Points_5'] = df['points_for'].rolling(window=5).mean()
            df['Avg_Points_Allowed_5'] = df['points_against'].rolling(window=5).mean()
            
            # Point differential
            df['Point_Diff'] = df['points_for'] - df['points_against']
            df['Avg_Point_Diff_5'] = df['Point_Diff'].rolling(window=5).mean()
            
            # Home/Away performance
            if 'is_home' in df.columns:
                df['Home_Win_Pct'] = (df[df['is_home']]['result'] == 'W').rolling(window=5).mean()
            
            logger.info("Team performance features added successfully")
            return df
        except Exception as e:
            logger.error(f"Error adding team performance features: {e}")
            return df
    
    @staticmethod
    def _calculate_rsi(prices: pd.Series, period: int = 14) -> pd.Series:
        """Calculate Relative Strength Index"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    @staticmethod
    def _calculate_macd(prices: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9):
        """Calculate MACD"""
        ema_fast = prices.ewm(span=fast, adjust=False).mean()
        ema_slow = prices.ewm(span=slow, adjust=False).mean()
        macd = ema_fast - ema_slow
        macd_signal = macd.ewm(span=signal, adjust=False).mean()
        macd_hist = macd - macd_signal
        return macd, macd_signal, macd_hist
    
    @staticmethod
    def _calculate_bollinger_bands(prices: pd.Series, period: int = 20, num_std: float = 2):
        """Calculate Bollinger Bands"""
        sma = prices.rolling(window=period).mean()
        std = prices.rolling(window=period).std()
        upper = sma + (std * num_std)
        lower = sma - (std * num_std)
        return upper, sma, lower
