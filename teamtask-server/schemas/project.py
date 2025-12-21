from pydantic import BaseModel


class ProjectBase(BaseModel):
    title: str


class ProjectCreate(ProjectBase):
    pass


class ProjectReadSimple(ProjectBase):
    id: int

    class Config:
        from_attributes = True


class ProjectRead(ProjectReadSimple):
    owner: "UserReadSimple"
    users: list["UserReadSimple"]
    tasks: list["TaskReadSimple"]


from schemas.user import UserReadSimple  # noqa
from schemas.task import TaskReadSimple  # noqa
