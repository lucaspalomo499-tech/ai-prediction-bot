"""Database initialization script - Creates all tables and seeds initial data"""
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from config import config
from src.models import Base, Sport, League, Sportsbook, User
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatabaseInitializer:
    """Initialize and seed the database"""
    
    def __init__(self, database_url=None):
        """
        Initialize database connection
        
        Args:
            database_url: Connection string (uses config if not provided)
        """
        if database_url is None:
            env = os.getenv('FLASK_ENV', 'development')
            config_obj = config[env]
            database_url = config_obj.DATABASE_URL
        
        self.engine = create_engine(database_url, echo=False)
        self.Session = sessionmaker(bind=self.engine)
    
    def create_all_tables(self):
        """Create all tables in the database"""
        logger.info("Creating all database tables...")
        try:
            Base.metadata.create_all(self.engine)
            logger.info("✓ All tables created successfully")
            return True
        except Exception as e:
            logger.error(f"✗ Error creating tables: {e}")
            return False
    
    def drop_all_tables(self):
        """Drop all tables (WARNING: Destructive!)"""
        logger.warning("WARNING: Dropping all tables!")
        try:
            Base.metadata.drop_all(self.engine)
            logger.info("✓ All tables dropped")
            return True
        except Exception as e:
            logger.error(f"✗ Error dropping tables: {e}")
            return False
    
    def seed_sports(self):
        """Seed initial sports data"""
        session = self.Session()
        try:
            logger.info("Seeding sports...")
            
            sports_data = [
                {'name': 'NFL', 'slug': 'nfl', 'description': 'National Football League'},
                {'name': 'NBA', 'slug': 'nba', 'description': 'National Basketball Association'},
                {'name': 'MLB', 'slug': 'mlb', 'description': 'Major League Baseball'},
                {'name': 'NHL', 'slug': 'nhl', 'description': 'National Hockey League'},
                {'name': 'Soccer', 'slug': 'soccer', 'description': 'Association Football'},
                {'name': 'MLS', 'slug': 'mls', 'description': 'Major League Soccer'},
                {'name': 'NCAA Basketball', 'slug': 'ncaab', 'description': 'NCAA Division I Basketball'},
                {'name': 'NCAA Football', 'slug': 'ncaaf', 'description': 'NCAA Division I Football'},
                {'name': 'Tennis', 'slug': 'tennis', 'description': 'Professional Tennis'},
                {'name': 'Golf', 'slug': 'golf', 'description': 'Professional Golf'},
            ]
            
            for sport_data in sports_data:
                existing = session.query(Sport).filter_by(slug=sport_data['slug']).first()
                if not existing:
                    sport = Sport(**sport_data)
                    session.add(sport)
                    logger.info(f"  + Added {sport_data['name']}")
            
            session.commit()
            logger.info("✓ Sports seeded successfully")
            return True
        except Exception as e:
            session.rollback()
            logger.error(f"✗ Error seeding sports: {e}")
            return False
        finally:
            session.close()
    
    def seed_sportsbooks(self):
        """Seed initial sportsbook data"""
        session = self.Session()
        try:
            logger.info("Seeding sportsbooks...")
            
            sportsbooks_data = [
                {'name': 'DraftKings', 'slug': 'draftkings', 'api_available': True},
                {'name': 'FanDuel', 'slug': 'fanduel', 'api_available': True},
                {'name': 'BetMGM', 'slug': 'betmgm', 'api_available': True},
                {'name': 'Caesars', 'slug': 'caesars', 'api_available': True},
                {'name': 'BetRivers', 'slug': 'betrivers', 'api_available': False},
                {'name': 'WynnBET', 'slug': 'wynnbet', 'api_available': False},
                {'name': 'PointsBet', 'slug': 'pointsbet', 'api_available': True},
                {'name': 'Bovada', 'slug': 'bovada', 'api_available': False},
                {'name': 'BetUS', 'slug': 'betus', 'api_available': False},
                {'name': 'MyBookie', 'slug': 'mybookie', 'api_available': False},
            ]
            
            for book_data in sportsbooks_data:
                existing = session.query(Sportsbook).filter_by(slug=book_data['slug']).first()
                if not existing:
                    sportsbook = Sportsbook(**book_data)
                    session.add(sportsbook)
                    logger.info(f"  + Added {book_data['name']}")
            
            session.commit()
            logger.info("✓ Sportsbooks seeded successfully")
            return True
        except Exception as e:
            session.rollback()
            logger.error(f"✗ Error seeding sportsbooks: {e}")
            return False
        finally:
            session.close()
    
    def seed_leagues(self):
        """Seed initial league data"""
        session = self.Session()
        try:
            logger.info("Seeding leagues...")
            
            nfl_sport = session.query(Sport).filter_by(slug='nfl').first()
            nba_sport = session.query(Sport).filter_by(slug='nba').first()
            mlb_sport = session.query(Sport).filter_by(slug='mlb').first()
            soccer_sport = session.query(Sport).filter_by(slug='soccer').first()
            mls_sport = session.query(Sport).filter_by(slug='mls').first()
            
            leagues_data = [
                # NFL
                {'sport_id': nfl_sport.id if nfl_sport else None, 'name': 'NFL', 'slug': 'nfl', 'country': 'USA', 'season': 2024},
                
                # NBA
                {'sport_id': nba_sport.id if nba_sport else None, 'name': 'NBA', 'slug': 'nba', 'country': 'USA', 'season': 2024},
                
                # MLB
                {'sport_id': mlb_sport.id if mlb_sport else None, 'name': 'MLB', 'slug': 'mlb', 'country': 'USA', 'season': 2024},
                
                # Soccer
                {'sport_id': soccer_sport.id if soccer_sport else None, 'name': 'Premier League', 'slug': 'epl', 'country': 'England', 'season': 2024},
                {'sport_id': soccer_sport.id if soccer_sport else None, 'name': 'La Liga', 'slug': 'la-liga', 'country': 'Spain', 'season': 2024},
                {'sport_id': soccer_sport.id if soccer_sport else None, 'name': 'Serie A', 'slug': 'serie-a', 'country': 'Italy', 'season': 2024},
                {'sport_id': soccer_sport.id if soccer_sport else None, 'name': 'Bundesliga', 'slug': 'bundesliga', 'country': 'Germany', 'season': 2024},
                {'sport_id': soccer_sport.id if soccer_sport else None, 'name': 'Ligue 1', 'slug': 'ligue-1', 'country': 'France', 'season': 2024},
                
                # MLS
                {'sport_id': mls_sport.id if mls_sport else None, 'name': 'MLS', 'slug': 'mls', 'country': 'USA', 'season': 2024},
            ]
            
            for league_data in leagues_data:
                if league_data['sport_id']:
                    existing = session.query(League).filter_by(
                        sport_id=league_data['sport_id'],
                        slug=league_data['slug']
                    ).first()
                    if not existing:
                        league = League(**league_data)
                        session.add(league)
                        logger.info(f"  + Added {league_data['name']}")
            
            session.commit()
            logger.info("✓ Leagues seeded successfully")
            return True
        except Exception as e:
            session.rollback()
            logger.error(f"✗ Error seeding leagues: {e}")
            return False
        finally:
            session.close()
    
    def initialize(self, drop_existing=False):
        """
        Full database initialization
        
        Args:
            drop_existing: If True, drops all existing tables first
        """
        logger.info("=" * 60)
        logger.info("DATABASE INITIALIZATION")
        logger.info("=" * 60)
        
        if drop_existing:
            logger.warning("DESTRUCTIVE MODE: Dropping existing tables...")
            if not self.drop_all_tables():
                return False
        
        # Create tables
        if not self.create_all_tables():
            return False
        
        # Seed data
        if not self.seed_sports():
            return False
        
        if not self.seed_sportsbooks():
            return False
        
        if not self.seed_leagues():
            return False
        
        logger.info("=" * 60)
        logger.info("✓ DATABASE INITIALIZATION COMPLETE")
        logger.info("=" * 60)
        return True

if __name__ == '__main__':
    import sys
    
    # Check for --drop flag
    drop_existing = '--drop' in sys.argv
    
    initializer = DatabaseInitializer()
    success = initializer.initialize(drop_existing=drop_existing)
    
    sys.exit(0 if success else 1)
