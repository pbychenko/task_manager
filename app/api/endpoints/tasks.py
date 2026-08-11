from fastapi import APIRouter, Depends, HTTPException, Response, status

from app.api.endpoints.users import get_user_service
from app.api.schemas.task import TaskBulkUpdate, TaskCreate, TaskFromDB, TaskUpdate
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
    current_user: str = Depends(get_user_from_token),
    task_service: TaskService = Depends(get_task_service),
):
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token or user not authenticated",
        )

    return await task_service.get_tasks()


@task_router.post("/", response_model=TaskFromDB)
async def create_task(
    task_data: TaskCreate,
    task_service: TaskService = Depends(get_task_service),
    current_user: str = Depends(get_user_from_token),
    user_service: UserService = Depends(get_user_service),
):
    user = await user_service.get_user("username", current_user)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token or user not authenticated",
        )

    return await task_service.add_task(task_data, creator_id=user.id)


@task_router.put("/{task_id}", response_model=TaskFromDB)
async def update_task(
    task_id: int,
    task_data: TaskUpdate,
    task_service: TaskService = Depends(get_task_service),
    current_user: str = Depends(get_user_from_token),
):

    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token or user not authenticated",
        )

    task = await task_service.get_task("id", task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Task not found"
        )

    data = task_data.model_dump(exclude_unset=True)
    if not data:
        raise HTTPException(
            status_code=422,
            detail="At least one task field must be provided for update",
        )

    update_task = await task_service.update_task(task_id, data)
    if not update_task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found or no changes made",
        )

    return update_task


# @task_router.put("/update", response_model=list[TaskFromDB])
# async def update_tasks(
#     tasks_data: list[TaskBulkUpdate],
#     task_service: TaskService = Depends(get_task_service),
#     current_user: str = Depends(get_user_from_token),
# ):
#     if not tasks_data:
#         raise HTTPException(status_code=422, detail="At least one task must be provided")

#     if not current_user:
#         raise HTTPException(status_code=404, detail="User not found")

#     updated_tasks = await task_service.update_tasks(tasks_data)
#     if updated_tasks is None:
#         raise HTTPException(status_code=404, detail="Task not found")

#     return updated_tasks


@task_router.delete("/{task_id}")
async def delete_task(
    task_id: int,
    task_service: TaskService = Depends(get_task_service),
    user_service: UserService = Depends(get_user_service),
    current_user: str = Depends(get_user_from_token),
):
    # current_user = await get_user_from_token()
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token or user not authenticated",
        )

    user = await user_service.get_user("username", current_user)
    task = await task_service.get_task("id", task_id)

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    if task.creator_id != user.id:
        raise HTTPException(
            status_code=403, detail="You do not have permission to delete this task"
        )

    await task_service.delete_task(task_id)

    # return {"message": "Task successfully deleted"}
    return Response(status_code=status.HTTP_204_NO_CONTENT)
