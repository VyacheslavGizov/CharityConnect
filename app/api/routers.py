from fastapi import APIRouter

from app.api.endpoints import (
    charityproject_router,
    donatoin_router,
    google_router,
    user_router,
)


main_router = APIRouter()

main_router.include_router(
    charityproject_router,
    prefix='/charity_project',
    tags=['charity_projects']
)

main_router.include_router(
    donatoin_router,
    prefix='/donation',
    tags=['donations']
)

main_router.include_router(
    google_router,
    prefix='/google',
    tags=['Google']
)

main_router.include_router(user_router)
