from fastapi import APIRouter, Depends, status, HTTPException
from fastapi.responses import JSONResponse

from app.api.endpoints.users import get_user_service
from app.api.schemas.task import TaskFromDB, TaskCreate, TaskUpdate
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
        return await task_service.add_task(task_data, creator_id=user.id)
        
    # # Если пользователь не найден, возвращаем ошибку
    raise HTTPException(
        status_code=404,
        detail="User not found"
    )

@task_router.put("/update/{task_id}", response_model=TaskFromDB | None)
async def update_task(task_id: int, task_data: TaskUpdate, task_service: TaskService = Depends(get_task_service),
                    current_user: str = Depends(get_user_from_token)):
    print(f"Updating task with ID: {task_id} and data: {task_data}")

      # Debug print statement
    if current_user:
        return await task_service.update_task(task_id, task_data)

    raise HTTPException(
            status_code=404,
            detail="Task not found"
        )

@task_router.delete("/delete/{task_id}")
async def delete_task(task_id: int, task_service: TaskService = Depends(get_task_service), current_user: str = Depends(get_user_from_token)):
    # try:
        # Пытаемся удалить запись и получить подтверждение
        if current_user:
            deleted_count = await task_service.delete_task(task_id)
            if deleted_count == 0:
                raise HTTPException(
                    status_code=404,
                    detail="Task anot found"
                )
            return {"message": "Task successfully deleted"}
        raise HTTPException(
                    status_code=404,
                    detail="User not found"
                )
        
    # except Exception as e:
    #     # Логируем ошибку и возвращаем сообщение об ошибке
    #     print(f"Error deleting task: {e}")
    #     raise HTTPException(
    #         status_code=500,
    #         detail="An error occurred while trying to delete the task"
    #     )