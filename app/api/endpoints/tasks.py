from fastapi import APIRouter, Depends, status, HTTPException
from fastapi.responses import JSONResponse

from app.api.endpoints.users import get_user_service
from app.api.schemas.task import TaskFromDB, TaskCreate
from app.services.task_service import TaskService
from app.services.user_service import UserService

from app.utils.unitofwork import UnitOfWork, IUnitOfWork
from app.core.security import create_jwt_token, get_user_from_token, get_hash, compare_hash


task_router = APIRouter(
    prefix="/tasks",
    tags=["tasks"]
)

async def get_task_service(uow: IUnitOfWork = Depends(UnitOfWork)) -> TaskService:
    return TaskService(uow)

async def get_user_service(uow: IUnitOfWork = Depends(UnitOfWork)) -> UserService:
    return UserService(uow)

@task_router.get("/", response_model=list[TaskFromDB] | None)
async def get_all_tasks(task_service: TaskService = Depends(get_task_service)):
    return await task_service.get_tasks()

@task_router.post("/add", response_model=TaskFromDB)
async def create_task(task_data: TaskCreate, task_service: TaskService = Depends(get_task_service),
                      current_user: str = Depends(get_user_from_token), user_service: UserService = Depends(get_user_service)):
    user = await user_service.get_user("username", current_user)
    if user:
        await task_service.add_task(task_data, creator_id=user.id)
    # # Если пользователь не найден, возвращаем ошибку
    return {"error": "User not foddund"}


@task_router.patch("/")
async def update_task():
    pass

@task_router.delete("/")
async def delete_task():
    pass