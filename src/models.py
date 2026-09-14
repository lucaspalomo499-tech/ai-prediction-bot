"""SQLAlchemy database models for the prediction bot"""
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, ForeignKey, JSON, Text, UniqueConstraint, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

# ============================================================================
# CORE SPORTS DATA MODELS
# ============================================================================

class Sport(Base):
    """Sports categories"""
    __tablename__ = 'sports'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True, nullable=False)  # NFL, NBA, MLB, Soccer, etc.
    slug = Column(String(50), unique=True, nullable=False)
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    leagues = relationship('League', back_populates='sport')
    teams = relationship('Team', back_populates='sport')
    events = relationship('Event', back_populates='sport')
    
    def __repr__(self):
        return f"<Sport {self.name}>"

class League(Base):
    """Sports leagues"""
    __tablename__ = 'leagues'
    
    id = Column(Integer, primary_key=True)
    sport_id = Column(Integer, ForeignKey('sports.id'), nullable=False)
    name = Column(String(100), nullable=False)
    slug = Column(String(100), nullable=False)
    country = Column(String(50))
    season = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        UniqueConstraint('sport_id', 'slug', name='uq_sport_league'),
        Index('ix_sport_id', 'sport_id'),
    )
    
    sport = relationship('Sport', back_populates='leagues')
    teams = relationship('Team', back_populates='league')
    events = relationship('Event', back_populates='league')
    
    def __repr__(self):
        return f"<League {self.name}>"

class Team(Base):
    """Sports teams"""
    __tablename__ = 'teams'
    
    id = Column(Integer, primary_key=True)
    sport_id = Column(Integer, ForeignKey('sports.id'), nullable=False)
    league_id = Column(Integer, ForeignKey('leagues.id'), nullable=False)
    external_team_id = Column(String(100))  # ESPN ID, etc
    name = Column(String(100), nullable=False)
    slug = Column(String(100), nullable=False)
    city = Column(String(100))
    abbreviation = Column(String(10))
    logo_url = Column(String(255))
    stadium = Column(String(255))
    founded_year = Column(Integer)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        UniqueConstraint('league_id', 'slug', name='uq_league_team'),
        Index('ix_sport_id', 'sport_id'),
        Index('ix_league_id', 'league_id'),
    )
    
    sport = relationship('Sport', back_populates='teams')
    league = relationship('League', back_populates='teams')
    home_events = relationship('Event', foreign_keys='Event.home_team_id', back_populates='home_team')
    away_events = relationship('Event', foreign_keys='Event.away_team_id', back_populates='away_team')
    team_stats = relationship('TeamSeasonStats', back_populates='team')
    player_stats = relationship('PlayerSeasonStats', back_populates='team')
    advanced_metrics = relationship('TeamAdvancedMetrics', back_populates='team')
    injury_reports = relationship('InjuryReport', back_populates='team')
    
    def __repr__(self):
        return f"<Team {self.name}>"

class Player(Base):
    """Individual players"""
    __tablename__ = 'players'
    
    id = Column(Integer, primary_key=True)
    external_player_id = Column(String(100), unique=True)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    position = Column(String(50))
    jersey_number = Column(Integer)
    height = Column(String(20))
    weight = Column(Integer)
    date_of_birth = Column(DateTime)
    nationality = Column(String(50))
    college = Column(String(100))
    drafted_year = Column(Integer)
    draft_round = Column(Integer)
    draft_pick = Column(Integer)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    __table_args__ = (
        Index('ix_external_player_id', 'external_player_id'),
        Index('ix_position', 'position'),
    )
    
    player_stats = relationship('PlayerSeasonStats', back_populates='player')
    game_logs = relationship('PlayerGameLog', back_populates='player')
    injuries = relationship('InjuryReport', back_populates='player')
    
    def __repr__(self):
        return f"<Player {self.first_name} {self.last_name}>"

# ============================================================================
# EVENTS & GAME DATA MODELS
# ============================================================================

