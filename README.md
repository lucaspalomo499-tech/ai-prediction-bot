# 🤖 AI Prediction Bot - Sports Betting & Prediction Markets

An enterprise-grade machine learning system for predicting sports outcomes and identifying betting opportunities across multiple sports and prediction markets.

## 📋 Table of Contents

- [Features](#features)
- [Architecture](#architecture)
- [Installation](#installation)
- [Database Setup](#database-setup)
- [Usage Examples](#usage-examples)
- [API Documentation](#api-documentation)
- [Database Models](#database-models)
- [Contributing](#contributing)

---

## ✨ Features

### Core Capabilities
- **Multi-Sport Support**: NFL, NBA, MLB, Soccer, Hockey, Golf, Tennis, NCAA
- **Multiple Sportsbooks**: DraftKings, FanDuel, BetMGM, Caesars, and 6+ more
- **Prediction Markets**: Polymarket, Manifold, and other crypto prediction markets
- **Advanced ML Models**: Ensemble, XGBoost, and Neural Networks
- **Technical Analysis**: RSI, MACD, Bollinger Bands, Moving Averages
- **Team Analytics**: Win streaks, home/away splits, strength of schedule
- **Player Tracking**: Season stats, game logs, injury reports
- **Odds Comparison**: Real-time odds from all major sportsbooks
- **Arbitrage Detection**: Identify cross-sportsbook arbitrage opportunities
- **Portfolio Management**: Track bets, ROI, Sharpe ratio, drawdown
- **Risk Analysis**: Kelly Criterion, Expected Value, Confidence intervals

### Database Features
- **37 Database Models** covering all aspects of sports betting
- **Multi-Sport Stats**: NFL, NBA, Soccer, Baseball specific metrics
- **Historical Data**: Season stats, game logs, player performances
- **Betting Data**: Odds history, line movement, arbitrage opportunities
- **Prediction Tracking**: Model predictions, accuracy, edge analysis
- **Portfolio Management**: Bet tracking, performance analytics

---

## 🏗️ Architecture

```
ai-prediction-bot/
├── config.py                 # Configuration management
├── init_db.py               # Database initialization
├── main.py                  # Entry point
│
├── src/
│   ├── models.py            # 37 SQLAlchemy database models
│   ├── sport_models.py      # Sport-specific models (NFL, NBA, Soccer, etc.)
│   ├── data_fetcher.py      # API data fetching
│   ├── feature_engineering.py # ML feature creation
│   ├── model.py             # ML model implementations
│   ├── predictor.py         # Prediction engine
│   ├── api.py               # Flask REST API
│   ├── db_queries.py        # ORM helper functions (80+ queries)
│   └── db_migrations.py     # Database migration system
│
├── requirements.txt         # Python dependencies
└── .env.example            # Environment variables template
```

---

## 💾 Database Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment

Copy `.env.example` to `.env` and fill in your API keys:

```bash
cp .env.example .env
```

Edit `.env`:
```env
FLASK_ENV=development
DATABASE_URL=postgresql://user:password@localhost/prediction_bot
SPORTS_API_KEY=your_sports_api_key
FINNHUB_API_KEY=your_finnhub_key
```

### 3. Initialize Database

```bash
# Creates all 37 tables and seeds initial data
python init_db.py

# Or to drop existing tables first (destructive):
python init_db.py --drop
```

This will:
- ✓ Create all database tables
- ✓ Add 10 sports (NFL, NBA, MLB, Soccer, etc.)
- ✓ Add 10 sportsbooks (DraftKings, FanDuel, etc.)
- ✓ Add 8 leagues with seasons

### 4. Run Migrations (for updates)

```bash
# Create a new migration
python -m src.db_migrations create "add_stadium_capacity_to_teams"

# Apply latest migrations
python -m src.db_migrations upgrade

# Rollback one step
python -m src.db_migrations downgrade

# Show migration history
python -m src.db_migrations history
```

---

## 🚀 Usage Examples

### Initialize the Application

```python
from config import config
from src.data_fetcher import DataFetcher
from src.feature_engineering import FeatureEngineer
from src.model import PredictionModel
from src.predictor import Predictor
from sqlalchemy.orm import Session

env = 'development'
config_obj = config[env]

# Create components
data_fetcher = DataFetcher(config_obj)
feature_engineer = FeatureEngineer(lookback_period=30)
model = PredictionModel(model_type='ensemble')
model.build_ensemble_model()

predictor = Predictor(
    model=model,
    feature_engineer=feature_engineer,
    confidence_threshold=0.65
)
```

### Database Queries

```python
from src.db_queries import (
    EventQueries, TeamQueries, PlayerQueries,
    OddsQueries, PredictionQueries, BettingQueries,
    ArbitrageQueries
)
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Connect to database
engine = create_engine(config_obj.DATABASE_URL)
Session = sessionmaker(bind=engine)
session = Session()

# Get upcoming games
upcoming = EventQueries.get_upcoming_events(session, days=7)
print(f"Found {len(upcoming)} games in next 7 days")

# Get team season stats
stats = TeamQueries.get_team_season_stats(session, team_id=1, season=2024)
print(f"Team wins: {stats.wins}, losses: {stats.losses}")

# Get injured players
injuries = PlayerQueries.get_injured_players(session, team_id=1)
for injury in injuries:
    print(f"{injury.player.first_name} - {injury.injury_type}")

# Get best odds
odds = OddsQueries.get_best_odds(session, event_id=1, market_type='moneyline')
print(f"Best home odds: {odds.home_moneyline} from {odds.sportsbook.name}")

# Find arbitrage opportunities
arbs = ArbitrageQueries.get_active_arbitrage(session, min_arb_pct=2.0)
for arb in arbs:
    print(f"Arbitrage opportunity: {arb.arb_percentage}% profit")

# Get portfolio performance
portfolio_stats = BettingQueries.calculate_portfolio_stats(session, portfolio_id=1)
print(f"Portfolio ROI: {portfolio_stats['roi']}%")
print(f"Win Rate: {portfolio_stats['win_rate']}%")
```

### Make Predictions

```python
import pandas as pd

# Fetch event data
event_data = pd.DataFrame({
    'close': [100, 102, 101, 103, 104, 105, 104, 106, 107, 108],
    'volume': [1000, 1100, 900, 1200, 1300, 1400, 1100, 1500, 1600, 1700]
})

# Make prediction
prediction = predictor.predict_event(event_data)

print(f"Prediction: {prediction['prediction']}")
print(f"Probability: {prediction['probability']:.2%}")
print(f"Confidence: {prediction['confidence']:.2%}")
print(f"Betting Recommendation: {prediction.get('betting_recommendation', 'N/A')}")
```

### REST API Usage

```bash
# Start the Flask API
python src/api.py

# In another terminal, make requests:

# Health check
curl http://localhost:5000/health

# Single event prediction
curl -X POST http://localhost:5000/api/v1/predict/event \
  -H "Content-Type: application/json" \
  -d '{
    "event_data": {"close": 100, "volume": 1000},
    "event_type": "sports"
  }'

# Multiple predictions
curl -X POST http://localhost:5000/api/v1/predict/multiple \
  -H "Content-Type: application/json" \
  -d '{
    "events": [
      {"close": 100, "volume": 1000},
      {"close": 101, "volume": 1100}
    ]
  }'

# Prediction markets
curl -X POST http://localhost:5000/api/v1/predict/markets \
  -H "Content-Type: application/json" \
  -d '{
    "market_data": [{"event_id": 1, "odds_for": 1.5}]
  }'

# Get performance stats
curl http://localhost:5000/api/v1/stats/performance

# Get model status
curl http://localhost:5000/api/v1/model/status
```

---

## 📚 Database Models Overview

### Core Sports Data (5 models)
- **Sport**: Sports categories (NFL, NBA, MLB, Soccer, etc.)
- **League**: Specific leagues (NFL, Premier League, NBA, etc.)
- **Team**: Sports teams with venue and history
- **Player**: Individual player information
- **Event**: Games/matches with scores and weather

### Team Performance (3 models)
- **TeamSeasonStats**: Complete season statistics
- **TeamAdvancedMetrics**: Pythagorean expectation, efficiency ratings
- **PlayerSeasonStats**: Individual player season stats

### Game Details (1 model)
- **PlayerGameLog**: Box scores for each player per game

### Injuries (1 model)
- **InjuryReport**: Player injury tracking with recovery dates

### Betting & Odds (5 models)
- **Sportsbook**: Betting platforms (DraftKings, FanDuel, etc.)
- **OddsSnapshot**: Historical odds from all sportsbooks
- **OddMovement**: Line movement and sharp action tracking
- **Prediction**: AI model predictions with confidence and edge
- **Bet**: Individual bets with ROI and status

### Portfolios (1 model)
- **Portfolio**: User betting accounts with performance metrics

### Users (1 model)
- **User**: User accounts with preferences

### Model Performance (3 models)
- **ModelMetrics**: Model accuracy and betting ROI
- **TrainingData**: Historical training samples
- **FeatureCalculation**: Cached technical indicators and metrics

### Market Data (3 models)
- **PredictionMarketData**: Polymarket, Manifold data
- **ArbitrageOpportunity**: Cross-sportsbook arbitrage
- **OddsComparison**: Best/worst odds comparison

### Sport-Specific Models (10 models)
- **NFL**: Game stats, player stats, injury reports
- **NBA**: Game stats, player stats, clutch performance
- **Soccer**: Game stats, player stats with xG, xA
- **Baseball**: Game stats, player stats with WAR
- **General**: Sport-agnostic performance metrics

---

## 📡 API Endpoints

### Predictions
- `POST /api/v1/predict/event` - Single event prediction
- `POST /api/v1/predict/multiple` - Batch predictions
- `POST /api/v1/predict/markets` - Betting market predictions

### Analytics
- `GET /api/v1/stats/performance` - Prediction performance stats
- `GET /api/v1/model/status` - Model status and info

### Health
- `GET /health` - Health check

---

## 🎯 Key Features by Use Case

### Sports Betting
- ✅ Moneyline predictions
- ✅ Spread predictions
- ✅ Over/Under predictions
- ✅ Player prop bets
- ✅ Parlay analysis
- ✅ Odds comparison
- ✅ Arbitrage detection

### Portfolio Management
- ✅ Bet tracking
- ✅ ROI calculation
- ✅ Win rate analysis
- ✅ Sharpe/Sortino ratios
- ✅ Max drawdown tracking
- ✅ Kelly Criterion sizing

### Data Analysis
- ✅ Team performance trends
- ✅ Player efficiency ratings
- ✅ Injury impact analysis
- ✅ Home/away splits
- ✅ Strength of schedule
- ✅ Head-to-head history

### Prediction Markets
- ✅ Polymarket integration
- ✅ Manifold integration
- ✅ Probability comparison
- ✅ Arbitrage in crypto markets

---

## 📊 Available Queries (80+)

### Event Queries
`get_event_by_id`, `get_upcoming_events`, `get_recent_events`, `get_team_schedule`, `get_matchup_history`, `get_events_by_date`

### Team Queries
`get_team_by_name`, `get_teams_by_league`, `get_team_season_stats`, `get_team_win_loss_streak`, `get_team_home_away_performance`, `get_power_rankings`

### Player Queries
`get_player_by_name`, `get_player_season_stats`, `get_player_game_logs`, `get_team_roster`, `get_leading_scorers`, `get_most_valuable_players`

### Injury Queries
`get_injured_players`, `get_out_players`, `get_player_injury_history`, `get_probable_players`

### Odds Queries
`get_best_odds`, `get_all_odds_for_event`, `get_odds_comparison`, `get_line_movement`

### Prediction Queries
`get_predictions_for_event`, `get_model_predictions`, `get_confident_predictions`, `get_prediction_accuracy`, `get_best_value_predictions`

### Betting Queries
`get_user_bets`, `get_pending_bets`, `calculate_portfolio_roi`, `calculate_portfolio_stats`, `get_most_profitable_bets`

### Arbitrage Queries
`get_active_arbitrage`, `get_best_arbitrage`, `get_arbitrage_by_event`

### Model Queries
`get_latest_model_metrics`, `get_model_history`, `get_best_model`, `get_model_top_features`

---

## 🔧 Configuration

Edit `config.py` to adjust:
- Model type (ensemble, xgboost, neural_net)
- Prediction confidence threshold (default 0.65)
- Lookback period for features (default 30 days)
- Technical indicators to use
- Min data points required
- Database URLs
- API keys

---

## 📦 Dependencies

- SQLAlchemy (ORM)
- Flask (REST API)
- TensorFlow/Keras (Neural Networks)
- XGBoost (Gradient Boosting)
- scikit-learn (ML utilities)
- pandas (Data manipulation)
- numpy (Numerical computing)
- requests (HTTP)
- python-dotenv (Environment variables)

---

## 🚨 Important Notes

1. **API Keys Required**: Set your API keys in `.env` before running
2. **Database Setup**: Run `init_db.py` before using the application
3. **Production Ready**: Includes migrations, logging, error handling
4. **Type Safe**: Full type hints for IDE support
5. **Scalable**: Designed for thousands of predictions daily

---

## 📄 License

MIT License - See LICENSE file for details

---

## 🤝 Contributing

1. Create a feature branch
2. Add tests for new functionality
3. Ensure migrations for any schema changes
4. Submit pull request

---

## 📞 Support

For issues or questions:
1. Check database initialization
2. Verify API keys are set
3. Review logs in `logs/` directory
4. Check documentation in each module

---

**Ready to start predicting?** Run `python init_db.py` and `python main.py` to get started!
