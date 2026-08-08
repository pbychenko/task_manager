from app.db.models import Task
from app.repositories.base_repository import Repository
from sqlalchemy import update


class TaskRepository(Repository):
    model = Task

    async def update_tasks(self, param, value, data: dict):
        stmt = (
            update(self.model)
            .where(getattr(self.model, param) == value)
            .values(**data)
            .returning(self.model)
        )
        result = await self.session.execute(stmt)
        return result
        # return result.scalar_one_or_none() 