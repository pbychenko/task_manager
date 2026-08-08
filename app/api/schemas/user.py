from pydantic import BaseModel,Field, EmailStr, ConfigDict

class UserBase(BaseModel):
    username: str
    password: str

class UserCreate(BaseModel):
    username: str
    # email: EmailStr = None
    password: str


class UserFromDB(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    username: str
    # email: str
    password: str
