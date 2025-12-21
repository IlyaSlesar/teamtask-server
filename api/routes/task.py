from typing import Annotated

from fastapi import (
    APIRouter,
    Path,
    Depends,
    Response,
    HTTPException,
    status
)
from sqlalchemy import select, or_
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from db.session import get_db
from db.models import User, Task, Project
from schemas.task import TaskRead, TaskUpdate
from api.deps import get_current_user, log_task_modification


PREFIX_URL = "/task"
router = APIRouter(
    prefix=PREFIX_URL
)


async def get_task_by_id(
    session: AsyncSession,
    user_id: int,
    task_id: int
):
    return (await session.execute(
        select(Task)
        .join(Project, Task.project_id == Project.id)
        .where(
            Task.id == task_id,
            or_(
                Project.owner_id == user_id,
                Project.users.any(User.id == user_id)
            )
        )
        .options(
            selectinload(Task.project),
            selectinload(Task.logs)
        )
    )).scalars().one_or_none()


@router.get("/{id}", response_model=TaskRead)
async def read_task(
    id: Annotated[int, Path(title="task ID")],
    session: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)]
):
    task = await get_task_by_id(session, current_user.id, id)
    if task is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND)
    return task


@router.patch("/{id}", response_model=TaskRead)
async def update_task(
    id: Annotated[int, Path(title="task ID")],
    session: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
    update: TaskUpdate
):
    task = await get_task_by_id(session, current_user.id, id)
    if task is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND)
    updated_fields = []
    for field_name, field_value in update:
        if field_value is not None:
            setattr(task, field_name, field_value)
            updated_fields.append(field_name)
    await log_task_modification(
        session,
        current_user.id,
        task.id,
        f'Updated fields: {", ".join(updated_fields)}'
    )
    await session.commit()
    return (await session.execute(
        select(Task)
        .where(Task.id == id)
        .options(
            selectinload(Task.project),
            selectinload(Task.logs)
        )
    )).scalars().one_or_none()


@router.delete("/{id}")
async def delete_task(
    id: Annotated[int, Path(title="task ID")],
    session: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)]
):
    task = await get_task_by_id(session, current_user.id, id)
    if task is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND)
    if task.project.owner_id != current_user.id:
        raise HTTPException(status.HTTP_403_FORBIDDEN)
    await session.delete(task)
    await session.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
