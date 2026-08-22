from abc import ABC, abstractmethod

from sqlalchemy import delete, insert, select
from sqlalchemy.ext.asyncio import AsyncSession

class AbstractRepository(ABC):
    @abstractmethod
    async def add_one(self, data: dict):
        raise NotImplementedError

    @abstractmethod
    async def find_all(self):
        raise NotImplementedError


class Repository(
    AbstractRepository
):  
    model = None  

    def __init__(self, session: AsyncSession):
        self.session = session 

    async def add_one(self, data: dict):
        stmt = insert(self.model).values(**data).returning(self.model)
        res = await self.session.execute(stmt)

        return res.scalar_one_or_none()

    async def find_all(self):
        result = await self.session.execute(select(self.model))
        return result.scalars().all()

    async def find_one(self, param, value):
        result = await self.session.execute(
            select(self.model).where(getattr(self.model, param) == value)
        )
        return result.scalar_one_or_none()

    async def delete_one(self, id):
        stmt = delete(self.model).where(self.model.id == id)

        result = await self.session.execute(stmt)

        return result.rowcount
