from datetime import datetime

from aiogoogle import Aiogoogle

from app.core.config import DATETIME_FORMAT, settings
from app.models.charity_project import CharityProject


SPREADSHEET_TITLE = 'Закрытые проекты'
SHEET_TITLE = 'Лист1'
LOCALE = 'ru_RU'

REPORT_TITLE = ['Отчёт от', ]
REPORT_TABLE_HEADER = [
    ['Топ проектов по скорости закрытия'],
    ['Название проекта', 'Время сбора', 'Описание']
]
REPORT_LINK = 'https://docs.google.com/spreadsheets/d/{spreadsheet_id}'


def create_report_table(projects: list[CharityProject]):
    report_title = REPORT_TITLE[:]
    report_title.append(datetime.now().strftime(DATETIME_FORMAT))
    return [
        report_title,
        *REPORT_TABLE_HEADER,
        *[
            list(map(str, [
                project.name,
                project.close_date - project.create_date,
                project.description
            ]))
            for project in projects
        ]
    ]


async def spreadsheets_create(
        wrapper_services: Aiogoogle,
        rows_number: int = 100,
        columns_number: int = 100,
) -> str:
    service = await wrapper_services.discover('sheets', 'v4')
    spreadsheet_body = {
        'properties': {
            'title': SPREADSHEET_TITLE,
            'locale': LOCALE
        },
        'sheets': [{
            'properties': {
                'sheetType': 'GRID',
                'sheetId': 0,
                'title': SHEET_TITLE,
                'gridProperties': {
                    'rowCount': rows_number,
                    'columnCount': columns_number
                }
            }
        }]
    }
    return (
        await wrapper_services.as_service_account(
            service.spreadsheets.create(json=spreadsheet_body))
    )['spreadsheetId']


async def set_user_permissions(
        spreadsheet_id: str,
        wrapper_services: Aiogoogle
) -> None:
    service = await wrapper_services.discover('drive', 'v3')
    await wrapper_services.as_service_account(
        service.permissions.create(
            fileId=spreadsheet_id,
            json={
                'type': 'user',
                'role': 'writer',
                'emailAddress': settings.email
            },
            fields='id'
        )
    )


async def spreadsheets_update_value(
        spreadsheet_id: str,
        table: list,
        wrapper_services: Aiogoogle
) -> None:
    service = await wrapper_services.discover('sheets', 'v4')
    await wrapper_services.as_service_account(
        service.spreadsheets.values.append(
            spreadsheetId=spreadsheet_id,
            range=SHEET_TITLE,
            valueInputOption='USER_ENTERED',
            insertDataOption='INSERT_ROWS',
            json={'values': table}
        )
    )
