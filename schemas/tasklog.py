from datetime import datetime

from pydantic import BaseModel


class TaskLogRead(BaseModel):
    id: int
    task_id: int
    user_id: int
    action: str
    timestamp: datetime


from schemas.task import TaskReadSimple  # noqa
from schemas.user import UserReadSimple  # noqa
