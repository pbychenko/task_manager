from pydantic import BaseModel, ConfigDict, model_validator


class ProjectCreate(BaseModel):
    name: str
    description: str


class ProjectUpdate(BaseModel):
    name: str = None
    description: str = None

    @model_validator(mode="after")
    def has_update_fields(self):
        if not self.model_dump(exclude_unset=True):
            raise ValueError("At least one project field must be provided")
        return self


class ProjectFromDB(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: str
    owner_id: int | None
