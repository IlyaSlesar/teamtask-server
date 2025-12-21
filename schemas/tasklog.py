from pydantic import BaseModel


class TaskLogReadSimple(BaseModel):
    id: int
    task_id: int
    user_id: int
    action: str


class TaskLogRead(BaseModel):
    id: int
    task: "TaskReadSimple"
    user: "UserReadSimple"
    action: str


from schemas.task import TaskReadSimple  # noqa
from schemas.user import UserReadSimple  # noqa
