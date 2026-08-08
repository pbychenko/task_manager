from app.api.schemas.task import TaskCreate, TaskFromDB
from app.utils.unitofwork import IUnitOfWork


class TaskService:
    def __init__(self, uow: IUnitOfWork):
        self.uow = uow

    async def add_task(self, task: TaskCreate, creator_id: int) -> TaskFromDB:
        task_dict: dict = task.model_dump()  # подготовка данных для внесения в БД
        task_dict["creator_id"] = creator_id  # добавляем ID создателя задачи
        async with self.uow as uow:  # вход в контекст (если выбьет с ошибкой, то изменения откатятся) 
            task_from_db = await uow.task.add_one(task_dict)
            task_to_return = TaskFromDB.model_validate(task_from_db)  # обработка полученных данных из БД для их возврата - делаем модель пидантик
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

    async def update_tasks(self, param: str, value: str, data: dict) -> TaskFromDB | None:
        async with self.uow as uow:
            # result = 
            await uow.task.update_tasks(param, value, data)
            # return TaskFromDB.model_validate(task) if task else None