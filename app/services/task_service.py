from app.api.schemas.task import TaskCreate, TaskFromDB, TaskUpdate
from app.utils.unitofwork import IUnitOfWork


class TaskService:
    def __init__(self, uow: IUnitOfWork):
        self.uow = uow

    async def add_task(self, task: TaskCreate, creator_id: int) -> TaskFromDB:
        task_dict: dict = task.model_dump()  # подготовка данных для внесения в БД
        task_dict["creator_id"] = creator_id  # добавляем ID создателя задачи
        # task_dict["executor_id"] = executor_id  # добавляем ID исполнителя задачи
        print(f"Task dict before adding to DB: {task_dict}")  # Debug print statement
        async with self.uow as uow:  # вход в контекст (если выбьет с ошибкой, то изменения откатятся) 
            task_from_db = await uow.task.add_one(task_dict)
            task_to_return = TaskFromDB.model_validate(task_from_db)  # обработка полученных данных из БД для их возврата - делаем модель пидантик
            await uow.commit()  # это самый важный кусок кода, до этого коммита можно записать данные в 50 моделей, но если кто-то вылетит с ошибкой, все изменения откатятся! Если код дошёл сюда, то все прошло окей! 
            return task_to_return

        
    async def update_task(self, task_id: int, task_data: TaskUpdate) -> TaskFromDB | None:
        data = task_data.model_dump(exclude_unset=True)
        print(data)
        async with self.uow as uow:
            updated_task = await uow.task.update_task("id", task_id, data)
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

    async def delete_task(self, id: int) -> None:
        async with self.uow as uow:
            deleted_count = await uow.task.delete_one(id)
            await uow.commit() 
            return  deleted_count
        # это самый важный кусок кода, до этого коммита можно записать данные в 50 моделей, но если кто-то вылетит с ошибкой, все изменения откатятся! Если код дошёл сюда, то все прошло окей! 
            # return deleted_task.id if deleted_task else None