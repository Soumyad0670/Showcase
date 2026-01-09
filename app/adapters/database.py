# app/adapters/database.py

import logging
from typing import Generator

from sqlmodel import Session, create_engine
# from sqlalchemy.orm import sessionmaker, DeclarativeBase, Session # Removed Session override
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from sqlalchemy.exc import SQLAlchemyError

from app.core.config import settings

logger = logging.getLogger(__name__)

# Declarative Base (shared by all ORM models)
class Base(DeclarativeBase):
    pass

try:
    engine = create_engine(
        settings.DATABASE_URL,
        echo=settings.DEBUG,
        pool_pre_ping=True,
        pool_size=10,
        max_overflow=20,
        future=True,
    )

except Exception as exc:
    # If SQLite, might fail with pool arguments? SQLite doesn't support pool_size?
    # Retrying without pool args just in case or assume PostgreSQL for prod
    if "sqlite" in settings.DATABASE_URL:
         engine = create_engine(
            settings.DATABASE_URL,
            echo=settings.DEBUG,
            connect_args={"check_same_thread": False},
        )
    else:
        raise

# Session Factory
SessionLocal = sessionmaker(
    bind=engine,
    class_=Session,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False,
)

# Session Dependency / Provider
def get_db() -> Generator[Session, None, None]:
    """
    Provides a scoped database session.
    """
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except SQLAlchemyError:
        session.rollback()
        logger.exception("Database transaction failed")
        raise
    finally:
        session.close()

def close_engine() -> None:
    try:
        engine.dispose()
        logger.info("Database engine disposed successfully")
    except Exception:
        logger.exception("Error while disposing database engine")
