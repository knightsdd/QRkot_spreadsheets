from typing import List

from fastapi import APIRouter, Depends

from app.api.validators import (check_project_befor_update,
                                check_project_before_delete,
                                check_project_dublicate)
from app.core.db import AsyncSession, get_async_session
from app.core.user import current_superuser
from app.crud.charity_project import charity_project_crud
from app.schemas.charity_project import (CharityProjectCreate,
                                         CharityProjectDB,
                                         CharityProjectUpdate)
from app.services.investing import investing_to_projects

router = APIRouter()


@router.post(
    '/',
    response_model=CharityProjectDB,
    response_model_exclude_none=True,
    dependencies=[Depends(current_superuser)],)
async def create_new_charity_project(
    project: CharityProjectCreate,
    session: AsyncSession = Depends(get_async_session)
):
    """Только для суперюзеров."""

    await check_project_dublicate(project.name, session)
    new_project = await charity_project_crud.create(project, session)
    new_project = await investing_to_projects(new_project, session)
    return new_project


@router.get(
    '/',
    response_model=List[CharityProjectDB],
    response_model_exclude_none=True,)
async def get_all_project(
    session: AsyncSession = Depends(get_async_session)
):
    """Получить список всех проектов"""

    all_projects = await charity_project_crud.get_multi(session=session)
    return all_projects


@router.delete(
    '/{project_id}',
    response_model=CharityProjectDB,
    dependencies=[Depends(current_superuser)],)
async def remove_project(
    project_id: int,
    session: AsyncSession = Depends(get_async_session),
):
    """Только для суперюзеров."""

    project = await check_project_before_delete(project_id, session)
    await charity_project_crud.remove(project, session)
    return project


@router.patch(
    '/{project_id}',
    response_model=CharityProjectDB,
    dependencies=[Depends(current_superuser)],
)
async def update_project(
    project_id: int,
    obj_in: CharityProjectUpdate,
    session: AsyncSession = Depends(get_async_session),
):
    """Только для суперюзеров."""

    new_amount = obj_in.full_amount
    project = await check_project_befor_update(
        proj_id=project_id, new_amount=new_amount, session=session)

    if obj_in.name is not None:
        await check_project_dublicate(
            proj_name=obj_in.name, update_id=project.id, session=session)

    project = await charity_project_crud.update_project_from_db(
        project, obj_in, session)
    return project
