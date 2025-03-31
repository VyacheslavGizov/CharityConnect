from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

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


charity_project_crud = CRUDCharityProject(CharityProject)
