from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncEngine, create_async_engine
from sqlalchemy.orm import declarative_base

from src.db.config import db_config


def create_engine(db_url: str = db_config.DATABASE_URL_asyncpg) -> AsyncEngine:
    return create_async_engine(db_url, echo=True)


SessionLocal = async_sessionmaker(autocommit=False, autoflush=False, bind=create_engine())

Base = declarative_base()
