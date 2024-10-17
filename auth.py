import os
from datetime import datetime, timedelta, timezone
from typing import Annotated, Union

from dotenv import load_dotenv
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from jwt import InvalidTokenError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from model.user import User
from schema.token import UserToken

load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = float(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


async def get_user(db: AsyncSession, email: str):
    from model.user import User

    result = await db.execute(select(User).filter(User.email == email))
    return result.scalar_one_or_none()


async def authenticate_user(
    email: str, password: str, db: AsyncSession = Depends(get_db)
):
    user = await get_user(db, email)
    if not user:
        return False
    if not user.verify_password(password):
        return False
    return user


def create_access_token(
    data: UserToken, expires_delta: Union[timedelta, None] = None
):
    to_encode = data.dict()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        token_data = UserToken(
            id=payload.get("id"),
            name=payload.get("name"),
            email=payload.get("email"),
            role=payload.get("role"),
            group_id=payload.get("group_id"),
        )
        UserToken.validate(token_data)
    except InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    # 부하 문제로 user 조회를 제거
    return User(
        id=token_data.id,
        name=token_data.name,
        email=token_data.email,
        role=token_data.role,
        group_id=token_data.group_id,
    )
