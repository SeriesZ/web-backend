from typing import AsyncGenerator

import casbin_sqlalchemy_adapter
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
    adapter = casbin_sqlalchemy_adapter.Adapter(engine)
    adapter.create_table()
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

    response = await client.post("/register", json=test_user)
    assert response.status_code == 200, "Failed to create user"

    response = await client.post(
        "/login", data={"username": email, "password": password}
    )
    assert response.status_code == 200, "Failed to get access token"
    token = response.json()
    access_token = token["access_token"]
    headers = {"Authorization": f"Bearer {access_token}"}
    return headers


@pytest.fixture
async def create_ideation_data(async_session: AsyncSession):
    import datetime

    from model.ideation import Ideation
    from model.invest import Investment, Investor
    from model.user import RoleEnum, User

    investor = Investor(
        name="Test Investor",
        description="This is a test investor",
        image="http://example.com/image.jpg",
        assets_under_management="1million",
        investment_count=1234,
    )
    async_session.add(investor)
    await async_session.commit()
    await async_session.refresh(investor)

    user = User(
        name="testuser",
        email="test234@test.com",
    )
    user.password = "password"
    user.role = RoleEnum.INVESTOR.value
    user.investor_id = investor.id

    async_session.add(user)
    await async_session.commit()
    await async_session.refresh(user)

    ideation = Ideation(
        title="Test Ideation",
        content="This is a test idea",
        image="http://example.com/image.jpg",
        theme="BioIndustry",
        presentation_date=datetime.datetime(2024, 1, 1),
        close_date=datetime.datetime(2024, 1, 31),
        investment_goal=10000,
    )
    ideation.user_id = user.id
    async_session.add(ideation)
    await async_session.commit()
    await async_session.refresh(ideation)

    investment1 = Investment(
        ideation_id=ideation.id,
        investor_id=investor.id,
        amount=100,
        approval_status=True,
    )
    investment2 = Investment(
        ideation_id=ideation.id,
        investor_id=investor.id,
        amount=200,
        approval_status=True,
    )
    async_session.add(investment1)
    async_session.add(investment2)
    await async_session.commit()
    await async_session.refresh(investment1)
    await async_session.refresh(investment2)
