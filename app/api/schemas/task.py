from pydantic import BaseModel, ConfigDict, EmailStr, Field, model_validator
from typing import Literal



class TaskCreate(BaseModel):
    title: str
    description: str
    project_id: int
    # status: Literal["to_do", "in_progress", "review", "completed"] = "to_do"
    priority: Literal["high", "medium", "low"] = "medium"


class TaskUpdate(BaseModel):
    title: str = None
    description: str = None
    status: Literal["to_do", "in_progress", "review", "completed"] = "to_do"
    priority: Literal["high", "medium", "low"] = "medium"
    executor_id: int | None = None
    project_id: int | None = None

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
    status: Literal["to_do", "in_progress", "review", "completed"] = "to_do"
    priority: Literal["high", "medium", "low"] = "medium"
    creator_id: int
    executor_id: int | None
    project_id: int | None
