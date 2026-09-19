from app.db.models import User
from app.repositories.base_repository import Repository
from sqlalchemy import update



class UserRepository(Repository):
    model = User

    async def update_user(self, param, value, data):
        stmt = (
            update(self.model)
            .where(getattr(self.model, param) == value)
            .values(**data)
            .returning(self.model)
        )
        result = await self.session.execute(stmt)

        return result.scalar_one_or_none()