class Event(Base):
    """Sports events/games"""
    __tablename__ = 'events'
    
    id = Column(Integer, primary_key=True)
    sport_id = Column(Integer, ForeignKey('sports.id'), nullable=False)
    league_id = Column(Integer, ForeignKey('leagues.id'), nullable=False)
    home_team_id = Column(Integer, ForeignKey('teams.id'), nullable=False)
    away_team_id = Column(Integer, ForeignKey('teams.id'), nullable=False)
    season = Column(Integer, nullable=False)
    week = Column(Integer)  # Week of season
    game_number = Column(Integer)
    external_event_id = Column(String(100))
    
    # Event details
    event_date = Column(DateTime, nullable=False)
    kickoff_time = Column(DateTime)
    venue = Column(String(255))
    venue_id = Column(String(100))
    timezone = Column(String(50))
    
    # Outcome
    home_score = Column(Integer)
    away_score = Column(Integer)
    winner_id = Column(Integer, ForeignKey('teams.id'))
    status = Column(String(20))  # scheduled, in_progress, completed, postponed, cancelled
    is_neutral_site = Column(Boolean, default=False)
    is_playoff = Column(Boolean, default=False)
    
    # Weather
    weather_conditions = Column(JSON)  # {temperature, wind_speed, precipitation, humidity}
    
    # Attendance
    attendance = Column(Integer)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    __table_args__ = (
        UniqueConstraint('sport_id', 'external_event_id', name='uq_sport_event'),
        Index('ix_sport_id', 'sport_id'),
        Index('ix_league_id', 'league_id'),
        Index('ix_home_team_id', 'home_team_id'),
        Index('ix_away_team_id', 'away_team_id'),
        Index('ix_event_date', 'event_date'),
        Index('ix_status', 'status'),
        Index('ix_season', 'season'),
    )
    
    sport = relationship('Sport', back_populates='events')
    league = relationship('League', back_populates='events')
    home_team = relationship('Team', foreign_keys=[home_team_id], back_populates='home_events')
    away_team = relationship('Team', foreign_keys=[away_team_id], back_populates='away_events')
    
    predictions = relationship('Prediction', back_populates='event')
    odds_history = relationship('OddsSnapshot', back_populates='event')
    player_game_logs = relationship('PlayerGameLog', back_populates='event')
    
    def __repr__(self):
        return f"<Event {self.home_team.name} vs {self.away_team.name}>"

class PlayerGameLog(Base):
    """Individual player performance in a specific game"""
    __tablename__ = 'player_game_logs'
    
    id = Column(Integer, primary_key=True)
    event_id = Column(Integer, ForeignKey('events.id'), nullable=False)
    player_id = Column(Integer, ForeignKey('players.id'), nullable=False)
    team_id = Column(Integer, ForeignKey('teams.id'), nullable=False)
    
    # Sport-agnostic stats (more in sport-specific extensions)
    minutes_played = Column(Float)
    games_started = Column(Boolean)
    
    # Basketball stats
    points = Column(Integer)
    rebounds = Column(Integer)
    assists = Column(Integer)
    steals = Column(Integer)
    blocks = Column(Integer)
    turnovers = Column(Integer)
    fouls = Column(Integer)
    field_goals_made = Column(Integer)
    field_goals_attempted = Column(Integer)
    three_pointers_made = Column(Integer)
    three_pointers_attempted = Column(Integer)
    free_throws_made = Column(Integer)
    free_throws_attempted = Column(Integer)
    plus_minus = Column(Float)
    
    # Football stats
    passing_yards = Column(Integer)
    passing_touchdowns = Column(Integer)
    interceptions = Column(Integer)
    rushing_yards = Column(Integer)
    rushing_touchdowns = Column(Integer)
    receiving_yards = Column(Integer)
    receiving_touchdowns = Column(Integer)
    receptions = Column(Integer)
    tackles = Column(Integer)
    sacks = Column(Float)
    
    # Soccer stats
    goals = Column(Integer)
    assists_soccer = Column(Integer)
    shots_on_target = Column(Integer)
    pass_completion_pct = Column(Float)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        Index('ix_event_id', 'event_id'),
        Index('ix_player_id', 'player_id'),
        Index('ix_team_id', 'team_id'),
    )
    
    event = relationship('Event', back_populates='player_game_logs')
    player = relationship('Player', back_populates='game_logs')
    team = relationship('Team')
    
    def __repr__(self):
        return f"<PlayerGameLog {self.player.first_name} - Event {self.event_id}>"

# ============================================================================
# TEAM STATISTICS & PERFORMANCE MODELS
# ============================================================================

