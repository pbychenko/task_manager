from fastapi import APIRouter, Depends, Response, status

from app.api.schemas.task import TaskCreate, TaskFromDB, TaskUpdate, TaskUpdateStatus
from app.api.schemas.user import UserRead
from app.core.security import get_user_from_token, require_role
from app.services.task_service import TaskService
from app.services.user_service import UserService
from app.utils.unitofwork import IUnitOfWork, UnitOfWork
from app.core.roles import Role


task_router = APIRouter(prefix="/tasks", tags=["tasks"])


async def get_task_service(uow: IUnitOfWork = Depends(UnitOfWork)) -> TaskService:
    return TaskService(uow)


async def get_user_service(uow: IUnitOfWork = Depends(UnitOfWork)) -> UserService:
    return UserService(uow)


@task_router.get("/{task_id}", response_model=TaskFromDB)
async def get_task_by_id(
    task_id: int,
    _: str = Depends(get_user_from_token),
    task_service: TaskService = Depends(get_task_service),
):
    return await task_service.get_task("id", task_id)


@task_router.get("/", response_model=list[TaskFromDB])
async def get_all_tasks(
    skip: int = 0,
    limit: int = 10,
    _: str = Depends(get_user_from_token),
    task_service: TaskService = Depends(get_task_service),
):
    return await task_service.get_tasks(skip, limit)


@task_router.post("/", response_model=TaskFromDB)
async def create_task(
    task_data: TaskCreate,
    task_service: TaskService = Depends(get_task_service),
    current_user: UserRead = Depends(require_role(Role.MANAGER)),
):
    return await task_service.add_task(task_data, current_user)


@task_router.patch("/{task_id}", response_model=TaskFromDB)
async def update_task(
    task_id: int,
    task_data: TaskUpdate,
    task_service: TaskService = Depends(get_task_service),
    current_user: UserRead = Depends(require_role(Role.MANAGER)),
):

    return await task_service.update_task(task_id, task_data, current_user)

@task_router.patch("/{task_id}/status", response_model=TaskFromDB)
async def update_task_status(
    task_id: int,
    task_data: TaskUpdateStatus,
    task_service: TaskService = Depends(get_task_service),
    current_user: UserRead = Depends(get_user_from_token),
):

    return await task_service.update_task_status(task_id, task_data, current_user)

@task_router.delete("/{task_id}")
async def delete_task(
    task_id: int,
    task_service: TaskService = Depends(get_task_service),
    current_user: UserRead = Depends(require_role(Role.MANAGER)),
):

    await task_service.delete_task(task_id, current_user)

    return Response(status_code=status.HTTP_204_NO_CONTENT)
