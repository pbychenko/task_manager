from fastapi import APIRouter, Depends, Response, status

from app.api.schemas.project import ProjectCreate, ProjectUpdate, ProjectFromDB
from app.api.schemas.user import UserRead
from app.core.security import require_role
from app.services.project_service import ProjectService
from app.services.user_service import UserService
from app.utils.unitofwork import IUnitOfWork, UnitOfWork
from app.core.role_levels import RoleLevel


project_router = APIRouter(prefix="/projects", tags=["projects"])

async def get_project_service(uow: IUnitOfWork = Depends(UnitOfWork)) -> ProjectService:
    return ProjectService(uow)


async def get_user_service(uow: IUnitOfWork = Depends(UnitOfWork)) -> UserService:
    return UserService(uow)


@project_router.get("/{project_id}", response_model=ProjectFromDB)
async def get_project_by_id(
    project_id: int,
    _: UserRead = Depends(require_role(RoleLevel.MANAGER)),
    project_service: ProjectService = Depends(get_project_service),
):
    return await project_service.get_project("id", project_id)


@project_router.get("/", response_model=list[ProjectFromDB])
async def get_all_projects(
    skip: int = 0,
    limit: int = 10,
    _: UserRead = Depends(require_role(RoleLevel.MANAGER)),
    project_service: ProjectService = Depends(get_project_service),
):
    return await project_service.get_projects(skip, limit)


@project_router.post("/", response_model=ProjectFromDB)
async def create_project(
    project_data: ProjectCreate,
    project_service: ProjectService = Depends(get_project_service),
    current_user: UserRead = Depends(require_role(RoleLevel.MANAGER)),
):
    return await project_service.add_project(project_data, owner_id=current_user.id)


@project_router.patch("/{project_id}", response_model=ProjectFromDB)
async def update_project(
    project_id: int,
    project_data: ProjectUpdate,
    project_service: ProjectService = Depends(get_project_service),
    current_user: UserRead = Depends(require_role(RoleLevel.MANAGER)),
):

    return await project_service.update_project(project_id, project_data, current_user=current_user)


@project_router.delete("/{project_id}")
async def delete_project(
    project_id: int,
    project_service: ProjectService = Depends(get_project_service),
    current_user: UserRead = Depends(require_role(RoleLevel.MANAGER)),
):

    await project_service.delete_project(project_id, current_user)

    return Response(status_code=status.HTTP_204_NO_CONTENT)
