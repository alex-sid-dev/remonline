import structlog
from dishka import FromDishka

from dishka.integrations.fastapi import DishkaRoute, inject
from fastapi import APIRouter, Depends
from starlette import status

from src.application.commands.base.auth import RegisterCommandHandler, RegisterCommand, LoginCommandHandler, \
    LoginResponse, LoginCommand, LogoutCommandHandler, LogoutCommand, UpdateAccessTokenCommandHandler, \
    UpdateAccessTokenResponse, UpdateAccessTokenCommand
from src.application.commands.base.auth.registration import RegisterCommandResponse
from src.entities.employees.enum import EmployeePosition
from src.presentation.api.common.dependencies import CredentialsDependency
from src.presentation.api.common.schemas.base.auth import RegisterSchema, UpdateAccessTokenSchema, LogoutSchema, \
    LoginSchema
from src.presentation.api.common.schemas.base.exception import ExceptionSchema
from src.presentation.api.rest.v1.permissions import RoleChecker

router = APIRouter(prefix="/auth", tags=["Auth"], route_class=DishkaRoute)

logger = structlog.get_logger("api.auth").bind(service="auth")

health_checker = RoleChecker([EmployeePosition.SUPERVISOR, EmployeePosition.ADMIN])


@router.post(
    path="/register",
    dependencies=[Depends(inject(health_checker.__call__))],
    status_code=status.HTTP_201_CREATED,
    responses={
        status.HTTP_409_CONFLICT: {"model": ExceptionSchema},
        status.HTTP_503_SERVICE_UNAVAILABLE: {"model": ExceptionSchema},
    },
)
async def register(
        request_data: RegisterSchema,
        interactor: FromDishka[RegisterCommandHandler],
) -> RegisterCommandResponse:
    logger.info("Register endpoint called", email=str(request_data.email))
    dto = RegisterCommand(
        email=str(request_data.email),
        password=request_data.password,
    )
    result = await interactor.run(dto)
    logger.info("User registered successfully", email=str(request_data.email))
    return result


@router.post(
    path="/login",
    responses={
        status.HTTP_404_NOT_FOUND: {"model": ExceptionSchema},
        status.HTTP_503_SERVICE_UNAVAILABLE: {"model": ExceptionSchema},
    },
)
async def login_seller(
        request_data: LoginSchema,
        interactor: FromDishka[LoginCommandHandler],
) -> LoginResponse:
    logger.info("Login endpoint called", email=str(request_data.email))
    dto = LoginCommand(
        email=request_data.email,
        password=request_data.password,
    )
    result = await interactor.run(dto)
    logger.info("User logged in successfully", email=str(request_data.email))
    return result


@router.post(
    path="/logout",
    responses={
        status.HTTP_401_UNAUTHORIZED: {"model": ExceptionSchema},
        status.HTTP_503_SERVICE_UNAVAILABLE: {"model": ExceptionSchema},
    },
)
async def logout_seller(
        request_data: LogoutSchema,
        interactor: FromDishka[LogoutCommandHandler],
) -> None:
    logger.info("Logout endpoint called",
                refresh_token=request_data.refresh_token[:8] + "...")  # partial token for security
    dto = LogoutCommand(refresh_token=request_data.refresh_token)
    await interactor.run(dto)
    logger.info("User logged out successfully")


@router.post(
    path="/refresh",
    responses={
        status.HTTP_401_UNAUTHORIZED: {"model": ExceptionSchema},
        status.HTTP_503_SERVICE_UNAVAILABLE: {"model": ExceptionSchema},
    },
)
async def update_access_token(
        request_data: UpdateAccessTokenSchema,
        interactor: FromDishka[UpdateAccessTokenCommandHandler],
) -> UpdateAccessTokenResponse:
    logger.info("Refresh token endpoint called", refresh_token=request_data.refresh_token[:8] + "...")
    dto = UpdateAccessTokenCommand(refresh_token=request_data.refresh_token)
    result = await interactor.run(dto)
    logger.info("Access token refreshed successfully")
    return result
