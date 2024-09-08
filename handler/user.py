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
    user = await authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": user.name}, expires_delta=access_token_expires)
    return Token(access_token=access_token, token_type="bearer")


@router.get("/users/me/", response_model=UserResponse)
async def read_users_me(
    current_user: Annotated[UserResponse, Depends(get_current_active_user)],
):
    return current_user


@router.post("/users/", response_model=UserResponse)
async def create_user(request: UserRequest, db: AsyncSession = Depends(get_db)):
    db_user = User(
        name=request.name,
        password=request.password,
        email=request.email,
        disabled=False,
    )
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user


@router.get("/users/", response_model=List[UserResponse])
async def read_users(offset: int = 0, limit: int = 10, db: AsyncSession = Depends(get_db)):
    users = await db.execute(select(User).offset(offset).limit(limit))
    return users.scalars().all()
