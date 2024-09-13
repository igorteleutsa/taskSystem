from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import update, delete
from typing import Type, TypeVar, Generic, Optional, List
from app.core.base_model import BaseModel

ModelType = TypeVar("ModelType", bound=BaseModel)


class BaseRepository(Generic[ModelType]):
    def __init__(self, model: Type[ModelType], db_session: AsyncSession):
        self.model = model
        self.db_session = db_session

    async def get_by_id(self, id: int) -> Optional[ModelType]:
        query = select(self.model).where(self.model.id == id)
        result = await self.db_session.execute(query)
        return result.scalars().first()

    async def get_all(
        self, skip: Optional[int] = None, limit: Optional[int] = None
    ) -> List[ModelType]:
        query = select(self.model)

        # Apply pagination if skip and/or limit are provided
        if skip is not None:
            query = query.offset(skip)
        if limit is not None:
            query = query.limit(limit)

        result = await self.db_session.execute(query)
        return result.scalars().all()

    async def create(self, obj_in: dict) -> ModelType:
        db_obj = self.model(**obj_in)
        self.db_session.add(db_obj)
        await self.db_session.commit()
        await self.db_session.refresh(db_obj)
        return db_obj

    async def update(self, id: int, obj_in: dict) -> Optional[ModelType]:
        query = (
            update(self.model)
            .where(self.model.id == id)
            .values(**obj_in)
            .execution_options(synchronize_session="fetch")
        )
        await self.db_session.execute(query)
        await self.db_session.commit()
        return await self.get_by_id(id)

    async def delete(self, id: int) -> Optional[ModelType]:
        query = (
            delete(self.model)
            .where(self.model.id == id)
            .execution_options(synchronize_session="fetch")
        )
        await self.db_session.execute(query)
        await self.db_session.commit()
        return None
