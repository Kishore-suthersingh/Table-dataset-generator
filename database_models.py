"""
Database models for Antigravity table generation system.
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from config import DatabaseConfig

Base = declarative_base()

class TrafficLog(Base):
    """Traffic log table for storing HTTP request data."""
    __tablename__ = 'traffic_logs'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime, nullable=False, default=datetime.utcnow)
    ip_address = Column(String(45), nullable=False)  # IPv6 max length
    user_id = Column(Integer, nullable=True)
    endpoint = Column(String(255), nullable=False)
    method = Column(String(10), nullable=False)
    status_code = Column(Integer, nullable=False)
    latency_ms = Column(Float, nullable=False)
    user_agent = Column(String(255), nullable=True)
    geo_location = Column(String(10), nullable=True)
    
    def to_dict(self):
        """Convert to dictionary."""
        return {
            'id': self.id,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'ip_address': self.ip_address,
            'user_id': self.user_id,
            'endpoint': self.endpoint,
            'method': self.method,
            'status_code': self.status_code,
            'latency_ms': self.latency_ms,
            'user_agent': self.user_agent,
            'geo_location': self.geo_location,
        }
    
    def __repr__(self):
        return f"<TrafficLog(id={self.id}, timestamp={self.timestamp}, endpoint={self.endpoint})>"


class User(Base):
    """User table for referential integrity."""
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), nullable=False, unique=True)
    email = Column(String(100), nullable=False, unique=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<User(id={self.id}, username={self.username})>"


# Database initialization
db_config = DatabaseConfig()
engine = create_engine(db_config.url, echo=db_config.echo)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_database():
    """Initialize the database and create tables."""
    Base.metadata.create_all(bind=engine)
    print("Database initialized successfully")

def get_db():
    """Get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
