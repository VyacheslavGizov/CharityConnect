from fastapi import FastAPI

from app.api.routers import main_router
from app.core.config import APP_TITLE, APP_DECRIPTION
from app.core.init_db import create_first_superuser


app = FastAPI(title=APP_TITLE, description=APP_DECRIPTION)

app.include_router(main_router)


@app.on_event('startup')
async def startup():
    await create_first_superuser()
