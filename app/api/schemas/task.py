from pydantic import BaseModel, ConfigDict, EmailStr, Field, model_validator


class TaskCreate(BaseModel):
    title: str
    description: str


class TaskUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    completed: bool | None = None  # Задали значение по-умолчанию False
    executor_id: int | None = None  # Добавляем поле executor_id для хранения идентификатора исполнителя задачи


class TaskBulkUpdate(TaskUpdate):
    id: int

    @model_validator(mode="after")
    def has_update_fields(self):
        if not self.model_dump(exclude_unset=True, exclude={"id"}):
            raise ValueError("At least one task field must be provided")
        return self


class TaskFromDB(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    description: str
    completed: bool = Field(default=False)  # Задали значение по-умолчанию False
    creator_id: int  # Добавляем поле creator_id для хранения идентификатора создателя задачи
    executor_id: (
        int | None
    )  # Добавляем поле executor_id для хранения идентификатора исполнителя задачи, может быть пустым
