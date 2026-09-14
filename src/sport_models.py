"""Sport-specific database models for detailed analytics"""
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, ForeignKey, JSON, Text, UniqueConstraint, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

# ============================================================================
# NFL SPECIFIC MODELS
# ============================================================================

class NFLGameStats(Base):
    """Detailed NFL game statistics"""
    __tablename__ = 'nfl_game_stats'
    
    id = Column(Integer, primary_key=True)
    event_id = Column(Integer, ForeignKey('events.id'), nullable=False)
    team_id = Column(Integer, ForeignKey('teams.id'), nullable=False)
    
    # Offensive stats
    total_yards = Column(Integer)
    passing_yards = Column(Integer)
    rushing_yards = Column(Integer)
    passing_touchdowns = Column(Integer)
    rushing_touchdowns = Column(Integer)
    interceptions = Column(Integer)
    fumbles = Column(Integer)
    fumbles_lost = Column(Integer)
    
    # Defensive stats
    tackles = Column(Integer)
    sacks = Column(Float)
    interceptions_defense = Column(Integer)
    forced_fumbles = Column(Integer)
    defensive_touchdowns = Column(Integer)
    passes_defended = Column(Integer)
    
    # Red zone performance
    red_zone_attempts = Column(Integer)
    red_zone_conversions = Column(Integer)
    red_zone_conversion_pct = Column(Float)
    
    # Third down
    third_down_attempts = Column(Integer)
    third_down_conversions = Column(Integer)
    third_down_conversion_pct = Column(Float)
    
    # Penalties
    total_penalties = Column(Integer)
    total_penalty_yards = Column(Integer)
    
    # Play by play data
    play_by_play = Column(JSON)  # Detailed play data
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        Index('ix_event_id', 'event_id'),
        Index('ix_team_id', 'team_id'),
    )

class NFLPlayerStats(Base):
    """NFL-specific player stats"""
    __tablename__ = 'nfl_player_stats'
    
    id = Column(Integer, primary_key=True)
    player_id = Column(Integer, ForeignKey('players.id'), nullable=False)
    season = Column(Integer, nullable=False)
    
    # QB specific
    pass_attempts = Column(Integer)
    pass_completions = Column(Integer)
    completion_pct = Column(Float)
    passing_yards_season = Column(Integer)
    passing_tds_season = Column(Integer)
    interceptions_thrown = Column(Integer)
    qb_rating = Column(Float)
    yards_per_attempt = Column(Float)
    
    # RB/WR specific
    rushing_attempts = Column(Integer)
    rushing_yards_season = Column(Integer)
    rushing_tds = Column(Integer)
    receiving_receptions = Column(Integer)
    receiving_yards_season = Column(Integer)
    receiving_tds = Column(Integer)
    yards_after_catch = Column(Float)
    
    # Defense specific
    tackles_season = Column(Integer)
    sacks_season = Column(Float)
    interceptions_season = Column(Integer)
    forced_fumbles_season = Column(Integer)
    passes_defended_season = Column(Integer)
    
    # Injury games missed
    games_missed = Column(Integer, default=0)
    
    __table_args__ = (
        UniqueConstraint('player_id', 'season', name='uq_nfl_player_season'),
    )

class NFLInjuryReport(Base):
    """NFL-specific injury report with practice participation"""
    __tablename__ = 'nfl_injury_reports'
    
    id = Column(Integer, primary_key=True)
    player_id = Column(Integer, ForeignKey('players.id'), nullable=False)
    team_id = Column(Integer, ForeignKey('teams.id'), nullable=False)
    week = Column(Integer)
    
    # Injury details
    injury = Column(String(100), nullable=False)
    practice_participation = Column(String(50))  # Out, Limited, Full
    injury_status = Column(String(50))  # Out, Questionable, Doubtful, Probable, Healthy
    
    # Dates
    date_reported = Column(DateTime)
    estimated_return = Column(DateTime)
    
    created_at = Column(DateTime, default=datetime.utcnow)

# ============================================================================
# NBA SPECIFIC MODELS
# ============================================================================

class NBAGameStats(Base):
    """Detailed NBA game statistics"""
    __tablename__ = 'nba_game_stats'
    
    id = Column(Integer, primary_key=True)
    event_id = Column(Integer, ForeignKey('events.id'), nullable=False)
    team_id = Column(Integer, ForeignKey('teams.id'), nullable=False)
    
    # Shooting
    field_goals_made = Column(Integer)
    field_goals_attempted = Column(Integer)
    fg_pct = Column(Float)
    three_pointers_made = Column(Integer)
    three_pointers_attempted = Column(Integer)
    three_pct = Column(Float)
    free_throws_made = Column(Integer)
    free_throws_attempted = Column(Integer)
    ft_pct = Column(Float)
    
    # Rebounding
    offensive_rebounds = Column(Integer)
    defensive_rebounds = Column(Integer)
    total_rebounds = Column(Integer)
    
    # Playmaking
    assists = Column(Integer)
    turnovers = Column(Integer)
    assist_turnover_ratio = Column(Float)
    
    # Defense
    steals = Column(Integer)
    blocks = Column(Integer)
    fouls = Column(Integer)
    
    # Pace & efficiency
    pace = Column(Float)  # Possessions per 48 min
    offensive_rating = Column(Float)
    defensive_rating = Column(Float)
    net_rating = Column(Float)
    
    # Bench vs starters
    bench_points = Column(Integer)
    starter_minutes = Column(Float)
    
    # Clutch time (last 5 min, ≤5 point diff)
    clutch_fg_pct = Column(Float)
    clutch_three_pct = Column(Float)
    
    play_by_play = Column(JSON)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        Index('ix_event_id', 'event_id'),
    )

