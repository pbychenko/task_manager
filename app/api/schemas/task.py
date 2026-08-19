from pydantic import BaseModel, ConfigDict, EmailStr, Field, model_validator


class TaskCreate(BaseModel):
    title: str
    description: str


class TaskUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    completed: bool | None = None 
    executor_id: int | None = None 

    @model_validator(mode="after")
    def has_update_fields(self):
        if not self.model_dump(exclude_unset=True):
            raise ValueError("At least one task field must be provided")
        return self


class TaskFromDB(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    description: str
    completed: bool = Field(default=False)  # Задали значение по-умолчанию False
    creator_id: int
    executor_id: int | None