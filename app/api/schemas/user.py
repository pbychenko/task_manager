from pydantic import BaseModel, ConfigDict, EmailStr, Field
from typing import Literal


class UserCreate(BaseModel):
    username: str = Field(min_length=2)
    # email: EmailStr = None
    password: str = Field(min_length=4)
    



class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    role: Literal["user", "manager", "admin"] = "user"
    # email: EmailStr = None
    # password: str


class UserFromDB(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    # email: str
    password: str
    role: Literal["user", "manager", "admin"] = "user"

class UserRoleUpdate(BaseModel):
    role: Literal["user", "manager", "admin"]
