from app.db.models import Project, Task
from app.api.schemas.user import UserRead

class ProjectPolicy:
    @staticmethod
    def can_manage(user: UserRead, project: Project) -> bool:
        return user.role == "admin" or (
            user.role == "manager" and project.owner_id == user.id
        )


class TaskPolicy:
    @staticmethod
    def can_manage(user: UserRead, project: Project) -> bool:
        return ProjectPolicy.can_manage(user, project)

    @staticmethod
    def can_transition_status(user: UserRead, task: Task, project: Project) -> bool:
        if user.role == 'admin':
            return True
        
        if user.role == 'manager':
            return project.owner_id == user.id
        
        return task.executor_id == user.id