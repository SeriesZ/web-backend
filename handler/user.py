import traceback
from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from auth import (ACCESS_TOKEN_EXPIRE_MINUTES, authenticate_user,
                  create_access_token)
from database import get_db
from model.user import User
from schema.token import Token, UserToken
from schema.user import UserRequest, UserResponse

router = APIRouter(tags=["유저"])


@router.post("/login")
async def login(
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


@router.post("/logout")
async def logout():
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Not implemented",
    )


@router.post("/forgot-password")
async def forgot_password():
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Not implemented",
    )


@router.post("/reset-password")
async def reset_password():
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Not implemented",
    )


@router.post("/register", response_model=UserResponse)
async def create_user(
    request: UserRequest,
    db: AsyncSession = Depends(get_db),
):
    db_user = User(
        name=request.name,
        email=request.email,
    )
    db_user.password = request.password
    db.add(db_user)
    try:
        await db.refresh(db_user)
    except Exception:
        traceback.print_exc()
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to create user",
        )
    return UserResponse.model_validate(db_user)


def _create_token(user: User):
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    data = UserToken(
        id=user.id,
        name=user.name,
        email=user.email,
        role=user.role,
        group_id=user.group_id,
    )
    access_token = create_access_token(data, access_token_expires)
    return Token(access_token=access_token, token_type="bearer")
