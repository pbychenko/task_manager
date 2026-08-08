from pydantic import BaseModel,Field, EmailStr, ConfigDict


class TaskCreate(BaseModel):
    title: str
    description: str

class TaskUpdate(BaseModel):
    title: str
    description: str
    completed: bool = Field(default=False)  # Задали значение по-умолчанию False
    executor_id: int  # Добавляем поле executor_id для хранения идентификатора исполнителя задачи


class TaskFromDB(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    title: str
    description: str
    completed: bool = Field(default=False)  # Задали значение по-умолчанию False
    creator_id: int  # Добавляем поле creator_id для хранения идентификатора создателя задачи
    executor_id: int  # Добавляем поле executor_id для хранения идентификатора исполнителя задачи