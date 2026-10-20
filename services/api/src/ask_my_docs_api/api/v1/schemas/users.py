from pydantic import BaseModel, ConfigDict


class UserBase(BaseModel):
    name: str | None


class UserRead(UserBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
