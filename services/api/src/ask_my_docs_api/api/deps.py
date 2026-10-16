from collections.abc import AsyncGenerator
from typing import Annotated

from fastapi import Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession


async def get_session(request: Request) -> AsyncGenerator[AsyncSession]:
    async_sessionmaker = request.app.state.sessionmaker
    async with async_sessionmaker() as session:
        yield session


SessionDep = Annotated[AsyncSession, Depends(get_session)]
