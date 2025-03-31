from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_async_session
from app.core.user import current_user, current_superuser
from app.crud.charityproject import charity_project_crud
from app.crud.donation import donation_crud
from app.models import User
from app.schemas import DonationCreate, DonationForAdminDB, DonationForUserDB
from app.services.investment import donations_distribution


router = APIRouter()


@router.post(
    '/',
    response_model=DonationForUserDB,
    response_model_exclude_none=True,
)
async def create_donation(
        donation: DonationCreate,
        session: AsyncSession = Depends(get_async_session),
        user: User = Depends(current_user),
):
    """Сделать пожертвование."""

    donation = await donation_crud.create(
        donation, session, user, commit=False)
    session.add_all(
        donations_distribution(
            target=donation,
            sources=await charity_project_crud.get_opens(session)))
    await session.commit()
    await session.refresh(donation)
    return donation


@router.get(
    '/',
    response_model=list[DonationForAdminDB],
    response_model_exclude_none=True,
    dependencies=[Depends(current_superuser)]
)
async def get_all_donations(
        session: AsyncSession = Depends(get_async_session),
):
    """
    Только для суперюзеров.
    Возвращает список всех пожертвований.
    """

    return await donation_crud.get_all(session)


@router.get(
    '/my',
    response_model=list[DonationForUserDB],
    response_model_exclude_none=True,
    response_model_exclude={'user_id'},
)
async def get_user_donations(
        session: AsyncSession = Depends(get_async_session),
        user: User = Depends(current_user),
):
    """Вернуть список пожертвований пользователя, выполняющего запрос."""

    return await donation_crud.get_by_user(user, session)