class NBAPlayerStats(Base):
    """NBA-specific player season stats"""
    __tablename__ = 'nba_player_stats'
    
    id = Column(Integer, primary_key=True)
    player_id = Column(Integer, ForeignKey('players.id'), nullable=False)
    season = Column(Integer, nullable=False)
    
    # Per game averages
    ppg = Column(Float)  # Points per game
    rpg = Column(Float)  # Rebounds per game
    apg = Column(Float)  # Assists per game
    spg = Column(Float)  # Steals per game
    bpg = Column(Float)  # Blocks per game
    tov_pg = Column(Float)  # Turnovers per game
    
    # Shooting percentages
    fg_pct = Column(Float)
    three_pct = Column(Float)
    ft_pct = Column(Float)
    ts_pct = Column(Float)  # True shooting %
    efg_pct = Column(Float)  # Effective FG %
    
    # Advanced
    per = Column(Float)  # Player Efficiency Rating
    win_shares = Column(Float)
    vorp = Column(Float)  # Value Over Replacement Player
    usage_pct = Column(Float)
    ast_ratio = Column(Float)  # Assist ratio
    
    # Plus/Minus
    plus_minus = Column(Float)
    plus_minus_per_100 = Column(Float)
    
    # Durability
    games_played = Column(Integer)
    games_started = Column(Integer)
    minutes_per_game = Column(Float)
    
    __table_args__ = (
        UniqueConstraint('player_id', 'season', name='uq_nba_player_season'),
    )

class NBAClutchPerformance(Base):
    """NBA clutch time performance (last 5 min, ≤5 point diff)"""
    __tablename__ = 'nba_clutch_performance'
    
    id = Column(Integer, primary_key=True)
    player_id = Column(Integer, ForeignKey('players.id'), nullable=False)
    season = Column(Integer, nullable=False)
    
    clutch_games = Column(Integer)
    clutch_minutes = Column(Float)
    clutch_ppg = Column(Float)
    clutch_fg_pct = Column(Float)
    clutch_three_pct = Column(Float)
    clutch_ft_pct = Column(Float)
    clutch_plus_minus = Column(Float)

# ============================================================================
# SOCCER/FOOTBALL SPECIFIC MODELS
# ============================================================================

class SoccerGameStats(Base):
    """Detailed soccer game statistics"""
    __tablename__ = 'soccer_game_stats'
    
    id = Column(Integer, primary_key=True)
    event_id = Column(Integer, ForeignKey('events.id'), nullable=False)
    team_id = Column(Integer, ForeignKey('teams.id'), nullable=False)
    
    # Possession
    possession_pct = Column(Float)
    passes = Column(Integer)
    pass_completion_pct = Column(Float)
    
    # Shooting
    shots = Column(Integer)
    shots_on_target = Column(Integer)
    shots_on_target_pct = Column(Float)
    goals = Column(Integer)
    
    # Expected goals (quality of chances)
    expected_goals = Column(Float)  # xG
    expected_assists = Column(Float)  # xA
    expected_goals_against = Column(Float)  # xGA
    
    # Passing types
    short_passes = Column(Integer)
    long_passes = Column(Integer)
    through_balls = Column(Integer)
    cross_passes = Column(Integer)
    
    # Defense
    tackles = Column(Integer)
    tackles_won_pct = Column(Float)
    interceptions = Column(Integer)
    clearances = Column(Integer)
    blocks = Column(Integer)
    fouls = Column(Integer)
    
    # Set pieces
    corners = Column(Integer)
    offside = Column(Integer)
    
    # Formation
    formation = Column(String(20))  # 4-3-3, 5-2-3, etc.
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        Index('ix_event_id', 'event_id'),
    )

