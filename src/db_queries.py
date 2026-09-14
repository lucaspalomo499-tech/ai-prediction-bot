"""ORM helper functions - Pre-written queries for common database operations"""
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, func
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Tuple
import logging

from src.models import (
    Event, Team, Player, PlayerSeasonStats, TeamSeasonStats, 
    Prediction, Bet, Portfolio, OddsSnapshot, Sportsbook,
    PlayerGameLog, InjuryReport, ArbitrageOpportunity, OddsComparison,
    PredictionMarketData, ModelMetrics, FeatureCalculation
)

logger = logging.getLogger(__name__)

# ============================================================================
# EVENT QUERIES
# ============================================================================

class EventQueries:
    """Queries related to sports events/games"""
    
    @staticmethod
    def get_event_by_id(session: Session, event_id: int) -> Optional[Event]:
        """Get event by ID"""
        return session.query(Event).filter(Event.id == event_id).first()
    
    @staticmethod
    def get_upcoming_events(session: Session, days: int = 7, sport_id: Optional[int] = None) -> List[Event]:
        """Get upcoming events in next N days"""
        now = datetime.utcnow()
        future = now + timedelta(days=days)
        
        query = session.query(Event).filter(
            and_(
                Event.event_date >= now,
                Event.event_date <= future,
                Event.status == 'scheduled'
            )
        )
        
        if sport_id:
            query = query.filter(Event.sport_id == sport_id)
        
        return query.order_by(Event.event_date).all()
    
    @staticmethod
    def get_recent_events(session: Session, days: int = 7, sport_id: Optional[int] = None) -> List[Event]:
        """Get recently completed events"""
        now = datetime.utcnow()
        past = now - timedelta(days=days)
        
        query = session.query(Event).filter(
            and_(
                Event.event_date >= past,
                Event.event_date <= now,
                Event.status == 'completed'
            )
        )
        
        if sport_id:
            query = query.filter(Event.sport_id == sport_id)
        
        return query.order_by(desc(Event.event_date)).all()
    
    @staticmethod
    def get_team_schedule(session: Session, team_id: int, season: int) -> List[Event]:
        """Get all games for a team in a season"""
        return session.query(Event).filter(
            and_(
                or_(
                    Event.home_team_id == team_id,
                    Event.away_team_id == team_id
                ),
                Event.season == season
            )
        ).order_by(Event.event_date).all()
    
    @staticmethod
    def get_matchup_history(session: Session, team1_id: int, team2_id: int, limit: int = 10) -> List[Event]:
        """Get head-to-head history between two teams"""
        return session.query(Event).filter(
            or_(
                and_(Event.home_team_id == team1_id, Event.away_team_id == team2_id),
                and_(Event.home_team_id == team2_id, Event.away_team_id == team1_id)
            )
        ).order_by(desc(Event.event_date)).limit(limit).all()
    
    @staticmethod
    def get_events_by_date(session: Session, date: datetime) -> List[Event]:
        """Get all events on a specific date"""
        start = date.replace(hour=0, minute=0, second=0)
        end = date.replace(hour=23, minute=59, second=59)
        
        return session.query(Event).filter(
            and_(Event.event_date >= start, Event.event_date <= end)
        ).order_by(Event.event_date).all()

# ============================================================================
# TEAM QUERIES
# ============================================================================

class TeamQueries:
    """Queries related to teams"""
    
    @staticmethod
    def get_team_by_name(session: Session, name: str) -> Optional[Team]:
        """Get team by name"""
        return session.query(Team).filter(Team.name.ilike(f"%{name}%")).first()
    
    @staticmethod
    def get_teams_by_league(session: Session, league_id: int) -> List[Team]:
        """Get all teams in a league"""
        return session.query(Team).filter(Team.league_id == league_id).all()
    
    @staticmethod
    def get_team_season_stats(session: Session, team_id: int, season: int) -> Optional[TeamSeasonStats]:
        """Get season stats for a team"""
        return session.query(TeamSeasonStats).filter(
            and_(TeamSeasonStats.team_id == team_id, TeamSeasonStats.season == season)
        ).first()
    
    @staticmethod
    def get_team_win_loss_streak(session: Session, team_id: int) -> Tuple[int, int]:
        """Get current win/loss streak for a team"""
        stats = session.query(TeamSeasonStats).filter(
            TeamSeasonStats.team_id == team_id
        ).order_by(desc(TeamSeasonStats.season)).first()
        
        if stats:
            return (stats.current_win_streak, stats.current_loss_streak)
        return (0, 0)
    
    @staticmethod
    def get_team_home_away_performance(session: Session, team_id: int, season: int) -> Dict:
        """Get home vs away win percentages"""
        stats = session.query(TeamSeasonStats).filter(
            and_(TeamSeasonStats.team_id == team_id, TeamSeasonStats.season == season)
        ).first()
        
        if stats:
            return {
                'home_win_pct': stats.home_win_pct,
                'away_win_pct': stats.away_win_pct,
                'home_wins': stats.home_wins,
                'away_wins': stats.away_wins
            }
        return {}
    
    @staticmethod
    def get_power_rankings(session: Session, season: int, limit: int = 25) -> List[Tuple[Team, TeamSeasonStats]]:
        """Get power rankings based on win percentage and strength of schedule"""
        stats = session.query(TeamSeasonStats).filter(
            TeamSeasonStats.season == season
        ).order_by(desc(TeamSeasonStats.win_percentage)).limit(limit).all()
        
        return [(stat.team, stat) for stat in stats]

