from datetime import datetime

from aiogoogle import Aiogoogle

from app.core.config import (
    FORMAT,
    LOCALE,
    settings,
    SHEET_TITLE,
    SPREADSHEET_TITLE,
)
from app.models.charity_project import CharityProject


async def spreadsheets_create(
        wrapper_services: Aiogoogle,
        rows: int = 100,
        columns: int = 100,
) -> str:
    now_date_time = datetime.now().strftime(FORMAT)
    service = await wrapper_services.discover('sheets', 'v4')
    spreadsheet_body = {
        'properties': {
            'title': SPREADSHEET_TITLE.format(timestamp=now_date_time),  # Возможно дата лишняя, как будет биься с датой ниже
            'locale': LOCALE
        },
        'sheets': [{
            'properties': {
                'sheetType': 'GRID',
                'sheetId': 0,
                'title': SHEET_TITLE,
                'gridProperties': {
                    'rowCount': rows,
                    'columnCount': columns
                }
            }
        }]
    }
    response = await wrapper_services.as_service_account(
        service.spreadsheets.create(json=spreadsheet_body)
    )
    spreadsheet_id = response['spreadsheetId']
    print(f'https://docs.google.com/spreadsheets/d/{spreadsheet_id}')  # потом убрать
    return spreadsheet_id


async def set_user_permissions(
        spreadsheet_id: str,
        wrapper_services: Aiogoogle
) -> None:
    permissions_body = {'type': 'user',
                        'role': 'writer',
                        'emailAddress': settings.email}
    service = await wrapper_services.discover('drive', 'v3')
    await wrapper_services.as_service_account(
        service.permissions.create(
            fileId=spreadsheet_id,
            json=permissions_body,
            fields='id'
        ))


def create_projects_table(projects: list[CharityProject]): # может прийти пустой список, правильная аннотация
    table_header = [  # Это константа
        ['Отчёт от', datetime.now().strftime(FORMAT)],
        ['Топ проектов по скорости закрытия'],
        ['Название проекта', 'Время сбора', 'Описание']
    ]
    table = [
        *table_header,
        *[list(map(  # отформатировать
            str, [project.name,
                  project.close_date - project.create_date,
                  project.description]))
          for project in projects]
    ]
    return table


async def spreadsheets_update_value(  # думаю это лучше сделать через append, или разом...
        spreadsheet_id: str,
        table: list,
        wrapper_services: Aiogoogle
) -> None:
    # now_date_time = datetime.now().strftime(FORMAT)
    service = await wrapper_services.discover('sheets', 'v4')
    update_body = {'values': table}
    response = await wrapper_services.as_service_account(  # нужно ли возвращать куда-то?
        service.spreadsheets.values.append(
            spreadsheetId=spreadsheet_id,
            range=SHEET_TITLE,  # как это вычислить заранее
            valueInputOption='USER_ENTERED',
            insertDataOption='INSERT_ROWS',
            json=update_body
        )
    )