class TeamSeasonStats(Base):
    """Complete team season statistics"""
    __tablename__ = 'team_season_stats'
    
    id = Column(Integer, primary_key=True)
    team_id = Column(Integer, ForeignKey('teams.id'), nullable=False)
    season = Column(Integer, nullable=False)
    league_id = Column(Integer, ForeignKey('leagues.id'), nullable=False)
    
    # Record
    games_played = Column(Integer, default=0)
    wins = Column(Integer, default=0)
    losses = Column(Integer, default=0)
    draws = Column(Integer, default=0)
    win_percentage = Column(Float)
    
    # Scoring
    points_for = Column(Float)
    points_against = Column(Float)
    points_diff = Column(Float)
    avg_points_per_game = Column(Float)
    avg_points_allowed = Column(Float)
    
    # Home/Away splits
    home_wins = Column(Integer)
    home_losses = Column(Integer)
    home_win_pct = Column(Float)
    away_wins = Column(Integer)
    away_losses = Column(Integer)
    away_win_pct = Column(Float)
    
    # Streaks
    current_win_streak = Column(Integer, default=0)
    current_loss_streak = Column(Integer, default=0)
    longest_win_streak = Column(Integer, default=0)
    longest_loss_streak = Column(Integer, default=0)
    
    # Advanced metrics
    strength_of_schedule = Column(Float)
    strength_of_victory = Column(Float)
    strength_of_loss = Column(Float)
    
    # Playoff seeding
    playoff_seed = Column(Integer)
    playoff_clinched = Column(Boolean, default=False)
    
    # Net stats
    net_rating = Column(Float)  # Basketball
    offensive_rating = Column(Float)
    defensive_rating = Column(Float)
    pace = Column(Float)  # Possessions per 48 minutes
    
    # Soccer specific
    goals_for = Column(Integer)
    goals_against = Column(Integer)
    goal_diff = Column(Integer)
    possession_pct = Column(Float)
    shots_for = Column(Integer)
    shots_against = Column(Integer)
    shots_on_target_for = Column(Integer)
    shots_on_target_against = Column(Integer)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    __table_args__ = (
        UniqueConstraint('team_id', 'season', name='uq_team_season'),
        Index('ix_team_id', 'team_id'),
        Index('ix_season', 'season'),
        Index('ix_league_id', 'league_id'),
    )
    
    team = relationship('Team', back_populates='team_stats')
    league = relationship('League')
    
    def __repr__(self):
        return f"<TeamSeasonStats {self.team.name} {self.season}>"

class TeamAdvancedMetrics(Base):
    """Advanced analytics for teams"""
    __tablename__ = 'team_advanced_metrics'
    
    id = Column(Integer, primary_key=True)
    team_id = Column(Integer, ForeignKey('teams.id'), nullable=False)
    season = Column(Integer, nullable=False)
    
    # Expected values
    expected_wins = Column(Float)  # Pythagorean expectation
    luck_factor = Column(Float)  # Actual wins - Expected wins
    
    # Advanced efficiency
    true_shooting_pct = Column(Float)
    effective_fg_pct = Column(Float)
    turnover_rate = Column(Float)
    free_throw_rate = Column(Float)
    
    # Four factors
    pace_factor = Column(Float)
    efg_rating = Column(Float)
    tov_rating = Column(Float)
    frb_rating = Column(Float)  # Free throw and rebound rating
    
    # Clustering metrics
    ball_movement_index = Column(Float)
    spacing_score = Column(Float)
    
    # Predictive metrics
    win_shares = Column(Float)
    player_efficiency_rating = Column(Float)
    team_power_rating = Column(Float)
    
    # Durability
    days_of_rest_avg = Column(Float)
    back_to_back_record = Column(String(20))
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    __table_args__ = (
        UniqueConstraint('team_id', 'season', name='uq_team_metrics'),
        Index('ix_team_id', 'team_id'),
    )
    
    team = relationship('Team', back_populates='advanced_metrics')
    
    def __repr__(self):
        return f"<TeamAdvancedMetrics {self.team.name} {self.season}>"

