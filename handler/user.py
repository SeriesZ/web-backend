import traceback
from datetime import timedelta
from typing import Annotated, List

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from auth import authenticate_user, ACCESS_TOKEN_EXPIRE_MINUTES, create_access_token, get_current_active_user
from database import get_db
from model.user import User
from schema.token import Token
from schema.user import UserResponse, UserRequest

router = APIRouter()


@router.post("/token")
async def login_for_access_token(
        form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
        db: AsyncSession = Depends(get_db),
) -> Token:
    user = await authenticate_user(
        email=form_data.username,
        password=form_data.password,
        db=db,
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return _create_token(user)


@router.get("/users/me/", response_model=UserResponse)
async def read_users_me(
        current_user: Annotated[UserResponse, Depends(get_current_active_user)],
):
    return current_user


@router.post("/users/", response_model=UserResponse)
async def create_user(request: UserRequest, db: AsyncSession = Depends(get_db)):
    db_user = User(
        name=request.name,
        email=request.email,
    )
    db_user.password = request.password
    db.add(db_user)
    try:
        await db.commit()
        await db.refresh(db_user)
    except Exception:
        traceback.print_exc()
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to create user",
        )

    return UserResponse(
        id=db_user.id,
        name=db_user.name,
        email=db_user.email,
        token=_create_token(db_user),
    )


@router.get("/users/", response_model=List[UserResponse])
async def read_users(offset: int = 0, limit: int = 10, db: AsyncSession = Depends(get_db)):
    users = await db.execute(select(User).offset(offset).limit(limit))
    return users.scalars().all()


def _create_token(user: User):
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": user.email}, expires_delta=access_token_expires)
    return Token(access_token=access_token, token_type="bearer")
