from pydantic import BaseModel


class UserBase(BaseModel):
    username: str


class UserCreate(UserBase):
    password: str


class UserReadSimple(UserBase):
    id: int

    class Config:
        from_attributes = True


class UserRead(UserReadSimple):
    projects: list["ProjectReadSimple"]
    owned_projects: list["ProjectReadSimple"]
    logs: list["TaskLogReadSimple"]


from schemas.project import ProjectReadSimple  # noqa
from schemas.tasklog import TaskLogReadSimple  # noqa
