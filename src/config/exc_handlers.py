from functools import partial

from fastapi import FastAPI
from starlette import status as code

from src.application.errors._base import AuthenticationError, EntityNotFoundError, ConflictError, \
    ProductCardError, KeycloakError, FieldError
from src.presentation.api.common.exc_handlers import validate


def setup_exc_handlers(app: FastAPI) -> None:
    app.add_exception_handler(
        AuthenticationError,
        partial(validate, status=code.HTTP_401_UNAUTHORIZED),
    )
    app.add_exception_handler(
        EntityNotFoundError,
        partial(validate, status=code.HTTP_404_NOT_FOUND),
    )
    app.add_exception_handler(
        ConflictError,
        partial(validate, status=code.HTTP_409_CONFLICT),
    )
    app.add_exception_handler(
        ProductCardError,
        partial(validate, status=code.HTTP_422_UNPROCESSABLE_ENTITY),
    )
    app.add_exception_handler(
        FieldError,
        partial(validate, status=code.HTTP_422_UNPROCESSABLE_ENTITY),
    )
    app.add_exception_handler(
        KeycloakError,
        partial(validate, status=code.HTTP_503_SERVICE_UNAVAILABLE),
    )
