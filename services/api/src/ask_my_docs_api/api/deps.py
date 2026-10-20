from collections.abc import AsyncGenerator
from typing import Annotated

from fastapi import Depends, Request
from fastapi.security import APIKeyHeader
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ask_my_docs_api.core.errors import UnauthorizedError
from ask_my_docs_api.core.security import hash_api_key
from ask_my_docs_api.db.models import ApiKey, User

api_key_scheme = APIKeyHeader(name="X-API-Key", auto_error=False)


async def get_session(request: Request) -> AsyncGenerator[AsyncSession]:
    async_sessionmaker = request.app.state.sessionmaker
    async with async_sessionmaker() as session:
        yield session


SessionDep = Annotated[AsyncSession, Depends(get_session)]


async def get_current_user(
    db: SessionDep, api_key: Annotated[str | None, Depends(api_key_scheme)]
) -> User:
    if not api_key:
        raise UnauthorizedError("No API Key")

    hash = hash_api_key(api_key)
    stmt = (
        select(User).join(User.api_keys).where(ApiKey.key_hash == hash, ApiKey.revoked_at.is_(None))
    )
    user = await db.scalar(stmt)
    if user is None:
        raise UnauthorizedError

    return user


CurrentUser = Annotated[User, Depends(get_current_user)]
