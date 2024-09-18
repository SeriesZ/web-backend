import uuid
from datetime import datetime

import pytz
from sqlalchemy import Boolean, Column, DateTime, String, event
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.ext.declarative import as_declarative, declared_attr
from sqlalchemy.orm import sessionmaker

SQLALCHEMY_DATABASE_URL = "sqlite+aiosqlite:///./test.db"
KST = pytz.timezone("Asia/Seoul")

async_engine = create_async_engine(SQLALCHEMY_DATABASE_URL, echo=True)

AsyncSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_db():
    async with AsyncSessionLocal() as session:
        yield session


async def init_db():
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


@as_declarative()
class Base:
    id = Column(String, primary_key=True, index=True)
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(KST),
    )
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(KST),
        onupdate=lambda: datetime.now(KST),
    )
    in_use = Column(Boolean, default=True)

    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
            else:
                raise AttributeError(
                    f"{self.__class__.__name__} does not have attribute {key}"
                )


@event.listens_for(Base, "before_insert", propagate=True)
def before_insert(mapper, connection, target):
    table_name = target.__tablename__
    target.id = f"{table_name}_{uuid.uuid4()}"
