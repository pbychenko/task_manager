from app.api.schemas.task import TaskBulkUpdate, TaskCreate, TaskFromDB, TaskUpdate
from app.utils.unitofwork import IUnitOfWork


class TaskService:
    def __init__(self, uow: IUnitOfWork):
        self.uow = uow

    async def add_task(self, task: TaskCreate, creator_id: int) -> TaskFromDB:
        task_dict: dict = task.model_dump()  # подготовка данных для внесения в БД
        task_dict["creator_id"] = creator_id  # добавляем ID создателя задачиatement
        async with self.uow as uow:  # вход в контекст (если выбьет с ошибкой, то изменения откатятся)
            task_from_db = await uow.task.add_one(task_dict)
            task_to_return = TaskFromDB.model_validate(
                task_from_db
            )  # обработка полученных данных из БД для их возврата - делаем модель пидантик
            await uow.commit()  # это самый важный кусок кода, до этого коммита можно записать данные в 50 моделей, но если кто-то вылетит с ошибкой, все изменения откатятся! Если код дошёл сюда, то все прошло окей!
            return task_to_return

    async def update_task(self, task_id: int, task_data: dict) -> TaskFromDB | None:
        async with self.uow as uow:
            updated_task = await uow.task.update_task("id", task_id, task_data)
            if updated_task is None:
                return None

            task_to_return = TaskFromDB.model_validate(updated_task)
            if not task_to_return:
                return None

            await uow.commit()  # это самый важный кусок кода, до этого коммита можно записать данные в 50 моделей, но если кто-то вылетит с ошибкой, все изменения откатятся! Если код дошёл сюда, то все прошло окей!
            return task_to_return

    # async def update_tasks(self, tasks_data: list[TaskBulkUpdate]) -> list[TaskFromDB] | None:
    #     """Update several tasks atomically and return their updated versions."""
    #     updated_tasks: list[TaskFromDB] = []

    #     async with self.uow as uow:
    #         for task_data in tasks_data:
    #             data = task_data.model_dump(exclude_unset=True, exclude={"id"})
    #             updated_task = await uow.task.update_task("id", task_data.id, data)

    #             if updated_task is None:
    #                 return None

    #             updated_tasks.append(TaskFromDB.model_validate(updated_task))

    #         await uow.commit()
    #         return updated_tasks

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
            return deleted_count
        # это самый важный кусок кода, до этого коммита можно записать данные в 50 моделей, но если кто-то вылетит с ошибкой, все изменения откатятся! Если код дошёл сюда, то все прошло окей!
        # return deleted_task.id if deleted_task else None
