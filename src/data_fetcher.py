"""Data fetching module for sports, market, and financial data"""
import requests
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)

class DataFetcher:
    """Fetch data from various APIs for prediction models"""
    
    def __init__(self, config):
        self.config = config
        self.sports_api_key = config.SPORTS_API_KEY
        self.finnhub_api_key = config.FINNHUB_API_KEY
    
    def fetch_sports_data(self, sport: str, league: str) -> pd.DataFrame:
        """
        Fetch historical sports data for a given sport and league.
        Supports: NFL, NBA, MLB, MLS, Premier League
        """
        try:
            # Example: ESPN or ESPN API integration
            base_url = "https://api.sportsdata.io/v3"
            endpoint = f"/{sport.lower()}/scores/json/Games"
            
            params = {
                'key': self.sports_api_key
            }
            
            response = requests.get(base_url + endpoint, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            df = pd.DataFrame(data)
            
            logger.info(f"Fetched {len(df)} records for {sport} {league}")
            return df
        except Exception as e:
            logger.error(f"Error fetching sports data: {e}")
            return pd.DataFrame()
    
    def fetch_financial_data(self, symbol: str, period: str = '1y') -> pd.DataFrame:
        """
        Fetch financial/stock data for prediction markets.
        Uses yfinance for stock data.
        """
        try:
            import yfinance as yf
            ticker = yf.Ticker(symbol)
            df = ticker.history(period=period)
            
            logger.info(f"Fetched financial data for {symbol}")
            return df
        except Exception as e:
            logger.error(f"Error fetching financial data: {e}")
            return pd.DataFrame()
    
    def fetch_weather_data(self, latitude: float, longitude: float) -> Dict:
        """
        Fetch weather data that might affect sporting events.
        """
        try:
            base_url = "https://api.open-meteo.com/v1/forecast"
            params = {
                'latitude': latitude,
                'longitude': longitude,
                'hourly': 'temperature_2m,windspeed_10m,precipitation',
                'daily': 'temperature_2m_max,precipitation_sum,windspeed_10m_max'
            }
            
            response = requests.get(base_url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            logger.info(f"Fetched weather data for lat:{latitude}, lon:{longitude}")
            return data
        except Exception as e:
            logger.error(f"Error fetching weather data: {e}")
            return {}
    
    def fetch_odds_data(self, event_id: str) -> Dict:
        """
        Fetch current odds from betting markets.
        """
        try:
            # Integration with odds API (e.g., The Odds API)
            base_url = "https://api.the-odds-api.com/v4"
            endpoint = f"/sports/{event_id}/odds"
            
            params = {
                'apiKey': self.sports_api_key,
                'regions': 'us,uk',
                'markets': 'h2h,spreads'
            }
            
            response = requests.get(base_url + endpoint, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            logger.info(f"Fetched odds for event {event_id}")
            return data
        except Exception as e:
            logger.error(f"Error fetching odds data: {e}")
            return {}