class PlayerSeasonStats(Base):
    """Individual player season statistics"""
    __tablename__ = 'player_season_stats'
    
    id = Column(Integer, primary_key=True)
    player_id = Column(Integer, ForeignKey('players.id'), nullable=False)
    team_id = Column(Integer, ForeignKey('teams.id'), nullable=False)
    season = Column(Integer, nullable=False)
    
    # General
    games_played = Column(Integer, default=0)
    games_started = Column(Integer, default=0)
    minutes_played = Column(Float)
    
    # Basketball stats
    points_per_game = Column(Float)
    rebounds_per_game = Column(Float)
    assists_per_game = Column(Float)
    steals_per_game = Column(Float)
    blocks_per_game = Column(Float)
    turnovers_per_game = Column(Float)
    fouls_per_game = Column(Float)
    field_goal_pct = Column(Float)
    three_point_pct = Column(Float)
    free_throw_pct = Column(Float)
    plus_minus_per_game = Column(Float)
    usage_rate = Column(Float)
    true_shooting_pct = Column(Float)
    player_efficiency_rating = Column(Float)
    win_shares = Column(Float)
    
    # Football stats
    passing_yards = Column(Integer)
    passing_touchdowns = Column(Integer)
    interceptions = Column(Integer)
    completion_pct = Column(Float)
    yards_per_attempt = Column(Float)
    qb_rating = Column(Float)
    rushing_yards = Column(Integer)
    rushing_yards_per_game = Column(Float)
    rushing_touchdowns = Column(Integer)
    receiving_yards = Column(Integer)
    receiving_yards_per_game = Column(Float)
    receiving_touchdowns = Column(Integer)
    receptions = Column(Integer)
    tackles = Column(Integer)
    sacks = Column(Float)
    interceptions_as_def = Column(Integer)
    
    # Injury status
    is_injured = Column(Boolean, default=False)
    games_missed = Column(Integer, default=0)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    __table_args__ = (
        UniqueConstraint('player_id', 'season', 'team_id', name='uq_player_season_team'),
        Index('ix_player_id', 'player_id'),
        Index('ix_team_id', 'team_id'),
        Index('ix_season', 'season'),
    )
    
    player = relationship('Player', back_populates='player_stats')
    team = relationship('Team', back_populates='player_stats')
    
    def __repr__(self):
        return f"<PlayerSeasonStats {self.player.first_name} {self.season}>"

class InjuryReport(Base):
    """Player injury information"""
    __tablename__ = 'injury_reports'
    
    id = Column(Integer, primary_key=True)
    team_id = Column(Integer, ForeignKey('teams.id'), nullable=False)
    player_id = Column(Integer, ForeignKey('players.id'), nullable=False)
    
    # Injury details
    injury_type = Column(String(100), nullable=False)  # ACL tear, Hamstring, etc.
    date_injured = Column(DateTime)
    severity = Column(String(20))  # mild, moderate, severe, out_for_season
    
    # Recovery
    estimated_return = Column(DateTime)
    actual_return = Column(DateTime)
    days_missed = Column(Integer)
    
    # Status
    status = Column(String(50))  # out, questionable, doubtful, probable, healthy
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    __table_args__ = (
        Index('ix_team_id', 'team_id'),
        Index('ix_player_id', 'player_id'),
        Index('ix_status', 'status'),
    )
    
    team = relationship('Team', back_populates='injury_reports')
    player = relationship('Player', back_populates='injuries')
    
    def __repr__(self):
        return f"<InjuryReport {self.player.first_name} - {self.injury_type}>"

# ============================================================================
# BETTING & ODDS MODELS (Multiple Sportsbooks)
# ============================================================================

class Sportsbook(Base):
    """Sportsbook/Betting platforms"""
    __tablename__ = 'sportsbooks'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True, nullable=False)  # DraftKings, FanDuel, etc.
    slug = Column(String(50), unique=True, nullable=False)
    logo_url = Column(String(255))
    is_active = Column(Boolean, default=True)
    api_available = Column(Boolean, default=False)
    
    __table_args__ = (
        Index('ix_name', 'name'),
    )
    
    odds_snapshots = relationship('OddsSnapshot', back_populates='sportsbook')
    
    def __repr__(self):
        return f"<Sportsbook {self.name}>"

