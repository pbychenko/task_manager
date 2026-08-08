from fastapi import APIRouter, Depends, status, HTTPException
from fastapi.responses import JSONResponse

from app.api.schemas.user import UserFromDB, UserCreate
from app.services.user_service import UserService

from app.utils.unitofwork import UnitOfWork, IUnitOfWork
from app.core.security import create_jwt_token, get_user_from_token, get_hash, compare_hash


user_router = APIRouter(
    prefix="/users",
    tags=["Users"]
)


async def get_user_service(uow: IUnitOfWork = Depends(UnitOfWork)) -> UserService:
    return UserService(uow)


@user_router.post("/register/", response_model=UserFromDB)
async def create_user(user_data: UserCreate, user_service: UserService = Depends(get_user_service)):
    if await user_service.get_user("username", user_data.username):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="User already exists")
    
    user_data.password = get_hash(user_data.password)
    return await user_service.add_user(user_data)
    # return JSONResponse(status_code=201,
    #                     content={"message": "New user created"})

@user_router.post("/login/")
async def login(user_data: UserCreate, user_service: UserService = Depends(get_user_service)):
    user = await user_service.get_user("username", user_data.username)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    if not compare_hash(user_data.password, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    
    token = create_jwt_token({"sub": user_data.username})

    return {"access_token": token, "token_type": "bearer"}

@user_router.get("/about/")
async def about_me(current_user: str = Depends(get_user_from_token), user_service: UserService = Depends(get_user_service)):
    """
    Этот маршрут защищен и требует токен. Если токен действителен, мы возвращаем информацию о пользователе.
    """
    user = await user_service.get_user("username", current_user)
    if user:
        return user
    # # Если пользователь не найден, возвращаем ошибку
    return {"error": "User not found"}


@user_router.get("/", response_model=UserFromDB | None)
async def get_users(user_service: UserService = Depends(get_user_service), param: str = None, value: str = None):
    return await user_service.get_user(param, value)