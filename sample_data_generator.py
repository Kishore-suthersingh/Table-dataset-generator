"""
Bootstrap script to populate database with realistic baseline data for testing.
"""
from database_models import init_database, SessionLocal, TrafficLog, User
from datetime import datetime, timedelta
import random
from config import (
    SAMPLE_ENDPOINTS, SAMPLE_USER_AGENTS, SAMPLE_GEO_LOCATIONS,
    HTTP_METHODS, STATUS_CODES
)
from utils import generate_ip_address, weighted_choice, generate_latency


def create_sample_users(db, count: int = 50):
    """Create sample users for referential integrity."""
    print(f"Creating {count} sample users...")
    
    for i in range(count):
        user = User(
            username=f"user_{1000 + i}",
            email=f"user{1000 + i}@example.com",
            created_at=datetime.utcnow() - timedelta(days=random.randint(1, 365))
        )
        db.add(user)
    
    db.commit()
    print(f"Created {count} users")


def create_sample_traffic_logs(db, count: int = 1000, hours_back: int = 24):
    """Create sample traffic logs with realistic patterns."""
    print(f"Creating {count} sample traffic logs...")
    
    # Get user IDs
    users = db.query(User).all()
    user_ids = [user.id for user in users] if users else [None]
    
    start_time = datetime.utcnow() - timedelta(hours=hours_back)
    
    for i in range(count):
        # Generate timestamp with slight variation
        time_offset = (hours_back * 3600 * i) / count
        timestamp = start_time + timedelta(seconds=time_offset)
        
        # Create realistic log entry
        log = TrafficLog(
            timestamp=timestamp,
            ip_address=generate_ip_address(),
            user_id=random.choice(user_ids) if user_ids[0] is not None else None,
            endpoint=random.choice(SAMPLE_ENDPOINTS),
            method=random.choice(HTTP_METHODS),
            status_code=weighted_choice(STATUS_CODES),
            latency_ms=generate_latency(base_latency=100.0, multiplier=1.0, noise_factor=0.3),
            user_agent=random.choice(SAMPLE_USER_AGENTS),
            geo_location=random.choice(SAMPLE_GEO_LOCATIONS),
        )
        db.add(log)
        
        if (i + 1) % 100 == 0:
            print(f"  Created {i + 1}/{count} logs...")
    
    db.commit()
    print(f"Created {count} traffic logs")


def main():
    """Main bootstrap function."""
    print("="*60)
    print("ANTIGRAVITY DATABASE BOOTSTRAP")
    print("="*60)
    
    # Initialize database
    print("\nInitializing database...")
    init_database()
    
    # Get database session
    db = SessionLocal()
    
    try:
        # Create sample data
        create_sample_users(db, count=50)
        create_sample_traffic_logs(db, count=1000, hours_back=24)
        
        print("\n" + "="*60)
        print("BOOTSTRAP COMPLETE")
        print("="*60)
        print("Database is ready for Antigravity system testing!")
        
    except Exception as e:
        print(f"Error during bootstrap: {e}")
        db.rollback()
    
    finally:
        db.close()


if __name__ == "__main__":
    main()
