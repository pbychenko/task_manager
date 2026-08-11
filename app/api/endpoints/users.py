from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError

from app.api.schemas.user import UserCreate, UserRead
from app.core.security import (
    compare_hash,
    create_jwt_token,
    get_hash,
    get_user_from_token,
)
from app.services.user_service import UserService
from app.utils.unitofwork import IUnitOfWork, UnitOfWork

user_router = APIRouter(prefix="/users", tags=["Users"])


async def get_user_service(uow: IUnitOfWork = Depends(UnitOfWork)) -> UserService:
    return UserService(uow)


@user_router.post(
    "/register/", response_model=UserRead, status_code=status.HTTP_201_CREATED
)
async def create_user(
    user_data: UserCreate, user_service: UserService = Depends(get_user_service)
):
    # if await user_service.get_user("username", user_data.username):
    #     raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="User already exists")

    user_data.password = get_hash(user_data.password)
    try:
        return await user_service.add_user(user_data)
    except IntegrityError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="User already exists"
        ) from error


@user_router.post("/login/")
async def login(
    user_data: UserCreate, user_service: UserService = Depends(get_user_service)
):
    user = await user_service.get_user("username", user_data.username)

    if not user or not compare_hash(user_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials"
        )

    token = create_jwt_token({"sub": user.username})

    return {"access_token": token, "token_type": "bearer"}


@user_router.get("/{user_id}/", response_model=UserRead)
async def get_user_by_id(
    user_id: int,
    current_user: str = Depends(get_user_from_token),
    user_service: UserService = Depends(get_user_service),
):
    """
    Этот маршрут защищен и требует токен. Если токен действителен, мы возвращаем информацию о пользователе.
    """
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token or user not authenticated",
        )

    user = await user_service.get_user("id", str(user_id))

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    return user


@user_router.get("/", response_model=list[UserRead])
async def get_users(
    current_user: str = Depends(get_user_from_token),
    user_service: UserService = Depends(get_user_service),
    param: str = None,
    value: str = None,
):
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token or user not authenticated",
        )
    return await user_service.get_users()
