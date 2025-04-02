from pydantic import BaseSettings, EmailStr
from typing import Optional


MAX_NAME_LENGTH = 100
MIN_NAME_LENGTH = 1
MIN_DESCRIPTION_LENGTH = 1

APP_TITLE = 'Кошачий благотворительный фонд'
APP_DECRIPTION = 'Сервис для поддержки котиков!'

DATETIME_FORMAT = '%Y/%m/%d %H:%M:%S'


class Settings(BaseSettings):
    database_url: str = 'sqlite+aiosqlite:///./cat_fund.db'
    secret: str = 'default_secret'
    first_superuser_email: Optional[EmailStr] = None
    first_superuser_password: Optional[str] = None
    type: Optional[str] = None
    project_id: Optional[str] = None
    private_key_id: Optional[str] = None
    private_key: Optional[str] = None
    client_email: Optional[str] = None
    client_id: Optional[str] = None
    auth_uri: Optional[str] = None
    token_uri: Optional[str] = None
    auth_provider_x509_cert_url: Optional[str] = None
    client_x509_cert_url: Optional[str] = None
    email: Optional[str] = None

    class Config:
        env_file = '.env'


settings = Settings()
