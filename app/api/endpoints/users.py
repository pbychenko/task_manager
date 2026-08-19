from fastapi import APIRouter, Depends, HTTPException, status

from app.api.schemas.user import UserCreate, UserRead
from app.core.security import (
    compare_hash,
    create_jwt_token,
    get_user_from_token,
)
from app.services.user_service import UserService
from app.utils.unitofwork import IUnitOfWork, UnitOfWork


user_router = APIRouter(prefix="/users", tags=["Users"])

async def get_user_service(uow: IUnitOfWork = Depends(UnitOfWork)) -> UserService:
    return UserService(uow)


@user_router.post("/register/", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_data: UserCreate, user_service: UserService = Depends(get_user_service)
):
    return await user_service.add_user(user_data)


@user_router.post("/login/")
async def login(
    user_data: UserCreate, user_service: UserService = Depends(get_user_service)
):
    user = await user_service.get_user("username", user_data.username)

    if not user or not compare_hash(user_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials"
        )


    token = create_jwt_token({"sub": str(user.id)})

    return {"access_token": token, "token_type": "bearer"}


@user_router.get("/{user_id}/", response_model=UserRead)
async def get_user_by_id(
    user_id: int,
    _: UserRead = Depends(get_user_from_token),
    user_service: UserService = Depends(get_user_service),
):  
   return await user_service.get_user("id", user_id)


@user_router.get("/", response_model=list[UserRead])
async def get_users(
    _: str = Depends(get_user_from_token),
    user_service: UserService = Depends(get_user_service)
):
    return await user_service.get_users()
