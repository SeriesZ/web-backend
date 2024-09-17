from typing import AsyncGenerator

import pytest
from httpx import AsyncClient
from sqlalchemy import StaticPool, create_engine
from sqlalchemy.ext.asyncio import (AsyncConnection, AsyncSession,
                                    AsyncTransaction, create_async_engine)
from sqlalchemy.orm import sessionmaker

from database import Base, get_db
from main import app


@pytest.fixture(scope="function")
def db_session():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = sessionmaker(
        autocommit=False, autoflush=False, bind=engine
    )
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    yield session
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"


@pytest.fixture(scope="session")
async def connection() -> AsyncGenerator[AsyncConnection, None]:
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=True)
    async with engine.connect() as conn:
        yield conn


@pytest.fixture
async def transaction(
    connection: AsyncConnection,
) -> AsyncGenerator[AsyncTransaction, None]:
    trans = await connection.begin()
    yield trans
    await trans.rollback()


@pytest.fixture
async def async_session(
    connection: AsyncConnection, transaction: AsyncTransaction
) -> AsyncGenerator[AsyncSession, None]:
    async_session = AsyncSession(bind=connection, expire_on_commit=False)

    await connection.run_sync(Base.metadata.create_all)

    async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
        yield async_session

    app.dependency_overrides[get_db] = override_get_db

    yield async_session

    await async_session.close()
    del app.dependency_overrides[get_db]


@pytest.fixture
async def client(
    async_session: AsyncSession,
) -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(app=app, base_url="http://testserver") as ac:
        yield ac


async def create_user_and_get_auth_token(
    client: AsyncClient,
    email: str = "testuser@test.com",
    password: str = "password",
):
    test_user = {"name": "testuser", "email": email, "password": password}

    response = await client.post("/users/", json=test_user)
    assert response.status_code == 200, "Failed to create user"

    user = response.json()
    token = user["token"]
    access_token = token["access_token"]
    headers = {"Authorization": f"Bearer {access_token}"}
    return headers
