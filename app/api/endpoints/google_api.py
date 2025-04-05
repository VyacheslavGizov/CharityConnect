from aiogoogle import Aiogoogle
from fastapi import APIRouter, Depends
from fastapi import status
from fastapi.exceptions import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_async_session
from app.core.google_client import get_service
from app.core.user import current_superuser
from app.crud.charityproject import charity_project_crud
from app.services.google_api import (
    create_report_table,
    set_user_permissions,
    spreadsheets_create,
    spreadsheets_update_value,
)


router = APIRouter()


@router.get(
    '/',
    dependencies=[Depends(current_superuser)]
)
async def get_report(
    session: AsyncSession = Depends(get_async_session),
    wrapper_services: Aiogoogle = Depends(get_service)
) -> dict[str, str]:
    """Только для суперюзеров"""

    table = create_report_table(
        await charity_project_crud.get_projects_by_comletion_rate(session))
    rows_number = len(table)
    columns_number = max(map(len, table))
    try:
        spreadsheet_id, report_link = await spreadsheets_create(
            wrapper_services, rows_number, columns_number)
    except ValueError as error:
        raise HTTPException(
            status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(error))
    await set_user_permissions(spreadsheet_id, wrapper_services)
    await spreadsheets_update_value(
        spreadsheet_id,
        table,
        wrapper_services,
        update_range=f'R1C1:R{rows_number}C{columns_number}'
    )
    return {'report_link': report_link}