class OddsSnapshot(Base):
    """Historical odds from sportsbooks"""
    __tablename__ = 'odds_snapshots'
    
    id = Column(Integer, primary_key=True)
    event_id = Column(Integer, ForeignKey('events.id'), nullable=False)
    sportsbook_id = Column(Integer, ForeignKey('sportsbooks.id'), nullable=False)
    
    # Market info
    market_type = Column(String(50), nullable=False)  # moneyline, spread, over_under, props
    market_key = Column(String(100))  # h2h, spreads, totals
    
    # Moneyline odds
    home_moneyline = Column(Float)
    away_moneyline = Column(Float)
    draw_moneyline = Column(Float)
    
    # Spread odds
    home_spread = Column(Float)
    home_spread_odds = Column(Float)
    away_spread = Column(Float)
    away_spread_odds = Column(Float)
    
    # Over/Under
    over_under_total = Column(Float)
    over_odds = Column(Float)
    under_odds = Column(Float)
    
    # Implied probabilities
    home_implied_prob = Column(Float)
    away_implied_prob = Column(Float)
    draw_implied_prob = Column(Float)
    
    # Props (flexible JSON for various props)
    prop_bets = Column(JSON)  # {player: {stat: odds, ...}, ...}
    
    # Metadata
    timestamp = Column(DateTime, default=datetime.utcnow)  # When fetched
    is_live = Column(Boolean, default=False)
    
    __table_args__ = (
        Index('ix_event_id', 'event_id'),
        Index('ix_sportsbook_id', 'sportsbook_id'),
        Index('ix_timestamp', 'timestamp'),
        Index('ix_market_type', 'market_type'),
    )
    
    event = relationship('Event', back_populates='odds_history')
    sportsbook = relationship('Sportsbook', back_populates='odds_snapshots')
    
    def __repr__(self):
        return f"<OddsSnapshot {self.event_id} - {self.sportsbook.name}>"

class OddMovement(Base):
    """Tracks odds line movement over time"""
    __tablename__ = 'odds_movements'
    
    id = Column(Integer, primary_key=True)
    event_id = Column(Integer, ForeignKey('events.id'), nullable=False)
    sportsbook_id = Column(Integer, ForeignKey('sportsbooks.id'), nullable=False)
    
    market_type = Column(String(50), nullable=False)
    
    # Opening odds
    opening_home_moneyline = Column(Float)
    opening_away_moneyline = Column(Float)
    opening_spread = Column(Float)
    opening_over_under = Column(Float)
    
    # Current odds
    current_home_moneyline = Column(Float)
    current_away_moneyline = Column(Float)
    current_spread = Column(Float)
    current_over_under = Column(Float)
    
    # Movement analysis
    moneyline_movement = Column(String(50))  # sharp_action_home, steam_move, etc.
    spread_movement = Column(Float)  # How much line moved
    total_movement = Column(Float)
    
    # Betting volume
    total_tickets_home = Column(Integer)
    total_tickets_away = Column(Integer)
    total_money_home = Column(Float)
    total_money_away = Column(Float)
    public_money_pct = Column(Float)
    sharp_money_pct = Column(Float)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    __table_args__ = (
        Index('ix_event_id', 'event_id'),
        Index('ix_sportsbook_id', 'sportsbook_id'),
    )
    
    def __repr__(self):
        return f"<OddMovement {self.event_id}>"

# ============================================================================
# PREDICTION & BETTING MODELS
# ============================================================================

class Prediction(Base):
    """AI model predictions"""
    __tablename__ = 'predictions'
    
    id = Column(Integer, primary_key=True)
    event_id = Column(Integer, ForeignKey('events.id'), nullable=False)
    model_name = Column(String(100), nullable=False)
    model_version = Column(String(20), nullable=False)
    
    # Prediction
    prediction_type = Column(String(50), nullable=False)  # moneyline, spread, over_under, player_prop
    prediction = Column(String(100), nullable=False)
    probability = Column(Float, nullable=False)
    confidence = Column(Float)
    
    # Model output
    raw_output = Column(JSON)  # All model probabilities/scores
    features_used = Column(JSON)  # Serialized features
    
    # Comparison with actual
    actual_outcome = Column(String(50))
    is_correct = Column(Boolean)
    
    # Betting metrics
    betting_recommendation = Column(String(50))  # PASS, STRONG_BUY, BUY, SELL, etc.
    implied_odds = Column(Float)
    edge_vs_best_market = Column(Float)  # Percentage edge
    expected_value = Column(Float)  # EV if -110 odds
    kelly_fraction = Column(Float)  # Kelly criterion
    
    # Variance
    confidence_interval_lower = Column(Float)
    confidence_interval_upper = Column(Float)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    __table_args__ = (
        Index('ix_event_id', 'event_id'),
        Index('ix_model_name', 'model_name'),
        Index('ix_created_at', 'created_at'),
        Index('ix_is_correct', 'is_correct'),
    )
    
    event = relationship('Event', back_populates='predictions')
    
    def __repr__(self):
        return f"<Prediction {self.event_id} {self.model_name}>"

