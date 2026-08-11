import datetime
from typing import List

from sqlalchemy import BigInteger, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base


class User(Base):  # обязательно наследуем все модели от нашей Base-метатаблицы
    __tablename__ = "users"  # Указываем как будет называться наша таблица в базе данных (пишется в ед. числе)

    id: Mapped[int] = mapped_column(
        BigInteger, primary_key=True, index=True
    )  # Строка  говорит, что наша колонка будет интом, но уточняет, что ещё и большим интом (актуально для ТГ-ботов), первичным ключом и индексироваться
    username: Mapped[str] = mapped_column(
        unique=True, index=True
    )  # Просто строка без доп.условий; если нужно дополнительные условия добавить, то mapped_column
    password: Mapped[str]  # Просто строка без доп.условий; если нужно дополнительные условия добавить, то mapped_column
    # created_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=func.now())  # просто для примера
    created_tasks: Mapped[List["Task"]] = relationship(
        back_populates="creator",
        foreign_keys="[Task.creator_id]",  # Указываем, какой ключ отслеживать
    )
    executed_tasks: Mapped[List["Task"]] = relationship(
        back_populates="executor",
        foreign_keys="[Task.executor_id]",  # Указываем, какой ключ отслеживать
    )


class Task(Base):  # обязательно наследуем все модели от нашей Base-метатаблицы
    __tablename__ = "tasks"  # Указываем как будет называться наша таблица в базе данных (пишется в ед. числе)

    id: Mapped[int] = mapped_column(
        BigInteger, primary_key=True, index=True
    )  # Строка  говорит, что наша колонка будет интом, но уточняет, что ещё и большим интом (актуально для ТГ-ботов), первичным ключом и индексироваться
    title: Mapped[str]  # Просто строка без доп.условий; если нужно дополнительные условия добавить, то mapped_column
    description: Mapped[
        str
    ]  # Просто строка без доп.условий; если нужно дополнительные условия добавить, то mapped_column
    completed: Mapped[bool] = mapped_column(default=False)  # Задали значение по-умолчанию False
    creator_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE")
    )  # Добавляем поле creator_id для хранения идентификатора создателя задачи
    executor_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL")
    )  # Добавляем поле executor_id для хранения идентификатора исполнителя задачи, может быть пустым

    creator: Mapped["User"] = relationship(
        back_populates="created_tasks",
        foreign_keys=[creator_id],  # Привязка к колонке creator_id
    )

    executor: Mapped["User"] = relationship(
        back_populates="executed_tasks",
        foreign_keys=[executor_id],  # Привязка к колонке executor_id
    )
