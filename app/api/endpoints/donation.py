from typing import List

from fastapi import APIRouter, Depends

from app.core.db import AsyncSession, get_async_session
from app.core.user import current_superuser, current_user
from app.crud.donation import donation_crud
from app.models import User
from app.schemas.donation import DonationCreate, DonationDB, DonationMyRead
from app.services.investing import investing_to_projects

router = APIRouter()


@router.post(
    '/',
    response_model=DonationMyRead,
    response_model_exclude_none=True,
    dependencies=[Depends(current_user), ]
)
async def create_donation(
    donation: DonationCreate,
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_user)
):
    """Только для авторизованных пользователей"""

    new_donation = await donation_crud.create(donation, session, user)
    new_donation = await investing_to_projects(new_donation, session)

    return new_donation


@router.get(
    '/',
    response_model=List[DonationDB],
    response_model_exclude_none=True,
    dependencies=[Depends(current_superuser), ]
)
async def get_all_donations(
    session: AsyncSession = Depends(get_async_session)
):
    """Только для суперюзеров"""

    all_donations = await donation_crud.get_multi(session)
    return all_donations


@router.get(
    '/my',
    response_model=List[DonationMyRead],
    response_model_exclude_none=True,
    dependencies=[Depends(current_user), ]
)
async def get_user_donation(
    user: User = Depends(current_user),
    session: AsyncSession = Depends(get_async_session),
):
    """Только для авторизованных пользователей"""

    user_donations = await donation_crud.get_multi(session, user)
    return user_donations