class Bet(Base):
    """Individual bets placed"""
    __tablename__ = 'bets'
    
    id = Column(Integer, primary_key=True)
    portfolio_id = Column(Integer, ForeignKey('portfolios.id'), nullable=False)
    prediction_id = Column(Integer, ForeignKey('predictions.id'))
    event_id = Column(Integer, ForeignKey('events.id'), nullable=False)
    sportsbook_id = Column(Integer, ForeignKey('sportsbooks.id'))
    
    # Bet details
    bet_type = Column(String(50), nullable=False)  # moneyline, spread, parlay, teaser, etc.
    market_type = Column(String(50), nullable=False)
    prediction = Column(String(100), nullable=False)
    odds = Column(Float, nullable=False)  # Decimal odds
    stake = Column(Float, nullable=False)
    potential_return = Column(Float)
    
    # Status
    status = Column(String(20), default='pending')  # pending, won, lost, push, cancelled
    
    # Result
    result_amount = Column(Float)
    profit_loss = Column(Float)
    roi = Column(Float)
    
    # Analysis
    model_confidence = Column(Float)
    edge_pct = Column(Float)
    expected_value = Column(Float)
    
    # Tracking
    created_at = Column(DateTime, default=datetime.utcnow)
    settled_at = Column(DateTime)
    
    __table_args__ = (
        Index('ix_portfolio_id', 'portfolio_id'),
        Index('ix_event_id', 'event_id'),
        Index('ix_status', 'status'),
        Index('ix_created_at', 'created_at'),
    )
    
    portfolio = relationship('Portfolio', back_populates='bets')
    event = relationship('Event')
    prediction = relationship('Prediction')
    sportsbook = relationship('Sportsbook')
    
    def __repr__(self):
        return f"<Bet {self.prediction} @ {self.odds}>"

class Portfolio(Base):
    """User betting portfolios/accounts"""
    __tablename__ = 'portfolios'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    
    # Status
    is_active = Column(Boolean, default=True)
    strategy = Column(String(100))  # value_betting, arbitrage, etc.
    risk_tolerance = Column(String(20))  # low, medium, high
    
    # Bankroll
    starting_balance = Column(Float, nullable=False)
    current_balance = Column(Float, nullable=False)
    total_return = Column(Float)
    return_pct = Column(Float)
    
    # Performance
    total_bets = Column(Integer, default=0)
    winning_bets = Column(Integer, default=0)
    losing_bets = Column(Integer, default=0)
    push_bets = Column(Integer, default=0)
    win_rate = Column(Float)
    roi = Column(Float)
    
    # Risk metrics
    max_drawdown = Column(Float)
    max_drawdown_pct = Column(Float)
    avg_bet_size = Column(Float)
    largest_win = Column(Float)
    largest_loss = Column(Float)
    
    # Consistency
    profit_factor = Column(Float)  # Total wins / Total losses
    sharpe_ratio = Column(Float)
    sortino_ratio = Column(Float)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    __table_args__ = (
        Index('ix_user_id', 'user_id'),
        Index('ix_is_active', 'is_active'),
    )
    
    user = relationship('User', back_populates='portfolios')
    bets = relationship('Bet', back_populates='portfolio')
    
    def __repr__(self):
        return f"<Portfolio {self.name}>"

# ============================================================================
# USER & AUTHENTICATION MODELS
# ============================================================================

