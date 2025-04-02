from aiogoogle import Aiogoogle
from aiogoogle.auth.creds import ServiceAccountCreds
from aiogoogle.excs import AiogoogleError
from fastapi import status
from fastapi.exceptions import HTTPException

from app.core.config import settings


UNSUCCESFUL_GOOGLE_API = (
    'Операция не выполнена: ошибка при работе с API GoogleCloud.')

SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
]
INFO = {
    'type': settings.type,
    'project_id': settings.project_id,
    'private_key_id': settings.private_key_id,
    'private_key': settings.private_key,
    'client_email': settings.client_email,
    'client_id': settings.client_id,
    'auth_uri': settings.auth_uri,
    'token_uri': settings.token_uri,
    'auth_provider_x509_cert_url': settings.auth_provider_x509_cert_url,
    'client_x509_cert_url': settings.client_x509_cert_url
}

cred = ServiceAccountCreds(scopes=SCOPES, **INFO)


async def get_service():
    async with Aiogoogle(service_account_creds=cred) as aiogoogle:
        try:
            yield aiogoogle
        except AiogoogleError:
            raise HTTPException(
                status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=UNSUCCESFUL_GOOGLE_API
            )
