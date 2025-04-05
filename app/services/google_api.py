from copy import deepcopy
from datetime import datetime

from aiogoogle import Aiogoogle

from app.core.config import DATETIME_FORMAT, settings
from app.models.charity_project import CharityProject


MAX_ROWS = 10_000_000
MAX_COLUMNS = 18_278
WRONG_TABLE_SIZE = ('Таблица из {rows} строк и {columns} столбцов не может '
                    'быть создана. Превышены максимально допустимые размеры: '
                    f'{MAX_ROWS} строк, {MAX_COLUMNS} столбцов.')

SPREADSHEET_BODY = dict(
    properties=dict(
        title='Отчет от {timestamp}',
        locale='ru_RU',
    ),
    sheets=[dict(properties=dict(
        sheetType='GRID',
        sheetId=0,
        title='Лист1',
        gridProperties=dict(
            rowCount=...,
            columnCount=...,
        )
    ))]
)

PERMITIONS_BODY = dict(type='user', role='writer', emailAddress=...,)

REPORT_TABLE_HEADER = [
    ['Отчет от'],
    ['Топ проектов по скорости закрытия'],
    ['Название проекта', 'Время сбора', 'Описание']
]


def create_report_table(projects: list[CharityProject]):
    header = REPORT_TABLE_HEADER[:]
    header[0].append(datetime.now().strftime(DATETIME_FORMAT))
    return [
        *header,
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
) -> tuple[str, str]:
    if rows_number > MAX_ROWS or columns_number > MAX_COLUMNS:
        raise ValueError(WRONG_TABLE_SIZE.format(
            rows=rows_number, columns=columns_number))
    service = await wrapper_services.discover('sheets', 'v4')
    body = deepcopy(SPREADSHEET_BODY)
    body['properties']['title'] = body['properties']['title'].format(
        timestamp=datetime.now().strftime(DATETIME_FORMAT))
    grid_properties = body['sheets'][0]['properties']['gridProperties']
    grid_properties['rowCount'] = rows_number
    grid_properties['columnCount'] = columns_number
    response = (await wrapper_services.as_service_account(
        service.spreadsheets.create(json=body)))
    return response['spreadsheetId'], response['spreadsheetUrl']


async def set_user_permissions(
        spreadsheet_id: str,
        wrapper_services: Aiogoogle
) -> None:
    service = await wrapper_services.discover('drive', 'v3')
    permitions_body = PERMITIONS_BODY.copy()
    permitions_body['emailAddress'] = settings.email
    await wrapper_services.as_service_account(
        service.permissions.create(
            fileId=spreadsheet_id,
            json=permitions_body,
            fields='id'
        )
    )


async def spreadsheets_update_value(
        spreadsheet_id: str,
        table: list,
        wrapper_services: Aiogoogle,
        update_range: str
) -> None:
    service = await wrapper_services.discover('sheets', 'v4')
    await wrapper_services.as_service_account(
        service.spreadsheets.values.append(
            spreadsheetId=spreadsheet_id,
            range=update_range,
            valueInputOption='USER_ENTERED',
            insertDataOption='INSERT_ROWS',
            json={'values': table}
        )
    )