class SoccerPlayerStats(Base):
    """Soccer-specific player season stats"""
    __tablename__ = 'soccer_player_stats'
    
    id = Column(Integer, primary_key=True)
    player_id = Column(Integer, ForeignKey('players.id'), nullable=False)
    season = Column(Integer, nullable=False)
    
    # Shooting & Scoring
    goals = Column(Integer)
    assists = Column(Integer)
    goal_contributions = Column(Integer)  # Goals + Assists
    
    # Expected stats
    expected_goals = Column(Float)
    expected_assists = Column(Float)
    
    # Possession
    passes_per_game = Column(Float)
    pass_completion_pct = Column(Float)
    
    # Playmaking
    chances_created = Column(Integer)
    key_passes = Column(Integer)
    
    # Defense (for defenders)
    tackles_per_game = Column(Float)
    interceptions_per_game = Column(Float)
    clearances_per_game = Column(Float)
    
    # Discipline
    yellow_cards = Column(Integer)
    red_cards = Column(Integer)
    
    # Durability
    games_played = Column(Integer)
    minutes_played = Column(Integer)
    
    # Position
    position = Column(String(50))  # GK, DEF, MID, FWD
    
    __table_args__ = (
        UniqueConstraint('player_id', 'season', name='uq_soccer_player_season'),
    )

# ============================================================================
# BASEBALL SPECIFIC MODELS
# ============================================================================

class BaseballGameStats(Base):
    """Detailed baseball game statistics"""
    __tablename__ = 'baseball_game_stats'
    
    id = Column(Integer, primary_key=True)
    event_id = Column(Integer, ForeignKey('events.id'), nullable=False)
    team_id = Column(Integer, ForeignKey('teams.id'), nullable=False)
    
    # Hitting
    hits = Column(Integer)
    at_bats = Column(Integer)
    batting_average = Column(Float)
    runs = Column(Integer)
    rbis = Column(Integer)  # Runs batted in
    
    # Power
    home_runs = Column(Integer)
    doubles = Column(Integer)
    triples = Column(Integer)
    slugging_pct = Column(Float)
    
    # Discipline
    walks = Column(Integer)
    strikeouts = Column(Integer)
    on_base_pct = Column(Float)
    
    # Pitching
    innings_pitched = Column(Float)
    earned_runs = Column(Integer)
    era = Column(Float)  # Earned run average
    strikeouts_pitched = Column(Integer)
    walks_pitched = Column(Integer)
    
    # Defense
    errors = Column(Integer)
    fielding_pct = Column(Float)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        Index('ix_event_id', 'event_id'),
    )

class BaseballPlayerStats(Base):
    """Baseball-specific player season stats"""
    __tablename__ = 'baseball_player_stats'
    
    id = Column(Integer, primary_key=True)
    player_id = Column(Integer, ForeignKey('players.id'), nullable=False)
    season = Column(Integer, nullable=False)
    
    # Batting stats
    games = Column(Integer)
    at_bats = Column(Integer)
    hits = Column(Integer)
    doubles = Column(Integer)
    triples = Column(Integer)
    home_runs = Column(Integer)
    rbis = Column(Integer)
    runs = Column(Integer)
    
    # Batting averages
    batting_average = Column(Float)
    on_base_pct = Column(Float)
    slugging_pct = Column(Float)
    ops = Column(Float)  # On-base plus slugging
    
    # Advanced batting
    war = Column(Float)  # Wins above replacement
    wrc_plus = Column(Float)  # Weighted runs created plus
    
    # Discipline
    walks = Column(Integer)
    strikeouts = Column(Integer)
    strikeout_pct = Column(Float)
    
    # Pitching stats (if pitcher)
    innings_pitched = Column(Float)
    earned_run_average = Column(Float)
    wins = Column(Integer)
    losses = Column(Integer)
    saves = Column(Integer)
    strikeouts_pitched = Column(Integer)
    walks_pitched = Column(Integer)
    
    # Durability
    games_played = Column(Integer)
    
    __table_args__ = (
        UniqueConstraint('player_id', 'season', name='uq_baseball_player_season'),
    )

# ============================================================================
# GENERAL SPORT-SPECIFIC PERFORMANCE METRICS
# ============================================================================

class SportSpecificMetrics(Base):
    """General container for sport-specific analytical metrics"""
    __tablename__ = 'sport_specific_metrics'
    
    id = Column(Integer, primary_key=True)
    event_id = Column(Integer, ForeignKey('events.id'), nullable=False)
    team_id = Column(Integer, ForeignKey('teams.id'), nullable=False)
    sport_id = Column(Integer, ForeignKey('sports.id'), nullable=False)
    
    # Generic metrics (all sports)
    tempo = Column(Float)  # Game pace
    efficiency = Column(Float)  # Overall efficiency
    dominance_score = Column(Float)  # How dominant was the team?
    
    # Sport-agnostic advantage metrics
    home_field_advantage = Column(Float)
    momentum_index = Column(Float)  # Current form
    
    # Predictive metrics
    win_probability = Column(Float)  # Predicted chance to win
    expected_score_diff = Column(Float)
    
    # Variance metrics
    performance_consistency = Column(Float)  # Std dev of recent performance
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    __table_args__ = (
        Index('ix_event_id', 'event_id'),
        Index('ix_sport_id', 'sport_id'),
    )
