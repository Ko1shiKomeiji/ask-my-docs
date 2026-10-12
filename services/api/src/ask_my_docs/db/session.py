from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from ask_my_docs.core.config import Settings


def build_engine(settings: Settings) -> AsyncEngine:
    engine = create_async_engine(settings.database_url.get_secret_value(), pool_pre_ping=True)
    return engine


def build_sessionmaker(engine: AsyncEngine) -> async_sessionmaker[AsyncSession]:
    async_session_local = async_sessionmaker(
        bind=engine,
        autoflush=False,
        expire_on_commit=False,
    )
    return async_session_local
