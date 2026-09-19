from typing import List

from sqlalchemy import BigInteger, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base
import sqlalchemy as sa



class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, index=True)
    username: Mapped[str] = mapped_column(unique=True, index=True)
    password: Mapped[str]
    role: Mapped[str] = mapped_column(
        sa.Enum("user", "manager", "admin", name="user_role"),
        server_default="user",
        nullable=False,
    )
    created_tasks: Mapped[List["Task"]] = relationship(
        back_populates="creator",
        foreign_keys="[Task.creator_id]", 
    )
    executed_tasks: Mapped[List["Task"]] = relationship(
        back_populates="executor",
        foreign_keys="[Task.executor_id]", 
    )
    owned_projects: Mapped[List["Project"]] = relationship(
        back_populates="owner",
        foreign_keys="[Project.owner_id]",
    )

class Project(Base):
    __tablename__ = "projects"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, index=True)
    name: Mapped[str]
    description: Mapped[str]
    owner_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), index=True)
    owner: Mapped["User | None"] = relationship(back_populates="owned_projects")

    tasks: Mapped[List["Task"]] = relationship(
        back_populates="project",
        foreign_keys="[Task.project_id]"
    )


class Task(Base):
    __tablename__ = "tasks"  #
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, index=True)
    title: Mapped[str]
    description: Mapped[str]
    # completed: Mapped[bool] = mapped_column(server_default=sa.text("false"))
    status: Mapped[str] = mapped_column(
        sa.Enum("to_do", "in_progress", "review", "completed", name="task_status"),
        server_default="to_do",
    )
    priority: Mapped[str] = mapped_column(
        sa.Enum("low", "medium", "high", name="task_priority"),
        server_default="medium",
    )
    project_id: Mapped[int] = mapped_column(
        ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True
    )
    creator_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    executor_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), index=True
    )

    creator: Mapped["User"] = relationship(
        back_populates="created_tasks",
        foreign_keys=[creator_id],
    )

    executor: Mapped["User"] = relationship(
        back_populates="executed_tasks",
        foreign_keys=[executor_id],
    )

    project: Mapped["Project"] = relationship(
        back_populates="tasks",
        foreign_keys=[project_id],
    )
