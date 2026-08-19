from app.api.schemas.task import TaskCreate, TaskFromDB, TaskUpdate
from app.utils.unitofwork import IUnitOfWork
from app.core.exceptions import NotFoundError


class TaskService:
    def __init__(self, uow: IUnitOfWork):
        self.uow = uow

    async def add_task(self, task: TaskCreate, creator_id: int) -> TaskFromDB:
        task_dict: dict = task.model_dump()
        task_dict["creator_id"] = creator_id 
        async with self.uow as uow: 
            task_from_db = await uow.task.add_one(task_dict)
            task_to_return = TaskFromDB.model_validate(
                task_from_db
            ) 
            await uow.commit()

            return task_to_return
        

    async def update_task(self, task_id: int, task_data: TaskUpdate) -> TaskFromDB | None:
        data: dict = task_data.model_dump(exclude_unset=True)
        async with self.uow as uow:
            updated_task = await uow.task.update_task("id", task_id, data)
            if updated_task is None:
                raise NotFoundError(f"Task {task_id} not found")

            task_to_return = TaskFromDB.model_validate(updated_task)

            await uow.commit()  # это самый важный кусок кода, до этого коммита можно записать данные в 50 моделей, но если кто-то вылетит с ошибкой, все изменения откатятся! Если код дошёл сюда, то все прошло окей!
            return task_to_return

    async def get_tasks(self) -> list[TaskFromDB]:
        async with self.uow as uow:
            tasks: list = await uow.task.find_all()

            return [TaskFromDB.model_validate(task) for task in tasks]

    async def get_task(self, param: str, value: str) -> TaskFromDB | None:
        async with self.uow as uow:
            task = await uow.task.find_one(param, value)
            return TaskFromDB.model_validate(task) if task else None

    async def delete_task(self, id: int, user_id: int) -> None:
        task = await self.get_task("id", id)
        
        if not task:
            raise NotFoundError(f"Task {id} not found")

        print(f"Task creator_id: {task.creator_id}, User ID: {user_id}")  # Debug print statement
        if task.creator_id != user_id:
            raise PermissionError("You do not have permission to delete this task")
        
        async with self.uow as uow:
            deleted_count = await uow.task.delete_one(id)
            await uow.commit()

            return deleted_count
