"""
Database connection for worker
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://briefing_user:briefing_pass@localhost:5432/briefing_db"
)

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db_session():
    """Get database session"""
    return SessionLocal()


# Import models
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'api'))
from models import *  # noqa

