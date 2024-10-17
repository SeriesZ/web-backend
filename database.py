import os
import uuid
from datetime import datetime

import casbin
import casbin_async_sqlalchemy_adapter
import pytz
from sqlalchemy import Column, DateTime, String, event
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.ext.declarative import as_declarative, declared_attr
from sqlalchemy.orm import configure_mappers, sessionmaker

ROOT_PATH = os.path.dirname(os.path.abspath(__file__))

SQLALCHEMY_DATABASE_URL = "sqlite+aiosqlite:///./test.db"
KST = pytz.timezone("Asia/Seoul")

async_engine = create_async_engine(SQLALCHEMY_DATABASE_URL, echo=True)
adapter = casbin_async_sqlalchemy_adapter.Adapter(SQLALCHEMY_DATABASE_URL)
enforcer = casbin.AsyncEnforcer(f"{ROOT_PATH}/model.conf", adapter)

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
    configure_mappers()
    await adapter.create_table()
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


@as_declarative()
class Base:
    __versioned__ = {}

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
    created_by = Column(String)

    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
            raise AttributeError(
                f"{self.__class__.__name__} does not have attribute {key}"
            )


@event.listens_for(Base, "before_insert", propagate=True)
def before_insert(mapper, connection, target):
    # FIXME context로 유저 정보 주입
    # https://medium.com/wantedjobs/fastapi%EC%97%90%EC%84%9C-sqlalchemy-session-%EB%8B%A4%EB%A3%A8%EB%8A%94-%EB%B0%A9%EB%B2%95-118150b87efa
    table_name = target.__tablename__
    if not target.id:
        target.id = f"{table_name}_{uuid.uuid4()}"
