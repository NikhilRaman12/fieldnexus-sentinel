"""
KRISHIVA AI — Database Engine and Session Management
Supports PostgreSQL with PostGIS, with SQLite fallback for local test execution.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from backend.config.settings import settings
from backend.core.logging import get_logger

logger = get_logger("database")

# Handle SQLite vs PostgreSQL arguments
connect_args = {}
if settings.DATABASE_URL.startswith("sqlite"):
    connect_args["check_same_thread"] = False

engine = create_engine(
    settings.DATABASE_URL,
    echo=settings.DB_ECHO,
    connect_args=connect_args,
    future=True
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, future=True)
Base = declarative_base()


def get_db():
    """FastAPI Dependency for database session management."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Create all tables in the database."""
    logger.info(f"Initializing database schema at {settings.DATABASE_URL}")
    Base.metadata.create_all(bind=engine)
    logger.info("Database schema initialized successfully.")
