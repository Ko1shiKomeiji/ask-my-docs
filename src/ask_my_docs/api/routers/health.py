from fastapi import APIRouter

router = APIRouter(prefix="/health", tags=["healthchecks"])


@router.get("")
async def health() -> dict:
    return {"status": "ok"}
