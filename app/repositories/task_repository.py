from sqlalchemy import update

from app.db.models import Task
from app.repositories.base_repository import Repository


class TaskRepository(Repository):
    model = Task

    async def update_task(self, param, value, data):
        stmt = (
            update(self.model)
            .where(getattr(self.model, param) == value)
            .values(**data)
            .returning(self.model)
        )

        result = await self.session.execute(stmt)
        return (
            result.scalar_one_or_none()
        )  # Возвращает одну запись или None, если запись не найдена
        # return result.scalar_one_or_none()
