from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from starlette.exceptions import HTTPException

from database import get_db


class CrudRepository:
    db: AsyncSession

    def __init__(self, db: AsyncSession):
        self.db = db

    async def fetch_all(self, entity_class, offset=0, limit=10, clause=None):
        statement = select(entity_class)
        if clause is not None:
            statement = statement.where(clause)

        result = await self.db.execute(statement.offset(offset).limit(limit))
        return result.scalars().all()

    async def find_by_id(self, entity_class, entity_id, field_name="id"):
        field = getattr(entity_class, field_name, None)
        if not field:
            raise ModuleNotFoundError(
                f"Field '{field_name}' not found in {entity_class.__name__}"
            )

        entity = await self.db.execute(
            select(entity_class).where(field == entity_id)
        )
        entity = entity.scalar_one_or_none()
        if not entity:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"entity({entity_class.__name__}) not found with {field_name}={entity_id}",
            )
        return entity

    async def create(self, entity):
        self.db.add(entity)
        await self.db.commit()
        await self.db.refresh(entity)
        return entity

    async def update(self, entity, field_name="id"):
        entity_id = getattr(entity, field_name, None)
        existing_entity = await self.find_by_id(
            entity.__class__, entity_id, field_name
        )

        for key, value in entity.__dict__.items():
            if key != "_sa_instance_state":
                setattr(existing_entity, key, value)
        self.db.add(existing_entity)
        await self.db.refresh(existing_entity)
        return existing_entity

    async def delete(self, entity, field_name="id"):
        entity_id = getattr(entity, field_name, None)
        existing_entity = await self.find_by_id(
            entity.__class__, entity_id, field_name
        )
        await self.db.delete(existing_entity)
        await self.db.commit()


async def get_repository(
    db: AsyncSession = Depends(get_db),
) -> CrudRepository:
    return CrudRepository(db)
