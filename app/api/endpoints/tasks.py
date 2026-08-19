from fastapi import APIRouter, Depends, Response, status

from app.api.schemas.task import TaskCreate, TaskFromDB, TaskUpdate
from app.api.schemas.user import UserRead
from app.core.security import get_user_from_token
from app.services.task_service import TaskService
from app.services.user_service import UserService
from app.utils.unitofwork import IUnitOfWork, UnitOfWork

task_router = APIRouter(prefix="/tasks", tags=["tasks"])


async def get_task_service(uow: IUnitOfWork = Depends(UnitOfWork)) -> TaskService:
    return TaskService(uow)


async def get_user_service(uow: IUnitOfWork = Depends(UnitOfWork)) -> UserService:
    return UserService(uow)


@task_router.get("/", response_model=list[TaskFromDB])
async def get_all_tasks(
    _: str = Depends(get_user_from_token),
    task_service: TaskService = Depends(get_task_service)
):
    return await task_service.get_tasks()


@task_router.post("/", response_model=TaskFromDB)
async def create_task(
    task_data: TaskCreate,
    task_service: TaskService = Depends(get_task_service),
    current_user: UserRead = Depends(get_user_from_token)
):
    return await task_service.add_task(task_data, creator_id=current_user.id)


@task_router.put("/{task_id}", response_model=TaskFromDB)
async def update_task(
    task_id: int,
    task_data: TaskUpdate,
    task_service: TaskService = Depends(get_task_service),
    _: UserRead = Depends(get_user_from_token),
):      

    return await task_service.update_task(task_id, task_data)


@task_router.delete("/{task_id}")
async def delete_task(
    task_id: int,
    task_service: TaskService = Depends(get_task_service),
    current_user: UserRead = Depends(get_user_from_token),
):

    await task_service.delete_task(task_id, current_user.id)

    return Response(status_code=status.HTTP_204_NO_CONTENT)
