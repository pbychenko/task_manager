from app.api.schemas.user import UserCreate, UserFromDB, UserRead, UserRoleUpdate
from app.core.exceptions import InvalidCredentialsError, NotFoundError
from app.core.security import compare_hash, get_hash
from app.utils.unitofwork import IUnitOfWork


class UserService:
    def __init__(self, uow: IUnitOfWork):
        self.uow = uow

    async def add_user(self, user_data: UserCreate) -> UserRead:
        user_data.password = get_hash(user_data.password)
        user_dict: dict = user_data.model_dump()

        async with self.uow as uow:
            user_from_db = await uow.user.add_one(user_dict)
            user_to_return = UserRead.model_validate(user_from_db)

            await uow.commit()

            return user_to_return

    async def authenticate(self, username: str, password: str) -> UserFromDB:
        async with self.uow as uow:
            user = await uow.user.find_one("username", username)

            if user is None or not compare_hash(password, user.password):
                raise InvalidCredentialsError("Invalid username or password")

            return UserFromDB.model_validate(user)

    async def get_user(self, param: str, value: str) -> UserRead:
        async with self.uow as uow:
            user = await uow.user.find_one(param, value)

            if not user:
                raise NotFoundError(f"User with {param}={value} not found")

            return UserRead.model_validate(user)

    async def get_users(self, skip, limit) -> list[UserRead]:
        async with self.uow as uow:
            users: list = await uow.user.find_all(skip, limit)
            
            return [UserRead.model_validate(user) for user in users]


    async def update_user_role(self, user_id: int, role_update: UserRoleUpdate) -> UserRead:
        data: dict = role_update.model_dump(exclude_unset=True)

        async with self.uow as uow:
            updated_user = await uow.user.update_user("id", user_id, data)

            if updated_user is None:
                raise NotFoundError(f"User {user_id} not found")

            user_to_return = UserRead.model_validate(updated_user)
            await uow.commit() 

            return user_to_return
