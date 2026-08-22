from app.api.schemas.user import UserCreate, UserFromDB, UserRead
from app.utils.unitofwork import IUnitOfWork
from app.core.security import get_hash, compare_hash
from app.core.exceptions import NotFoundError, InvalidCredentialsError

class UserService:
    def __init__(self, uow: IUnitOfWork):
        self.uow = uow

    async def add_user(self, user_data: UserCreate) -> UserRead:
        user_data.password = get_hash(user_data.password)
        user_dict: dict = user_data.model_dump()

        async with self.uow as uow:
            user_from_db = await uow.user.add_one(user_dict)
            user_to_return = UserRead.model_validate(
                user_from_db
            )
            await uow.commit()
            return user_to_return

    async def authenticate(self, username: str, password: str) -> UserFromDB:
        async with self.uow as uow:
            user = await uow.user.find_one("username", username)
            if user is None or not compare_hash(password, user.password):
                raise InvalidCredentialsError("Invalid username or password")
        
            return UserFromDB.model_validate(user)
        

    async def get_user(self, param: str, value: str) -> UserFromDB:
        async with self.uow as uow:
            user = await uow.user.find_one(param, value)
            if not user:
                raise NotFoundError(f"User with {param}={value} not found")
            return UserFromDB.model_validate(user)
        

    async def get_users(self) -> list[UserFromDB]:
        async with self.uow as uow:
            users: list = await uow.user.find_all()
            return [UserFromDB.model_validate(user) for user in users]
