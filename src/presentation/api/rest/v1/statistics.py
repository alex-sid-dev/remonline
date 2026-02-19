from typing import Annotated

import structlog
from dishka import FromDishka
from dishka.integrations.fastapi import DishkaRoute, inject
from fastapi import APIRouter, Depends
from starlette import status

from src.application.commands.statistics.get_statistics import (
    GetStatisticsCommandHandler,
    StatisticsResponse,
)
from src.entities.employees.models import Employee, EmployeePosition
from src.presentation.api.rest.v1.permissions import RoleChecker

router = APIRouter(prefix="/statistics", tags=["Statistics"], route_class=DishkaRoute)

logger = structlog.get_logger("api.statistics").bind(service="statistics")

role_checker_all = RoleChecker(list(EmployeePosition))
AnyEmployee = Annotated[Employee, Depends(inject(role_checker_all.__call__))]


@router.get(
    path="",
    status_code=status.HTTP_200_OK,
)
async def get_statistics(
    interactor: FromDishka[GetStatisticsCommandHandler],
    current_employee: AnyEmployee,
) -> StatisticsResponse:
    logger.info("Statistics endpoint called")
    result = await interactor.run(current_employee)
    logger.info("Statistics calculated successfully", total_orders=result.total_orders)
    return result
