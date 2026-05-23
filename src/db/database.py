from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.db.models import Base

from src.core.config import settings

# Grabs connection configurations matching your internal container network names
DATABASE_URL = settings.database_url

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    """Builds database schemas directly on host/container instance."""
    Base.metadata.create_all(bind=engine)

def get_db():
    """Dependency tracking block for FastAPI route integration."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()