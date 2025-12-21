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


class ProjectUpdate(BaseModel):
    title: str | None = None
    users_add: list[int] | None = None
    users_remove: list[int] | None = None


from schemas.user import UserReadSimple  # noqa
from schemas.task import TaskReadSimple  # noqa
