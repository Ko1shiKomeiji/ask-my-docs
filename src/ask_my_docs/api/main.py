from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from ask_my_docs.api.routers import health
from ask_my_docs.core.config import Settings, get_settings
from ask_my_docs.core.logging import configure_logging
from ask_my_docs.core.middleware import RequestIDMiddleware
from ask_my_docs.db.session import build_engine, build_sessionmaker


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None]:
    settings = app.state.settings
    engine = build_engine(settings)
    sessionmaker = build_sessionmaker(engine)
    app.state.engine = engine
    app.state.sessionmaker = sessionmaker
    try:
        yield
    finally:
        await engine.dispose()


def create_app(settings: Settings | None = None) -> FastAPI:
    if settings is None:
        settings = get_settings()
    configure_logging(settings)
    app = FastAPI(lifespan=lifespan)
    app.state.settings = settings
    app.add_middleware(RequestIDMiddleware)
    app.include_router(health.router)
    return app
