import json

from aiogoogle import Aiogoogle
from aiogoogle.auth.creds import ServiceAccountCreds

from app.core.config import settings


SCOPES = [settings.spreadsheets_url, settings.drive_url]
INFO = json.load(open(settings.auth_info_filename))  # убрал из json// "universe_domain": "googleapis.com"

cred = ServiceAccountCreds(scopes=SCOPES, **INFO)


async def get_service():  # возможно здесь какое-то исключение
    async with Aiogoogle(service_account_creds=cred) as aiogoogle:
        yield aiogoogle
