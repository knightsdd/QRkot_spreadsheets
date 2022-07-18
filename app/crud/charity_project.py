from datetime import datetime as dt
from typing import Optional

from fastapi.encoders import jsonable_encoder
from sqlalchemy import select
from sqlalchemy.engine import Result
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base import CRUDBase
from app.models import CharityProject
from app.schemas.charity_project import CharityProjectUpdate


class CRUDCharityProject(CRUDBase):

    async def get_project_id_by_name(
        self,
        proj_name: str,
        session: AsyncSession,
        exclude_id: Optional[int] = None
    ) -> Optional[int]:

        select_stmt = select(CharityProject.id).where(
            CharityProject.name == proj_name)
        if exclude_id is not None:
            select_stmt = select_stmt.where(
                CharityProject.id != exclude_id)
        db_proj_id: Result = await session.execute(select_stmt)

        db_proj_id = db_proj_id.scalars().first()
        return db_proj_id

    async def update_project_from_db(
        self,
        db_project: CharityProject,
        project_in: CharityProjectUpdate,
        session: AsyncSession,
    ) -> CharityProject:

        obj_data = jsonable_encoder(db_project)
        update_data = project_in.dict(exclude_unset=True)
        for field in obj_data:
            if field in update_data:
                setattr(db_project, field, update_data[field])
        if db_project.full_amount == db_project.invested_amount:
            db_project.fully_invested = True
            db_project.close_date = dt.now()
        session.add(db_project)
        await session.commit()
        await session.refresh(db_project)
        return db_project


charity_project_crud = CRUDCharityProject(CharityProject)
