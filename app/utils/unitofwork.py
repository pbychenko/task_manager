from abc import ABC, abstractmethod

from app.db.database import async_session_maker
from app.repositories.task_repository import TaskRepository
from app.repositories.user_repository import UserRepository
from typing import Self


class IUnitOfWork(ABC):
    user: UserRepository
    task: TaskRepository

    @abstractmethod
    def __init__(self): ...

    @abstractmethod
    async def __aenter__(self) -> Self: ...

    @abstractmethod
    async def __aexit__(self, *args): ...

    @abstractmethod
    async def commit(self): ...

    @abstractmethod
    async def rollback(self): ...


class UnitOfWork(IUnitOfWork):
    def __init__(self):
        self.session_factory = async_session_maker

    async def __aenter__(self):
        self.session = self.session_factory()

        self.user = UserRepository(self.session)
        self.task = TaskRepository(self.session)
        return self

    async def __aexit__(self, *args):
        await self.rollback()
        await self.session.close()
        self.session = None  # спасибо за наводку Дмитрию Морозову, очищаем сессию после выхода из контекста

    async def commit(self):
        await self.session.commit()

    async def rollback(self):
        await self.session.rollback()
