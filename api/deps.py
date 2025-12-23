from typing import Annotated

from fastapi import (
    Depends,
    HTTPException,
    status
)
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import (
    AsyncSession
)

from db.session import get_db
from db.models import User, TaskLog
from core.security import decode_token, InvalidCredentials


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    session: Annotated[AsyncSession, Depends(get_db)]
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        token_data = decode_token(token)
    except InvalidCredentials:
        raise credentials_exception
    user = (await session.execute(
        select(User)
        .options(
            selectinload(User.projects),
            selectinload(User.owned_projects),
            selectinload(User.logs),
        )
        .where(User.username == token_data.username)
    )).scalar_one_or_none()
    if user is None:
        raise credentials_exception
    return user


async def log_task_modification(
    session: AsyncSession,
    user_id: int,
    task_id: int,
    action: str
):
    session.add(TaskLog(user_id=user_id, task_id=task_id, action=action))
