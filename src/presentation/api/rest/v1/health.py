import structlog
from dishka import FromDishka
from dishka.integrations.fastapi import DishkaRoute, inject
from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from starlette import status

from src.application.keycloak.auth_managers import OpenIDManager
from src.entities.employees.enum import EmployeePosition
from src.presentation.api.rest.v1.permissions import RoleChecker

logger = structlog.get_logger("health").bind(service="health")

router = APIRouter(prefix="/health", tags=["Health"], route_class=DishkaRoute)

health_checker = RoleChecker([EmployeePosition.SUPERVISOR, EmployeePosition.ADMIN])


@router.get(
    path="",
    dependencies=[Depends(inject(health_checker.__call__))],
    status_code=status.HTTP_200_OK,
    description="Health check endpoint that verifies the status of critical services.",
)
async def health_check(
    session_factory: FromDishka[async_sessionmaker[AsyncSession]],
    openid_manager: FromDishka[OpenIDManager],
) -> dict[str, str | dict[str, str]]:
    health_status: dict[str, str | dict[str, str]] = {
        "status": "healthy",
        "services": {},
    }

    # Check database
    try:
        async with session_factory() as session:
            await session.execute(text("SELECT 1"))
        health_status["services"]["database"] = "healthy"
        logger.info("Database healthy")
    except Exception as e:
        health_status["services"]["database"] = "unhealthy"
        health_status["status"] = "unhealthy"
        logger.error("Database unhealthy", error=str(e))

    # Check Keycloak
    try:
        await openid_manager.verify_token("dummy")
        health_status["services"]["keycloak"] = "healthy"
        logger.info("Keycloak healthy")
    except Exception as e:
        error_str = str(e).lower()
        error_type = type(e).__name__.lower()
        if any(
            keyword in error_str
            for keyword in ["connection", "timeout", "unreachable", "refused", "connect"]
        ) or any(keyword in error_type for keyword in ["connection", "timeout"]):
            health_status["services"]["keycloak"] = "unhealthy"
            health_status["status"] = "unhealthy"
            logger.error("Keycloak unhealthy", error=str(e))
        else:
            health_status["services"]["keycloak"] = "healthy"
            logger.info("Keycloak reachable but dummy token invalid")

    return health_status
