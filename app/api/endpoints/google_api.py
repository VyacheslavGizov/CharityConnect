from aiogoogle import Aiogoogle
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_async_session
from app.core.google_client import get_service
from app.core.user import current_superuser
from app.crud.charityproject import charity_project_crud
from app.schemas.charityproject import CharityProjecDB
from app.services.google_api import (
    create_projects_table,
    spreadsheets_create,
    set_user_permissions,
    spreadsheets_update_value,
)
from pprint import pprint


router = APIRouter()


@router.get(
    '/',
    response_model=list[CharityProjecDB],  # возможно вернуть ссылку на отчет
    dependencies=[Depends(current_superuser)]
)
async def get_report(
    session: AsyncSession = Depends(get_async_session),
    wrapper_services: Aiogoogle = Depends(get_service)
):
    """Только для суперюзеров"""
    charity_projects = await (
        charity_project_crud.get_projects_by_comletion_rate(session))
    
    table = create_projects_table(charity_projects)
    rows = len(table)
    columns = max(map(len, table))

    spreadsheet_id = await spreadsheets_create(
        wrapper_services, rows=rows, columns=columns)
    await set_user_permissions(
        spreadsheet_id=spreadsheet_id, wrapper_services=wrapper_services)
    await spreadsheets_update_value(spreadsheet_id, table, wrapper_services)

    pprint(table)
    print(rows, columns)
    return charity_projects
