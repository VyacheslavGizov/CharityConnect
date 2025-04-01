from pydantic import BaseSettings, EmailStr
from typing import Optional


MAX_NAME_LENGTH = 100
MIN_NAME_LENGTH = 1
MIN_DESCRIPTION_LENGTH = 1

APP_TITLE = 'Кошачий благотворительный фонд'
APP_DECRIPTION = 'Сервис для поддержки котиков!'

FORMAT = '%Y/%m/%d %H:%M:%S'
SPREADSHEET_TITLE = 'Закрытые проекты на {timestamp}'
SHEET_TITLE = 'Лист1'
LOCALE = 'ru_RU'


class Settings(BaseSettings):
    database_url: str = 'sqlite+aiosqlite:///./cat_fund.db'
    secret: str = 'default_secret'
    first_superuser_email: Optional[EmailStr] = None
    first_superuser_password: Optional[str] = None
    email: Optional[EmailStr] = None
    auth_info_filename: Optional[str] = None
    drive_url: Optional[str] = None
    spreadsheets_url: Optional[str] = None

    class Config:
        env_file = '.env'


settings = Settings()
