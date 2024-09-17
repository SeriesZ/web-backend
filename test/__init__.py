import pytest
from sqlalchemy import create_engine, StaticPool
from sqlalchemy.orm import sessionmaker

from database import Base

SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

ENGINE = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=ENGINE)


@pytest.fixture(scope="function")
def db_session():
    """테스트를 위한 데이터베이스 세션."""
    Base.metadata.create_all(bind=ENGINE)
    session = TestingSessionLocal()
    yield session
    Base.metadata.drop_all(bind=ENGINE)
