from datetime import datetime as dt
from typing import List

from sqlalchemy import false, select
from sqlalchemy.engine import Result
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import CharityProject, Donation


def close_object(obj, date: dt):
    obj.fully_invested = True
    obj.close_date = date
    return obj


def calculate_invest(obj1, obj2):
    obj1.invested_amount += (obj2.full_amount - obj2.invested_amount)
    obj2.invested_amount = obj2.full_amount


async def investing_to_projects(obj_in, session: AsyncSession):

    free_projects: Result = await session.execute(
        select(CharityProject).where(
            CharityProject.fully_invested == false()
        ).order_by(CharityProject.create_date)
    )
    free_projects: List[CharityProject] = free_projects.scalars().all()

    free_donations: Result = await session.execute(
        select(Donation).where(
            Donation.fully_invested == false()
        ).order_by(Donation.create_date)
    )
    free_donations: List[Donation] = free_donations.scalars().all()

    projects_for_commit, donations_for_commit = dict(), dict()

    date_now = dt.now()

    for proj in free_projects:
        for donat in free_donations:
            if donat.fully_invested or proj.fully_invested:
                continue
            if ((proj.full_amount - proj.invested_amount) ==
                    (donat.full_amount - donat.invested_amount)):
                calculate_invest(proj, donat)
                donations_for_commit[donat.id] = close_object(donat, date_now)
                projects_for_commit[proj.id] = close_object(proj, date_now)
                continue

            if ((proj.full_amount - proj.invested_amount) >
                    (donat.full_amount - donat.invested_amount)):
                calculate_invest(proj, donat)
                donations_for_commit[donat.id] = close_object(donat, date_now)
                projects_for_commit[proj.id] = proj
                continue

            if ((proj.full_amount - proj.invested_amount) <
                    (donat.full_amount - donat.invested_amount)):
                calculate_invest(donat, proj)
                projects_for_commit[proj.id] = close_object(proj, date_now)
                donations_for_commit[donat.id] = donat
                continue

    data_for_commit = (list(projects_for_commit.values()) +
                       list(donations_for_commit.values()))

    if data_for_commit:
        session.add_all(data_for_commit)
        await session.commit()
        await session.refresh(obj_in)

    return obj_in