class User(Base):
    """Users of the system"""
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    username = Column(String(100), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    
    # Profile
    first_name = Column(String(50))
    last_name = Column(String(50))
    avatar_url = Column(String(255))
    bio = Column(Text)
    
    # Preferences
    preferred_sports = Column(JSON)  # ["NFL", "NBA"]
    preferred_leagues = Column(JSON)
    preferred_sportsbooks = Column(JSON)
    
    # Settings
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    is_verified = Column(Boolean, default=False)
    notifications_enabled = Column(Boolean, default=True)
    email_notifications = Column(Boolean, default=True)
    
    # Account
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = Column(DateTime)
    
    __table_args__ = (
        Index('ix_username', 'username'),
        Index('ix_email', 'email'),
    )
    
    portfolios = relationship('Portfolio', back_populates='user')
    
    def __repr__(self):
        return f"<User {self.username}>"

# ============================================================================
# MODEL PERFORMANCE & TRAINING MODELS
# ============================================================================

class ModelMetrics(Base):
    """Performance metrics for trained models"""
    __tablename__ = 'model_metrics'
    
    id = Column(Integer, primary_key=True)
    model_name = Column(String(100), nullable=False)
    model_version = Column(String(20), nullable=False)
    training_date = Column(DateTime, nullable=False)
    
    # Classification metrics
    accuracy = Column(Float)
    precision = Column(Float)
    recall = Column(Float)
    f1_score = Column(Float)
    auc_roc = Column(Float)
    logloss = Column(Float)
    
    # Per-class metrics
    home_win_precision = Column(Float)
    away_win_precision = Column(Float)
    draw_precision = Column(Float)
    
    # Betting metrics
    win_rate = Column(Float)
    roi = Column(Float)
    profit_factor = Column(Float)
    sharpe_ratio = Column(Float)
    
    # Dataset
    training_samples = Column(Integer)
    validation_samples = Column(Integer)
    test_samples = Column(Integer)
    training_start_date = Column(DateTime)
    training_end_date = Column(DateTime)
    
    # Features
    feature_count = Column(Integer)
    top_features = Column(JSON)  # {"feature": score, ...}
    
    # Hyperparameters
    hyperparameters = Column(JSON)
    
    # Cross validation
    cv_scores = Column(JSON)  # Cross validation results
    cv_mean = Column(Float)
    cv_std = Column(Float)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        Index('ix_model_name', 'model_name'),
        Index('ix_training_date', 'training_date'),
    )
    
    def __repr__(self):
        return f"<ModelMetrics {self.model_name} v{self.model_version}>"

class TrainingData(Base):
    """Historical data used for model training"""
    __tablename__ = 'training_data'
    
    id = Column(Integer, primary_key=True)
    event_id = Column(Integer, ForeignKey('events.id'), nullable=False)
    
    # Features
    features = Column(JSON, nullable=False)  # All input features
    label = Column(String(50), nullable=False)  # Target (home_win, away_win, draw)
    
    # Metadata
    feature_version = Column(String(20))
    data_split = Column(String(20))  # train, val, test
    model_name = Column(String(100))
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        Index('ix_event_id', 'event_id'),
        Index('ix_data_split', 'data_split'),
        Index('ix_model_name', 'model_name'),
    )
    
    def __repr__(self):
        return f"<TrainingData {self.event_id}>"

class FeatureCalculation(Base):
    """Cache of calculated features for events"""
    __tablename__ = 'feature_calculations'
    
    id = Column(Integer, primary_key=True)
    event_id = Column(Integer, ForeignKey('events.id'), nullable=False)
    
    # Technical indicators
    home_team_rsi = Column(Float)
    away_team_rsi = Column(Float)
    home_team_macd = Column(Float)
    away_team_macd = Column(Float)
    
    # Form/Momentum
    home_win_streak = Column(Integer)
    away_win_streak = Column(Integer)
    home_form_score = Column(Float)  # Last 10 games performance
    away_form_score = Column(Float)
    
    # Head to head
    head_to_head_record = Column(String(20))  # H2H wins
    home_team_h2h_record = Column(String(20))
    away_team_h2h_record = Column(String(20))
    home_team_avg_vs_opponent = Column(Float)
    
    # Home/Away advantage
    home_field_advantage = Column(Float)
    venue_stats = Column(JSON)  # Historical stats at venue
    
    # Rest/Travel
    home_days_rest = Column(Integer)
    away_days_rest = Column(Integer)
    is_back_to_back = Column(Boolean)
    back_to_back_positions = Column(String(50))  # 1st, 2nd of b2b
    
    # Injuries impact
    home_missing_key_players = Column(JSON)  # Injured players
    away_missing_key_players = Column(JSON)
    home_injury_impact_score = Column(Float)
    away_injury_impact_score = Column(Float)
    
    # Seasonal stats
    home_sos = Column(Float)  # Strength of schedule
    away_sos = Column(Float)
    home_year_to_date_stats = Column(JSON)
    away_year_to_date_stats = Column(JSON)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        UniqueConstraint('event_id', name='uq_event_features'),
    )
    
    def __repr__(self):
        return f"<FeatureCalculation {self.event_id}>"

