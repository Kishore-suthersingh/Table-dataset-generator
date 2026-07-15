"""
Premier League database models.
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, create_engine, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime

Base = declarative_base()

class PLTeam(Base):
    """Premier League team."""
    __tablename__ = 'pl_teams'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False, unique=True)
    short_name = Column(String(10), nullable=False)
    stadium = Column(String(100))
    city = Column(String(50))
    
    def __repr__(self):
        return f"<PLTeam(id={self.id}, name={self.name})>"


class PLMatch(Base):
    """Premier League match result."""
    __tablename__ = 'pl_matches'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    match_date = Column(DateTime, nullable=False)
    home_team_id = Column(Integer, ForeignKey('pl_teams.id'), nullable=False)
    away_team_id = Column(Integer, ForeignKey('pl_teams.id'), nullable=False)
    home_score = Column(Integer, nullable=False)
    away_score = Column(Integer, nullable=False)
    attendance = Column(Integer)
    season = Column(String(10), default="2024-25")
    
    # Relationships
    home_team = relationship("PLTeam", foreign_keys=[home_team_id])
    away_team = relationship("PLTeam", foreign_keys=[away_team_id])
    
    def __repr__(self):
        return f"<PLMatch({self.home_team_id} vs {self.away_team_id}: {self.home_score}-{self.away_score})>"


class PLTableEntry(Base):
    """Premier League table standings entry."""
    __tablename__ = 'pl_table'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    team_id = Column(Integer, ForeignKey('pl_teams.id'), nullable=False)
    season = Column(String(10), default="2024-25")
    position = Column(Integer, nullable=False)
    played = Column(Integer, default=0)
    won = Column(Integer, default=0)
    drawn = Column(Integer, default=0)
    lost = Column(Integer, default=0)
    goals_for = Column(Integer, default=0)
    goals_against = Column(Integer, default=0)
    goal_difference = Column(Integer, default=0)
    points = Column(Integer, default=0)
    form = Column(String(10))  # Last 5 results: W, D, L
    updated_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship
    team = relationship("PLTeam")
    
    def __repr__(self):
        return f"<PLTableEntry(pos={self.position}, team={self.team_id}, points={self.points})>"


# Database setup
engine = create_engine("sqlite:///premier_league.db", echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_pl_database():
    """Initialize Premier League database."""
    Base.metadata.create_all(bind=engine)
    print("Premier League database initialized")

def get_pl_db():
    """Get Premier League database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
