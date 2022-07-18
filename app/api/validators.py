from http import HTTPStatus
from typing import Optional

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.charity_project import charity_project_crud
from app.models import CharityProject


async def check_project_dublicate(
    proj_name: str,
    session: AsyncSession,
    update_id: Optional[int] = None
) -> None:

    proj_id = await charity_project_crud.get_project_id_by_name(
        proj_name=proj_name, session=session, exclude_id=update_id)
    if proj_id is not None:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail='Проект с таким именем уже существует!'
        )


async def check_project_exists(
    proj_id: int,
    session: AsyncSession,
) -> CharityProject:
    project: CharityProject = await charity_project_crud.get(proj_id, session)
    if not project:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='Проект не найден'
        )
    return project


async def check_project_before_delete(
    proj_id: int,
    session: AsyncSession,
) -> CharityProject:

    project: CharityProject = await check_project_exists(proj_id, session)

    if project.invested_amount > 0:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail='В проект были внесены средства, не подлежит удалению!'
        )

    return project


async def check_project_befor_update(
    *,
    proj_id: int,
    new_amount: Optional[int] = None,
    session: AsyncSession,
) -> CharityProject:

    project: CharityProject = await check_project_exists(proj_id, session)

    if project.fully_invested:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail='Закрытый проект нельзя редактировать!'
        )

    if new_amount:
        if new_amount < project.invested_amount:
            raise HTTPException(
                status_code=HTTPStatus.UNPROCESSABLE_ENTITY,
                detail='Нельзя установить требуемую сумму меньше уже '
                       'вложенной'
            )
    return project
