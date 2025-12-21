from typing import Sequence, Annotated

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
    Path,
    Response
)
from sqlalchemy import (
    select,
    or_
)
from sqlalchemy.orm import (
    selectinload
)
from sqlalchemy.ext.asyncio import (
    AsyncSession
)
from sqlalchemy.exc import (
    IntegrityError
)

from db.session import get_db
from db.models import User, Project, Task
from schemas.project import (
    ProjectReadSimple,
    ProjectRead,
    ProjectCreate,
    ProjectUpdate
)
from schemas.task import TaskReadSimple, TaskBase
from api.deps import get_current_user, log_task_modification


PREFIX_URL = "/project"
router = APIRouter(
    prefix=PREFIX_URL
)


async def get_project_by_id(
    session: AsyncSession,
    project_id: int,
    user_id: int
) -> Project | None:
    return (await session.execute(
        select(Project)
        .where(
            Project.id == project_id,
            or_(
                Project.owner_id == user_id,
                Project.users.any(User.id == user_id)
            )
        )
        .options(
            selectinload(Project.users),
            selectinload(Project.owner),
            selectinload(Project.tasks)
        )
    )).scalars().one_or_none()


@router.get("/", response_model=Sequence[ProjectReadSimple])
async def read_projects(
    session: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)]
):
    return (await session.execute(
        select(Project)
        .where(
            or_(
                Project.owner_id == current_user.id,
                Project.users.any(User.id == current_user.id)
            )
        )
    )).scalars().all()


@router.get("/{id}", response_model=ProjectRead)
async def read_project(
    id: Annotated[int, Path(title="project ID")],
    session: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)]
):
    project = await get_project_by_id(session, id, current_user.id)
    if project is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND)
    return project


@router.post("/", response_model=ProjectReadSimple)
async def create_project(
    session: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
    project: ProjectCreate
):
    db_project = Project(**project.model_dump(), owner_id=current_user.id)
    session.add(db_project)
    try:
        await session.commit()
    except IntegrityError:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST
        )

    await session.refresh(db_project)
    return db_project


@router.post("/{id}", response_model=TaskReadSimple)
async def create_task_in_project(
    id: Annotated[int, Path(title="project ID")],
    session: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
    task: TaskBase
):
    project = await get_project_by_id(session, id, current_user.id)
    if project is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND)
    db_task = Task(**task.model_dump(), project=project)
    session.add(db_task)
    user_id = current_user.id
    await session.commit()
    await session.refresh(db_task)
    await log_task_modification(
        session,
        user_id,
        db_task.id,
        'Created a task'
    )
    await session.commit()
    return db_task


@router.patch("/{id}", response_model=ProjectRead)
async def update_project(
    id: Annotated[int, Path(title="project ID")],
    session: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
    update: ProjectUpdate
):
    project = await get_project_by_id(session, id, current_user.id)
    if project is None or project.owner_id != current_user.id:
        raise HTTPException(status.HTTP_404_NOT_FOUND)
    if update.title is not None:
        project.title = update.title
    if update.users_add is not None:
        users_to_add = [
            await session.get(User, user_id) for user_id in update.users_add
        ]
        for user in users_to_add:
            if user not in project.users:
                project.users.append(user)
    if update.users_remove is not None:
        users_to_remove = [
            await session.get(User, user_id) for user_id in update.users_remove
        ]
        for user in users_to_remove:
            if user in project.users:
                project.users.remove(user)
    await session.commit()
    return (await session.execute(
        select(Project)
        .where(Project.id == id)
        .options(
            selectinload(Project.owner),
            selectinload(Project.users),
            selectinload(Project.tasks)
        )
    )).scalars().one_or_none()


@router.delete("/{id}")
async def delete_project(
    id: Annotated[int, Path(title="project ID")],
    session: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    project = await get_project_by_id(session, id, current_user.id)
    if project is None or project.owner_id != current_user.id:
        raise HTTPException(status.HTTP_404_NOT_FOUND)
    await session.delete(project)
    await session.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