# ============================================================================
# PLAYER QUERIES
# ============================================================================

class PlayerQueries:
    """Queries related to players"""
    
    @staticmethod
    def get_player_by_name(session: Session, first_name: str, last_name: str) -> Optional[Player]:
        """Get player by name"""
        return session.query(Player).filter(
            and_(
                Player.first_name.ilike(first_name),
                Player.last_name.ilike(last_name)
            )
        ).first()
    
    @staticmethod
    def get_player_season_stats(session: Session, player_id: int, season: int) -> Optional[PlayerSeasonStats]:
        """Get season stats for a player"""
        return session.query(PlayerSeasonStats).filter(
            and_(PlayerSeasonStats.player_id == player_id, PlayerSeasonStats.season == season)
        ).first()
    
    @staticmethod
    def get_player_game_logs(session: Session, player_id: int, limit: int = 10) -> List[PlayerGameLog]:
        """Get recent game logs for a player"""
        return session.query(PlayerGameLog).filter(
            PlayerGameLog.player_id == player_id
        ).order_by(desc(PlayerGameLog.created_at)).limit(limit).all()
    
    @staticmethod
    def get_team_roster(session: Session, team_id: int, season: int) -> List[PlayerSeasonStats]:
        """Get all players on a team for a season"""
        return session.query(PlayerSeasonStats).filter(
            and_(PlayerSeasonStats.team_id == team_id, PlayerSeasonStats.season == season)
        ).all()
    
    @staticmethod
    def get_leading_scorers(session: Session, league_id: int, season: int, limit: int = 10) -> List[PlayerSeasonStats]:
        """Get top scorers in a league"""
        return session.query(PlayerSeasonStats).join(Team).filter(
            and_(Team.league_id == league_id, PlayerSeasonStats.season == season)
        ).order_by(desc(PlayerSeasonStats.points_per_game)).limit(limit).all()
    
    @staticmethod
    def get_most_valuable_players(session: Session, season: int, limit: int = 10) -> List[PlayerSeasonStats]:
        """Get players by efficiency rating (PER)"""
        return session.query(PlayerSeasonStats).filter(
            PlayerSeasonStats.season == season
        ).order_by(desc(PlayerSeasonStats.player_efficiency_rating)).limit(limit).all()

# ============================================================================
# INJURY QUERIES
# ============================================================================

class InjuryQueries:
    """Queries related to injuries"""
    
    @staticmethod
    def get_injured_players(session: Session, team_id: int) -> List[InjuryReport]:
        """Get all currently injured players on a team"""
        return session.query(InjuryReport).filter(
            and_(
                InjuryReport.team_id == team_id,
                InjuryReport.status != 'healthy'
            )
        ).all()
    
    @staticmethod
    def get_out_players(session: Session, team_id: int) -> List[InjuryReport]:
        """Get players marked as 'out'"""
        return session.query(InjuryReport).filter(
            and_(
                InjuryReport.team_id == team_id,
                InjuryReport.status == 'out'
            )
        ).all()
    
    @staticmethod
    def get_player_injury_history(session: Session, player_id: int) -> List[InjuryReport]:
        """Get injury history for a player"""
        return session.query(InjuryReport).filter(
            InjuryReport.player_id == player_id
        ).order_by(desc(InjuryReport.date_injured)).all()
    
    @staticmethod
    def get_probable_players(session: Session, team_id: int) -> List[InjuryReport]:
        """Get questionable/doubtful/probable players"""
        return session.query(InjuryReport).filter(
            and_(
                InjuryReport.team_id == team_id,
                InjuryReport.status.in_(['questionable', 'doubtful', 'probable'])
            )
        ).all()

# ============================================================================
# ODDS & BETTING QUERIES
# ============================================================================