class PredictionMarketData(Base):
    """Prediction market data (e.g., Polymarket, Manifold)"""
    __tablename__ = 'prediction_market_data'
    
    id = Column(Integer, primary_key=True)
    event_id = Column(Integer, ForeignKey('events.id'), nullable=False)
    market_name = Column(String(255), nullable=False)  # Market description
    market_source = Column(String(50), nullable=False)  # Polymarket, Manifold, etc.
    external_market_id = Column(String(100))
    
    # Market data
    yes_probability = Column(Float)  # Probability of outcome
    no_probability = Column(Float)
    yes_shares_price = Column(Float)
    no_shares_price = Column(Float)
    total_volume = Column(Float)
    
    # Liquidity
    liquidity = Column(Float)
    tvl = Column(Float)  # Total value locked
    
    # Tracking
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        Index('ix_event_id', 'event_id'),
        Index('ix_market_source', 'market_source'),
        Index('ix_timestamp', 'timestamp'),
    )
    
    def __repr__(self):
        return f"<PredictionMarketData {self.market_name}>"

# ============================================================================
# ARBITRAGE & COMPARISON MODELS
# ============================================================================

class ArbitrageOpportunity(Base):
    """Identifies arbitrage opportunities across sportsbooks"""
    __tablename__ = 'arbitrage_opportunities'
    
    id = Column(Integer, primary_key=True)
    event_id = Column(Integer, ForeignKey('events.id'), nullable=False)
    
    # Opportunity details
    opportunity_type = Column(String(50), nullable=False)  # two_way, three_way, etc.
    market_type = Column(String(50), nullable=False)  # moneyline, spread, etc.
    
    # Sportsbooks involved
    sportsbook_1 = Column(String(100), nullable=False)
    sportsbook_2 = Column(String(100), nullable=False)
    sportsbook_3 = Column(String(100))
    
    # Odds
    sportsbook_1_odds = Column(Float)
    sportsbook_2_odds = Column(Float)
    sportsbook_3_odds = Column(Float)
    sportsbook_1_side = Column(String(100))
    sportsbook_2_side = Column(String(100))
    sportsbook_3_side = Column(String(100))
    
    # Arbitrage calculation
    arb_percentage = Column(Float)  # Profit margin
    implied_return = Column(Float)  # Expected return
    stake_allocation = Column(JSON)  # How to distribute bet
    
    # Tracking
    is_active = Column(Boolean, default=True)
    was_exploited = Column(Boolean, default=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        Index('ix_event_id', 'event_id'),
        Index('ix_is_active', 'is_active'),
    )
    
    def __repr__(self):
        return f"<ArbitrageOpportunity {self.arb_percentage}%>"

class OddsComparison(Base):
    """Compares odds across sportsbooks for best value"""
    __tablename__ = 'odds_comparisons'
    
    id = Column(Integer, primary_key=True)
    event_id = Column(Integer, ForeignKey('events.id'), nullable=False)
    
    # Market details
    market_type = Column(String(50), nullable=False)
    prediction = Column(String(100), nullable=False)
    
    # Best odds tracking
    best_odds = Column(Float)
    best_sportsbook = Column(String(100))
    worst_odds = Column(Float)
    worst_sportsbook = Column(String(100))
    odds_differential = Column(Float)
    
    # Average market odds
    average_odds = Column(Float)
    median_odds = Column(Float)
    stddev_odds = Column(Float)
    
    # Comparison data
    all_odds = Column(JSON)  # {sportsbook: odds}
    
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        Index('ix_event_id', 'event_id'),
        Index('ix_timestamp', 'timestamp'),
    )
    
    def __repr__(self):
        return f"<OddsComparison {self.prediction}>"
