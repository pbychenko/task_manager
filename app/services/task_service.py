from app.api.schemas.task import TaskCreate, TaskFromDB, TaskUpdate, TaskUpdateStatus
from app.api.schemas.user import UserRead
from app.core.exceptions import ForbiddenError, InvalidTaskStatusError, NotFoundError
from app.utils.unitofwork import IUnitOfWork
from app.core.policies import TaskPolicy

def get_next_status(current_status: str) -> list[str]:
    status_transitions = {
        "to_do": ["to_do", "in_progress", "completed"],
        "in_progress": ["in_progress", "completed", "to_do", "review"],
        "completed": ["completed", "to_do", "in_progress"],
        "review": ["review", "in_progress", "completed"],
    }
    
    return status_transitions.get(current_status, [])

class TaskService:
    def __init__(self, uow: IUnitOfWork):
        self.uow = uow

    async def add_task(self, task: TaskCreate, current_user: UserRead) -> TaskFromDB:
        task_dict: dict = task.model_dump()
        task_dict["creator_id"] = current_user.id

        async with self.uow as uow:
            project = await uow.project.find_one("id", task.project_id)

            if not project:
                raise NotFoundError(f"Project {task.project_id} not found")

            if not TaskPolicy.can_manage(current_user, project):
                raise ForbiddenError("You do not have permission to create a task in this project")

            task_from_db = await uow.task.add_one(task_dict)
            task_to_return = TaskFromDB.model_validate(task_from_db)
            await uow.commit()

            return task_to_return

    async def update_task(self, task_id: int, task_data: TaskUpdate, current_user: UserRead) -> TaskFromDB:
        data: dict = task_data.model_dump(exclude_unset=True)        

        async with self.uow as uow:           
            task = await uow.task.find_one("id", task_id, for_update=True)

            if task is None:
                raise NotFoundError(f"Task {task_id} not found")

            project = await uow.project.find_one("id", task.project_id)

            if not TaskPolicy.can_manage(current_user, project):
                raise ForbiddenError("You do not have permission to update this task")

            if "status" in data:
                new_status = data["status"]

                possible_statuses = get_next_status(task.status)
                
                if new_status not in possible_statuses:
                    raise InvalidTaskStatusError(f"Invalid status transition from {task.status} to {new_status}")
                
            updated_task = await uow.task.update_task("id", task_id, data)

            if updated_task is None:
                raise NotFoundError(f"Task {task_id} not found")

            task_to_return = TaskFromDB.model_validate(updated_task)
            await uow.commit()  

            return task_to_return

    async def update_task_status(self, task_id: int, task_data: TaskUpdateStatus, current_user: UserRead) -> TaskFromDB:
        data: dict = task_data.model_dump(exclude_unset=True)

        async with self.uow as uow:
            task = await uow.task.find_one("id", task_id, for_update=True)

            if task is None:
                raise NotFoundError(f"Task {task_id} not found")

            project = await uow.project.find_one("id", task.project_id)
            if not TaskPolicy.can_transition_status(current_user, task, project):
                raise ForbiddenError("You do not have permission to update the status of this task")
            
            possible_statuses = get_next_status(task.status)

            new_status = data.get("status")
            if new_status not in possible_statuses:
                raise InvalidTaskStatusError(f"Invalid status transition from {task.status} to {new_status}")

            updated_task = await uow.task.update_task("id", task_id, data)

            if updated_task is None:
                raise NotFoundError(f"Task {task_id} not found")

            task_to_return = TaskFromDB.model_validate(updated_task)
            await uow.commit()

            return task_to_return

    async def get_tasks(self, skip, limit) -> list[TaskFromDB]:
        async with self.uow as uow:
            tasks: list = await uow.task.find_all(skip, limit)

            return [TaskFromDB.model_validate(task) for task in tasks]

    async def get_task(self, param: str, value: str) -> TaskFromDB:
        async with self.uow as uow:
            task = await uow.task.find_one(param, value)
            
            if not task:
                raise NotFoundError(f"Task with {param}={value} not found")

            return TaskFromDB.model_validate(task)

    async def delete_task(self, id: int, current_user: UserRead) -> None:
        async with self.uow as uow:
            task = await uow.task.find_one("id", id)

            if not task:
                raise NotFoundError(f"Task {id} not found")

            project = await uow.project.find_one("id", task.project_id)

            if not TaskPolicy.can_manage(current_user, project):
                raise ForbiddenError("You do not have permission to delete this task")

            await uow.task.delete_one(id)
            await uow.commit()
