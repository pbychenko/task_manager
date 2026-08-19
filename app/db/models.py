from typing import List

from sqlalchemy import BigInteger, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(
        BigInteger, primary_key=True, index=True
    )  
    username: Mapped[str] = mapped_column(
        unique=True, index=True
    )  
    password: Mapped[
        str
    ] 
    created_tasks: Mapped[List["Task"]] = relationship(
        back_populates="creator",
        foreign_keys="[Task.creator_id]",  # Указываем, какой ключ отслеживать
    )
    executed_tasks: Mapped[List["Task"]] = relationship(
        back_populates="executor",
        foreign_keys="[Task.executor_id]",  # Указываем, какой ключ отслеживать
    )


class Task(Base):  
    __tablename__ = "tasks"  #
    id: Mapped[int] = mapped_column(
        BigInteger, primary_key=True, index=True
    )  
    title: Mapped[
        str
    ]  
    description: Mapped[
        str
    ]  
    completed: Mapped[bool] = mapped_column(
        default=False
    )  
    creator_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE")
    )  
    executor_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL")
    )  

    creator: Mapped["User"] = relationship(
        back_populates="created_tasks",
        foreign_keys=[creator_id],  
    )

    executor: Mapped["User"] = relationship(
        back_populates="executed_tasks",
        foreign_keys=[executor_id],  
    )
