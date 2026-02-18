from fastapi import APIRouter
from starlette import status

from src.presentation.api.common.validation_rules import get_validation_rules_for_frontend

router = APIRouter(prefix="/validation-rules", tags=["Validation"])


@router.get(
    path="",
    status_code=status.HTTP_200_OK,
    description="Правила валидации полей (email, пароль, телефон и т.д.) — те же, что в Pydantic-схемах.",
)
async def get_validation_rules() -> dict:
    return get_validation_rules_for_frontend()