class OddsQueries:
    """Queries related to odds and betting"""
    
    @staticmethod
    def get_best_odds(session: Session, event_id: int, market_type: str = 'moneyline') -> Optional[OddsSnapshot]:
        """Get best odds for a market type"""
        if market_type == 'moneyline':
            # For moneyline, look for highest home odds or lowest away odds
            return session.query(OddsSnapshot).filter(
                and_(
                    OddsSnapshot.event_id == event_id,
                    OddsSnapshot.market_type == 'moneyline'
                )
            ).order_by(desc(OddsSnapshot.home_implied_prob)).first()
        
        return session.query(OddsSnapshot).filter(
            and_(
                OddsSnapshot.event_id == event_id,
                OddsSnapshot.market_type == market_type
            )
        ).first()
    
    @staticmethod
    def get_all_odds_for_event(session: Session, event_id: int, market_type: str = 'moneyline') -> List[OddsSnapshot]:
        """Get odds from all sportsbooks for an event"""
        return session.query(OddsSnapshot).filter(
            and_(
                OddsSnapshot.event_id == event_id,
                OddsSnapshot.market_type == market_type
            )
        ).all()
    
    @staticmethod
    def get_odds_comparison(session: Session, event_id: int) -> Optional[OddsComparison]:
        """Get odds comparison analysis"""
        return session.query(OddsComparison).filter(
            OddsComparison.event_id == event_id
        ).first()
    
    @staticmethod
    def get_line_movement(session: Session, event_id: int) -> Optional[Dict]:
        """Get line movement data"""
        from src.models import OddMovement
        movement = session.query(OddMovement).filter(
            OddMovement.event_id == event_id
        ).first()
        
        if movement:
            return {
                'opening_spread': movement.opening_spread,
                'current_spread': movement.current_spread,
                'spread_movement': movement.spread_movement,
                'sharp_money_pct': movement.sharp_money_pct,
                'public_money_pct': movement.public_money_pct
            }
        return None

# ============================================================================
# PREDICTION QUERIES
# ============================================================================

class PredictionQueries:
    """Queries related to AI predictions"""
    
    @staticmethod
    def get_predictions_for_event(session: Session, event_id: int) -> List[Prediction]:
        """Get all predictions for an event"""
        return session.query(Prediction).filter(
            Prediction.event_id == event_id
        ).all()
    
    @staticmethod
    def get_model_predictions(session: Session, model_name: str, limit: int = 100) -> List[Prediction]:
        """Get recent predictions from a specific model"""
        return session.query(Prediction).filter(
            Prediction.model_name == model_name
        ).order_by(desc(Prediction.created_at)).limit(limit).all()
    
    @staticmethod
    def get_confident_predictions(session: Session, confidence_threshold: float = 0.65, limit: int = 50) -> List[Prediction]:
        """Get predictions above confidence threshold"""
        return session.query(Prediction).filter(
            Prediction.confidence >= confidence_threshold
        ).order_by(desc(Prediction.confidence)).limit(limit).all()
    
    @staticmethod
    def get_prediction_accuracy(session: Session, model_name: str) -> Dict:
        """Calculate model accuracy"""
        total = session.query(Prediction).filter(
            and_(
                Prediction.model_name == model_name,
                Prediction.is_correct.isnot(None)
            )
        ).count()
        
        correct = session.query(Prediction).filter(
            and_(
                Prediction.model_name == model_name,
                Prediction.is_correct == True
            )
        ).count()
        
        accuracy = (correct / total * 100) if total > 0 else 0
        
        return {
            'total_predictions': total,
            'correct': correct,
            'accuracy': accuracy
        }
    
    @staticmethod
    def get_best_value_predictions(session: Session, min_edge: float = 5.0, limit: int = 20) -> List[Prediction]:
        """Get predictions with best edge vs market"""
        return session.query(Prediction).filter(
            Prediction.edge_vs_best_market >= min_edge
        ).order_by(desc(Prediction.edge_vs_best_market)).limit(limit).all()

# ============================================================================
# BETTING QUERIES
# ============================================================================

