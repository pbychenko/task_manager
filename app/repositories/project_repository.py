from sqlalchemy import update

from app.db.models import Project
from app.repositories.base_repository import Repository


class ProjectRepository(Repository):
    model = Project

    async def update_project(self, param, value, data):
        stmt = (
            update(self.model)
            .where(getattr(self.model, param) == value)
            .values(**data)
            .returning(self.model)
        )
        result = await self.session.execute(stmt)

        return result.scalar_one_or_none()
