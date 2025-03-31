from datetime import datetime

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.validators import (
    check_full_amount_not_less_than_invested,
    check_project_is_invested,
    check_project_is_not_fully_invested,
    check_project_name_duplicate,
)
from app.core.db import get_async_session
from app.core.user import current_superuser
from app.crud.charityproject import charity_project_crud
from app.crud.donation import donation_crud
from app.schemas import (
    CharityProjecDB, CharityProjectCreate, CharityProjectUpdate)
from app.services.investment import donations_distribution


router = APIRouter()


@router.post(
    '/',
    response_model=CharityProjecDB,
    response_model_exclude_none=True,
    dependencies=[Depends(current_superuser)],
)
async def create_charity_project(
        project: CharityProjectCreate,
        session: AsyncSession = Depends(get_async_session)
):
    """
    Только для суперюзеров.
    Создаёт благотварительный проект.
    """

    await check_project_name_duplicate(project.name, session)
    project = await charity_project_crud.create(project, session, commit=False)
    session.add_all(
        donations_distribution(
            target=project, sources=await donation_crud.get_opens(session)))
    await session.commit()
    await session.refresh(project)
    return project


@router.get(
    '/',
    response_model=list[CharityProjecDB],
    response_model_exclude_none=True,
)
async def get_charity_projects(
        session: AsyncSession = Depends(get_async_session)
):
    """Возвращает список всех проектов."""

    return await charity_project_crud.get_all(session)


@router.patch(
    '/{project_id}',
    response_model=CharityProjecDB,
    response_model_exclude_none=True,
    dependencies=[Depends(current_superuser)],
)
async def update_project(
        project_id: int,
        project_data: CharityProjectUpdate,
        session: AsyncSession = Depends(get_async_session),
):
    """
    Только для суперюзеров.
    Закрытый проект нельзя редактировать;
    нельзя установить требуемую сумму меньше уже вложенной.
    """

    project = await charity_project_crud.get_or_404(project_id, session)
    check_project_is_not_fully_invested(project)
    new_name = project_data.name
    if new_name is not None:
        await check_project_name_duplicate(
            new_name, session, permitted_id=project_id)
    new_full_amount = project_data.full_amount
    if new_full_amount is not None:
        check_full_amount_not_less_than_invested(project, new_full_amount)
        if new_full_amount == project.invested_amount:
            project.fully_invested = True
            project.close_date = datetime.now()
    return await charity_project_crud.update(
        project,
        update_data=project_data.dict(exclude_unset=True),
        session=session
    )


@router.delete(
    '/{project_id}',
    response_model=CharityProjecDB,
    response_model_exclude_none=True,
    dependencies=[Depends(current_superuser)],
)
async def delete(
        project_id: int,
        session: AsyncSession = Depends(get_async_session),
):
    """
    Только для суперюзеров.
    Удаляет проект. Нельзя удалить проект, в который уже были инвестированы
    средства, его можно только закрыть.
    """

    project = check_project_is_invested(
        await charity_project_crud.get_or_404(project_id, session))
    return await charity_project_crud.delete(project, session)