class BettingQueries:
    """Queries related to bets and portfolios"""
    
    @staticmethod
    def get_user_bets(session: Session, portfolio_id: int, status: Optional[str] = None) -> List[Bet]:
        """Get bets in a portfolio"""
        query = session.query(Bet).filter(Bet.portfolio_id == portfolio_id)
        
        if status:
            query = query.filter(Bet.status == status)
        
        return query.order_by(desc(Bet.created_at)).all()
    
    @staticmethod
    def get_pending_bets(session: Session, portfolio_id: int) -> List[Bet]:
        """Get unsettled bets"""
        return session.query(Bet).filter(
            and_(
                Bet.portfolio_id == portfolio_id,
                Bet.status == 'pending'
            )
        ).all()
    
    @staticmethod
    def calculate_portfolio_roi(session: Session, portfolio_id: int) -> float:
        """Calculate ROI for a portfolio"""
        portfolio = session.query(Portfolio).filter(Portfolio.id == portfolio_id).first()
        
        if portfolio and portfolio.starting_balance > 0:
            return ((portfolio.current_balance - portfolio.starting_balance) / portfolio.starting_balance) * 100
        return 0.0
    
    @staticmethod
    def calculate_portfolio_stats(session: Session, portfolio_id: int) -> Dict:
        """Get comprehensive portfolio statistics"""
        portfolio = session.query(Portfolio).filter(Portfolio.id == portfolio_id).first()
        
        if not portfolio:
            return {}
        
        bets = session.query(Bet).filter(Bet.portfolio_id == portfolio_id).all()
        
        won = len([b for b in bets if b.status == 'won'])
        lost = len([b for b in bets if b.status == 'lost'])
        total = len([b for b in bets if b.status in ['won', 'lost']])
        
        win_rate = (won / total * 100) if total > 0 else 0
        total_profit = sum([b.profit_loss for b in bets if b.profit_loss]) if bets else 0
        
        return {
            'current_balance': portfolio.current_balance,
            'starting_balance': portfolio.starting_balance,
            'total_bets': len(bets),
            'won': won,
            'lost': lost,
            'win_rate': win_rate,
            'roi': calculate_portfolio_roi(session, portfolio_id),
            'total_profit': total_profit,
            'avg_bet_size': portfolio.avg_bet_size,
            'max_drawdown': portfolio.max_drawdown,
            'sharpe_ratio': portfolio.sharpe_ratio
        }
    
    @staticmethod
    def get_most_profitable_bets(session: Session, portfolio_id: int, limit: int = 10) -> List[Bet]:
        """Get most profitable bets"""
        return session.query(Bet).filter(
            and_(
                Bet.portfolio_id == portfolio_id,
                Bet.profit_loss > 0
            )
        ).order_by(desc(Bet.profit_loss)).limit(limit).all()

# ============================================================================
# ARBITRAGE QUERIES
# ============================================================================

class ArbitrageQueries:
    """Queries related to arbitrage opportunities"""
    
    @staticmethod
    def get_active_arbitrage(session: Session, min_arb_pct: float = 2.0) -> List[ArbitrageOpportunity]:
        """Get active arbitrage opportunities above threshold"""
        return session.query(ArbitrageOpportunity).filter(
            and_(
                ArbitrageOpportunity.is_active == True,
                ArbitrageOpportunity.arb_percentage >= min_arb_pct
            )
        ).order_by(desc(ArbitrageOpportunity.arb_percentage)).all()
    
    @staticmethod
    def get_best_arbitrage(session: Session) -> Optional[ArbitrageOpportunity]:
        """Get arbitrage opportunity with highest profit margin"""
        return session.query(ArbitrageOpportunity).filter(
            ArbitrageOpportunity.is_active == True
        ).order_by(desc(ArbitrageOpportunity.arb_percentage)).first()
    
    @staticmethod
    def get_arbitrage_by_event(session: Session, event_id: int) -> List[ArbitrageOpportunity]:
        """Get all arbitrage opportunities for an event"""
        return session.query(ArbitrageOpportunity).filter(
            ArbitrageOpportunity.event_id == event_id
        ).all()

# ============================================================================
# MODEL QUERIES
# ============================================================================

class ModelQueries:
    """Queries related to model metrics and training"""
    
    @staticmethod
    def get_latest_model_metrics(session: Session, model_name: str) -> Optional[ModelMetrics]:
        """Get latest metrics for a model"""
        return session.query(ModelMetrics).filter(
            ModelMetrics.model_name == model_name
        ).order_by(desc(ModelMetrics.training_date)).first()
    
    @staticmethod
    def get_model_history(session: Session, model_name: str) -> List[ModelMetrics]:
        """Get training history for a model"""
        return session.query(ModelMetrics).filter(
            ModelMetrics.model_name == model_name
        ).order_by(desc(ModelMetrics.training_date)).all()
    
    @staticmethod
    def get_best_model(session: Session) -> Optional[ModelMetrics]:
        """Get best performing model by accuracy"""
        return session.query(ModelMetrics).order_by(
            desc(ModelMetrics.accuracy)
        ).first()
    
    @staticmethod
    def get_model_top_features(session: Session, model_name: str) -> Dict:
        """Get top features for a model"""
        metrics = ModelQueries.get_latest_model_metrics(session, model_name)
        if metrics and metrics.top_features:
            return metrics.top_features
        return {}
