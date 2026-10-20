from fastapi import APIRouter

from ask_my_docs_api.api.deps import CurrentUser
from ask_my_docs_api.api.v1.schemas.users import UserRead

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserRead)
async def get_me(current_user: CurrentUser) -> UserRead:
    return UserRead.model_validate(current_user)
