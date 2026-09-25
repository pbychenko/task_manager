from app.api.schemas.project import ProjectCreate, ProjectFromDB, ProjectUpdate
from app.api.schemas.user import UserRead

from app.core.exceptions import ForbiddenError, NotFoundError
from app.utils.unitofwork import IUnitOfWork
from app.core.policies import ProjectPolicy

class ProjectService:
    def __init__(self, uow: IUnitOfWork):
        self.uow = uow

    async def add_project(self, project: ProjectCreate, owner_id: int) -> ProjectFromDB:
        project_dict: dict = project.model_dump()
        project_dict["owner_id"] = owner_id

        async with self.uow as uow:
            project_from_db = await uow.project.add_one(project_dict)
            project_to_return = ProjectFromDB.model_validate(project_from_db)
            await uow.commit()

            return project_to_return

    async def update_project(self, project_id: int, project_data: ProjectUpdate, current_user: UserRead) -> ProjectFromDB:
        data: dict = project_data.model_dump(exclude_unset=True)

        async with self.uow as uow:
            project = await uow.project.find_one("id", project_id, for_update=True)

            if project is None:
                raise NotFoundError(f"Project {project_id} not found")      

            if not ProjectPolicy.can_manage(current_user, project):
                raise ForbiddenError("You do not have permission to update this project")

            updated_project = await uow.project.update_project("id", project_id, data)

            if updated_project is None:
                raise NotFoundError(f"Project {project_id} not found")
            

            project_to_return = ProjectFromDB.model_validate(updated_project)
            await uow.commit() 

            return project_to_return

    async def get_projects(self, skip, limit) -> list[ProjectFromDB]:
        async with self.uow as uow:
            projects: list = await uow.project.find_all(skip, limit)

            return [ProjectFromDB.model_validate(project) for project in projects]

    async def get_project(self, param: str, value: str) -> ProjectFromDB:
        async with self.uow as uow:
            project = await uow.project.find_one(param, value)

            if not project:
                raise NotFoundError(f"Project with {param}={value} not found")

            return ProjectFromDB.model_validate(project)

    async def delete_project(self, id: int, current_user: UserRead) -> None:
        async with self.uow as uow:
            project = await uow.project.find_one("id", id)

            if not project:
                raise NotFoundError(f"Project {id} not found")

            
            if not ProjectPolicy.can_manage(current_user, project):
                raise ForbiddenError("You do not have permission to delete this project")

            await uow.project.delete_one(id)
            await uow.commit()
