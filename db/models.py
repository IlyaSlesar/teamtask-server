from sqlalchemy import (
    String,
    Text,
    DateTime,
    ForeignKey,
    Table,
    Column
)
from sqlalchemy.sql import func
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship
)

from db.base import Base


user_project = Table(
    "users_teams",
    Base.metadata,
    Column("user_id", ForeignKey("users.id"), primary_key=True),
    Column("project_id", ForeignKey("projects.id"), primary_key=True),
    Column(
        "timestamp",
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
)


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        unique=True
    )
    password_hash: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )

    projects: Mapped[list["Project"]] = relationship(
        secondary=user_project,
        back_populates="users"
    )
    owned_projects: Mapped[list["Project"]] = relationship(
        back_populates="owner",
        cascade="all, delete-orphan"
    )
    logs: Mapped[list["TaskLog"]] = relationship(
        back_populates="user",
        cascade="all"
    )


class Project(Base):
    __tablename__ = "projects"

    id: Mapped[int] = mapped_column(primary_key=True)
    owner_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False
    )
    title: Mapped[str] = mapped_column(
        String(30),
        nullable=False
    )

    users: Mapped[list[User]] = relationship(
        secondary=user_project,
        back_populates="projects"
    )
    owner: Mapped[User] = relationship(
        back_populates="owned_projects",
        foreign_keys=[owner_id]
    )
    tasks: Mapped[list["Task"]] = relationship(
        back_populates="project",
        cascade="all, delete-orphan"
    )


class Task(Base):
    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(primary_key=True)
    project_id: Mapped[int] = mapped_column(
        ForeignKey("projects.id"),
        nullable=False
    )
    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )
    description: Mapped[str] = mapped_column(
        Text,
        nullable=True
    )
    status: Mapped[str] = mapped_column(String(30), nullable=False)

    project: Mapped[Project] = relationship(
        back_populates="tasks",
        foreign_keys=[project_id]
    )
    logs: Mapped[list["TaskLog"]] = relationship(
        back_populates="task",
        cascade="all, delete-orphan"
    )


class TaskLog(Base):
    __tablename__ = "tasklogs"

    id: Mapped[int] = mapped_column(primary_key=True)
    task_id: Mapped[int] = mapped_column(ForeignKey("tasks.id"))
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    action: Mapped[str] = mapped_column(String(255), nullable=False)

    task: Mapped[Task] = relationship(
        back_populates="logs",
        foreign_keys=[task_id]
    )
    user: Mapped[User] = relationship(
        back_populates="logs",
        foreign_keys=[user_id]
    )
