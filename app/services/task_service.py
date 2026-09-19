from app.api.schemas.task import TaskCreate, TaskFromDB, TaskUpdate, TaskUpdateStatus
from app.api.schemas.user import UserRead
from app.core.exceptions import ForbiddenError, InvalidTaskStatusError, NotFoundError
from app.utils.unitofwork import IUnitOfWork

def get_next_status(current_status: str) -> list[str]:
    status_transitions = {
        "to_do": ["to_do", "in_progress", "completed"],
        "in_progress": ["in_progress", "completed", "to_do", "review"],
        "completed": ["completed", "to_do", "in_progress"],
        "review": ["review", "in_progress", "completed"],
    }
    
    return status_transitions.get(current_status, [])

# def is_valid_priority(priority: str) -> bool:
#     priorities = ["low","medium", "high"]

#     return priority in priorities

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

            if current_user.role != 'admin' and current_user.id != project.owner_id:
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

            if current_user.role != 'admin' and project.owner_id != current_user.id:
                raise ForbiddenError("You do not have permission to update this task")

            # if "project_id" in data:
            #     project_id = data["project_id"]

            #     if project_id is not None:
            #         project = await uow.project.find_one("id", project_id)

            #         if project is None:
            #             raise NotFoundError(
            #                 f"Project {project_id} not found")

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

            if current_user.role =='admin':
                pass

            elif current_user.role == 'manager':
                project = await uow.project.find_one("id", task.project_id)                
               
                if project.owner_id != current_user.id:
                    raise ForbiddenError("You do not have permission to update the status of this task")

            elif task.executor_id != current_user.id:
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

    # async def update_task_status(self, task_id: int, status_data: dict) -> TaskFromDB:
    #     # status = status_data.get("status")
    #     # if  status_data.keys() != {"status"}:
    #     #     raise ValueError("Only 'status' field can be updated")

    #     status = status_data["status"] 

    #     async with self.uow as uow:
    #         task = await self.get_task("id", task_id)
            
    #         if not task:
    #             raise NotFoundError(f"Task {task_id} not found")
    
    #         old_status = task.status
    #         possible_statuses = get_next_status(old_status)
            
    #         if status not in possible_statuses:
    #             raise ValueError(f"Invalid status transition from {old_status} to {status}")
            
    #         updated_task = await uow.task.update_task("id", task_id, {"status": status})

    #         if updated_task is None:
    #             raise NotFoundError(f"Task {task_id} not found")

    #         task_to_return = TaskFromDB.model_validate(updated_task)
    #         await uow.commit()  # это самый важный кусок кода, до этого коммита можно записать данные в 50 моделей, но если кто-то вылетит с ошибкой, все изменения откатятся! Если код дошёл сюда, то все прошло окей!

    #         return task_to_return

    # async def update_task_priority(self, task_id: int, priority: str) -> TaskFromDB:  
    #         async with self.uow as uow:
    #             task = await self.get_task("id", task_id)
                
    #             if not task:
    #                 raise NotFoundError(f"Task {task_id} not found")
        
    #             old_priority = task.priority
    #             possible_priorities = get_next_priority(old_priority)
                
    #             if priority not in possible_priorities:
    #                 raise ValueError(f"Invalid priority transition from {old_priority} to {priority}")
                
    #             updated_task = await uow.task.update_task("id", task_id, {"priority": priority})
    
    #             if updated_task is None:
    #                 raise NotFoundError(f"Task {task_id} not found")
    
    #             task_to_return = TaskFromDB.model_validate(updated_task)
    #             await uow.commit()  # это самый важный кусок кода, до этого коммита можно записать данные в 50 моделей, но если кто-то вылетит с ошибкой, все изменения откатятся! Если код дошёл сюда, то все прошло окей!
    
    #             return task_to_return

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

            if current_user.role != 'admin' and project.owner_id != current_user.id:
                raise ForbiddenError("You do not have permission to delete this task")

            await uow.task.delete_one(id)
            await uow.commit()
