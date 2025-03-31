from typing import Optional

from fastapi import status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import User


NOT_FOUND_MESSAGE = '"{object_name}" c id={object_id} не найден!'


class CRUDBase:
    def __init__(self, model):
        self.model = model

    async def save(self, db_object, session: AsyncSession):
        await session.commit()
        await session.refresh(db_object)
        return db_object

    async def create(
            self,
            object_in,
            session: AsyncSession,
            user: Optional[User] = None,
            commit=True
    ):
        object_in_data = object_in.dict()
        object_in_data['invested_amount'] = 0
        if user is not None:
            object_in_data['user_id'] = user.id
        db_object = self.model(**object_in_data)
        session.add(db_object)
        if commit:
            return await self.save(db_object, session)
        return db_object

    async def get(
            self,
            object_id: int,
            session: AsyncSession,
    ):
        return (
            await session.execute(
                select(self.model).where(self.model.id == object_id))
        ).scalars().first()

    async def get_or_404(
            self,
            object_id: int,
            session: AsyncSession
    ):
        object = await self.get(object_id, session)
        if object is None:
            raise HTTPException(
                status.HTTP_404_NOT_FOUND,
                detail=NOT_FOUND_MESSAGE.format(
                    object_name=self.model.__name__,
                    object_id=object_id
                )
            )
        return object

    async def get_opens(
            self,
            session: AsyncSession
    ):
        return (
            await session.execute(
                select(self.model).where(
                    self.model.fully_invested == 0).order_by(
                        self.model.create_date))
        ).scalars().all()

    async def get_all(
            self,
            session: AsyncSession,
    ):
        return (await session.execute(select(self.model))).scalars().all()

    async def update(
            self,
            db_object,
            update_data,
            session: AsyncSession,
    ):
        object_data = jsonable_encoder(db_object)
        for field in object_data:
            if field in update_data:
                setattr(db_object, field, update_data[field])
        return await self.save(db_object, session)

    async def delete(
            self,
            db_object,
            session: AsyncSession
    ):
        await session.delete(db_object)
        await session.commit()
        return db_object
