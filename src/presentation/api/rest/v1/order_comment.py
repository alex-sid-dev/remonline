from typing import Annotated
from uuid import UUID

import structlog
from fastapi import APIRouter, Depends, status
from dishka import FromDishka
from dishka.integrations.fastapi import inject, DishkaRoute

from src.application.commands.order_comment.create_order_comment import (
    CreateOrderCommentCommandHandler,
    CreateOrderCommentCommand,
    CreateOrderCommentCommandResponse,
)
from src.entities.employees.models import Employee, EmployeePosition
from src.presentation.api.common.schemas.order_comment.create_order_comment import CreateOrderCommentSchema
from src.presentation.api.rest.v1.permissions import RoleChecker

router = APIRouter(prefix="/order_comment", tags=["Order Comment"], route_class=DishkaRoute)

logger = structlog.get_logger("api.order_comment").bind(service="order_comment")

role_checker = RoleChecker(
    [EmployeePosition.SUPERVISOR, EmployeePosition.ADMIN, EmployeePosition.MASTER, EmployeePosition.MANAGER])
CurrentEmployee = Annotated[Employee, Depends(inject(role_checker.__call__))]


@router.post(
    path="/create",
    status_code=status.HTTP_201_CREATED,
)
async def create_order_comment(
        request_data: CreateOrderCommentSchema,
        interactor: FromDishka[CreateOrderCommentCommandHandler],
        current_employee: CurrentEmployee,
) -> CreateOrderCommentCommandResponse:
    logger.info("Create order comment endpoint called", order_uuid=str(request_data.order_uuid))
    dto = CreateOrderCommentCommand(
        order_uuid=request_data.order_uuid,
        text=request_data.text,
    )
    result = await interactor.run(dto, current_employee)
    logger.info("Order comment created successfully", order_uuid=str(request_data.order_uuid))
    return result

