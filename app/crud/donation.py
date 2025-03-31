from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base import CRUDBase
from app.models import Donation, User


class CRUDDonation(CRUDBase):

    @staticmethod
    async def get_by_user(
            user: User,
            session: AsyncSession,
    ) -> Optional[list[Donation]]:
        return (
            await session.execute(
                select(Donation).where(Donation.user_id == user.id))
        ).scalars().all()


donation_crud = CRUDDonation(Donation)
