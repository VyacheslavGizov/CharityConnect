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

MAX_ROWS = 10_000_000
MAX_COLUMNS = 18_278
WRONG_TABLE_SIZE = ('Превышены допустимые размеры таблицы: '
                    f'{MAX_ROWS} строк, {MAX_COLUMNS} столбцов.')


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
        rows_number: int,
        columns_number: int,
):  # аннотация
    if rows_number > MAX_ROWS or columns_number > MAX_COLUMNS:
        raise ValueError(WRONG_TABLE_SIZE)
    service = await wrapper_services.discover('sheets', 'v4')
    spreadsheet_body = {
        'properties': {
            'title': SPREADSHEET_TITLE,  # Должна быть дата составления отчета
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
    response = (await wrapper_services.as_service_account(
        service.spreadsheets.create(json=spreadsheet_body)))
    return response['spreadsheetId'], response['spreadsheetUrl']


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
