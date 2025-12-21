from sqlalchemy.orm import declarative_base


Base = declarative_base()

from db.models import (  # noqa
    User,
    Project,
    Task,
    TaskLog
)
