import logging
from sqlalchemy import create_engine, pool
from sqlalchemy.orm import sessionmaker, declarative_base
from config import settings

logger = logging.getLogger(__name__)

# Create engine with connection pooling
engine = create_engine(
    settings.DATABASE_URL,
    echo=False,
    poolclass=pool.NullPool,  # Use NullPool to avoid connection issues in Celery
    connect_args={"connect_timeout": 10}
)

# Create session factory
SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False
)

# Create base class for models
Base = declarative_base()

logger.info("Database engine initialized")


def get_db():
    """
    Dependency for FastAPI to provide database sessions.
    
    Yields:
        SQLAlchemy Session
    """
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        logger.error(f"Database error: {e}")
        db.rollback()
        raise
    finally:
        db.close()
