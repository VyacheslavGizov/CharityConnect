from fastapi.exceptions import HTTPException
from fastapi import status
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.charityproject import charity_project_crud


NONUNIQUE_PROJECT_NAME = 'Проект с именем \'{name}\' уже существует.'
PROJECT_IS_CLOSED = '{project} - проект закрыт, редактирование недоступно!'
WRONG_FULL_AMOUNT = ('Нельзя установить значение full_amount меньше уже '
                     'вложенной суммы: {invested}.')
PROJECT_IS_INVESTED_ERROR = (
    '{project} - были внесены средства, не подлежит удалению!')


async def check_project_name_duplicate(
        name: str,
        session: AsyncSession,
        permitted_id=None
) -> None:
    project_id = await charity_project_crud.get_id_by_name(name, session)
    if project_id and permitted_id != project_id:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            detail=NONUNIQUE_PROJECT_NAME.format(name=name))


def check_project_is_not_fully_invested(project):
    if project.fully_invested:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            detail=PROJECT_IS_CLOSED.format(project=project))


def check_full_amount_not_less_than_invested(project, full_amount):
    invested_amount = project.invested_amount
    if full_amount < invested_amount:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            detail=WRONG_FULL_AMOUNT.format(invested=invested_amount))


def check_project_is_invested(project):
    if project.invested_amount > 0:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            detail=PROJECT_IS_INVESTED_ERROR.format(project=project))
    return project
