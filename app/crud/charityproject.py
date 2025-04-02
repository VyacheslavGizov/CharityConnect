from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import extract

from app.crud.base import CRUDBase
from app.models import CharityProject


class CRUDCharityProject(CRUDBase):

    @staticmethod
    async def get_id_by_name(
            name: str,
            session: AsyncSession
    ) -> Optional[int]:
        return (
            await session.execute(
                select(CharityProject.id).where(CharityProject.name == name))
        ).scalars().first()

    @staticmethod
    async def get_projects_by_comletion_rate(
        session: AsyncSession,
    ) -> list[CharityProject]:
        return (
            await session.execute(
                select(CharityProject).where(
                    CharityProject.fully_invested).order_by(
                        extract('epoch', CharityProject.close_date) -
                        extract('epoch', CharityProject.create_date)))
        ).scalars().all()


charity_project_crud = CRUDCharityProject(CharityProject)
