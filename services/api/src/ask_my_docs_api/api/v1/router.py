from fastapi import APIRouter

from ask_my_docs_api.api.v1.routers import users

router = APIRouter(prefix="/api/v1")
router.include_router(users.router)
