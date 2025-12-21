from pydantic import BaseModel


class TaskBase(BaseModel):
    title: str
    description: str | None = None
    status: str


class TaskCreate(TaskBase):
    project_id: int


class TaskReadSimple(TaskBase):
    id: int

    class Config:
        from_attributes = True


class TaskRead(TaskReadSimple):
    project: "ProjectReadSimple"
    logs: list["TaskLogReadSimple"]


class TaskUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    status: str | None = None


from schemas.project import ProjectReadSimple  # noqa
from schemas.tasklog import TaskLogReadSimple  # noqa
