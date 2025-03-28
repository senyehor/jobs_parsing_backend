from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncEngine, create_async_engine
from sqlalchemy.orm import declarative_base

from src.db.config import db_config


def create_engine(db_url: str = db_config.DATABASE_URL_asyncpg, **kwargs) -> AsyncEngine:
    return create_async_engine(db_url, **kwargs)


_session_factory = async_sessionmaker(autocommit=False, autoflush=False, bind=create_engine())


async def create_session():
    async with _session_factory() as session:
        async with session.begin():
            try:
                yield session
            except Exception as e:
                await session.rollback()
                raise e


Base = declarative_base()
