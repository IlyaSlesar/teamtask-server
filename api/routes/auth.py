from collections.abc import Sequence
from typing import Annotated

from fastapi import (
    APIRouter,
    HTTPException,
    Depends,
    status
)
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from core.security import (
    hash_password,
    verify_password,
    encode_token,
)
from db.models import User
from db.session import get_db
from schemas.user import UserReadSimple, UserRead, UserCreate
from schemas.auth import Token
from api.deps import get_current_user


prefix_url = "/auth"
router = APIRouter(
    prefix=prefix_url
)


@router.get("/", response_model=Sequence[UserReadSimple])
async def read_users(
    session: Annotated[AsyncSession, Depends(get_db)]
):
    users = (await session.execute(select(User))).scalars().all()
    return users


@router.post("/new", response_model=UserReadSimple)
async def create_user(
    user: UserCreate,
    session: Annotated[AsyncSession, Depends(get_db)]
):
    password_hash = hash_password(user.password)
    db_user = User(
        username=user.username,
        password_hash=password_hash
    )
    session.add(db_user)
    try:
        await session.commit()
    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username already taken."
        )
    await session.refresh(db_user)
    return db_user


@router.get("/me", response_model=UserRead)
def read_current_user(
    current_user: Annotated[User, Depends(get_current_user)]
):
    return current_user


@router.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    session: Annotated[AsyncSession, Depends(get_db)]
):
    user = (await session.execute(
        select(User)
        .where(User.username == form_data.username)
    )).scalar_one_or_none()
    incorrect = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Incorrect username or password",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if not user:
        raise incorrect
    if not verify_password(user.password_hash, form_data.password):
        raise incorrect

    access_token = encode_token(user.username)
    return {"access_token": access_token, "token_type": "bearer"}
