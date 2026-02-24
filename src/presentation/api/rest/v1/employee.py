from typing import Annotated
from uuid import UUID

import structlog
from dishka import FromDishka
from dishka.integrations.fastapi import DishkaRoute, inject
from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel, Field
from starlette import status

from src.application.commands.employee.change_password import (
    ChangePasswordCommand,
    ChangePasswordCommandHandler,
)
from src.application.commands.employee.create_employee import (
    CreateEmployeeCommand,
    CreateEmployeeCommandHandler,
    CreateEmployeeCommandResponse,
)
from src.application.commands.employee.delete_employee import (
    DeleteEmployeeCommand,
    DeleteEmployeeCommandHandler,
)
from src.application.commands.employee.read_all_employee import (
    PaginatedEmployeeResponse,
    ReadAllEmployeeCommand,
    ReadAllEmployeeCommandHandler,
    ReadEmployeeResponse,
)
from src.application.commands.employee.read_employee import (
    ReadEmployeeCommand,
    ReadEmployeeCommandHandler,
)
from src.application.commands.employee.update_employee import (
    UpdateEmployeeCommand,
    UpdateEmployeeCommandHandler,
)
from src.entities.employees.models import Employee, EmployeePosition
from src.presentation.api.common.schemas.employee.create_employee import CreateEmployeeSchema
from src.presentation.api.common.schemas.employee.update_employee import UpdateEmployeeSchema
from src.presentation.api.rest.v1.permissions import RoleChecker

router = APIRouter(prefix="/employee", tags=["Employee"], route_class=DishkaRoute)

logger = structlog.get_logger("api.employee").bind(service="employee")

role_checker = RoleChecker([EmployeePosition.SUPERVISOR, EmployeePosition.ADMIN])
CurrentEmployee = Annotated[Employee, Depends(inject(role_checker.__call__))]

# Любой авторизованный сотрудник (для /me — узнать свою роль)
any_employee_checker = RoleChecker(list(EmployeePosition))
AnyEmployee = Annotated[Employee, Depends(inject(any_employee_checker.__call__))]


@router.get(
    path="/me",
    status_code=status.HTTP_200_OK,
)
async def get_current_employee(
    current_employee: AnyEmployee,
) -> ReadEmployeeResponse:
    """Текущий авторизованный сотрудник (для определения роли на фронте)."""
    logger.info("Get current employee (me) called")
    return ReadEmployeeResponse.from_entity(current_employee)


@router.get(
    path="/all",
    status_code=status.HTTP_200_OK,
)
async def get_all_employees(
    interactor: FromDishka[ReadAllEmployeeCommandHandler],
    current_employee: CurrentEmployee,
    limit: int = Query(200, ge=1, le=1000),
    offset: int = Query(0, ge=0),
) -> PaginatedEmployeeResponse:
    logger.info("ReadAll employees endpoint called", limit=limit, offset=offset)
    dto = ReadAllEmployeeCommand(limit=limit, offset=offset)
    result = await interactor.run(dto, current_employee)
    logger.info("ReadAll employees successfully", total=result.total)
    return result


@router.post(
    path="/create",
    status_code=status.HTTP_201_CREATED,
)
async def create_employee(
    request_data: CreateEmployeeSchema,
    interactor: FromDishka[CreateEmployeeCommandHandler],
    current_employee: CurrentEmployee,
) -> CreateEmployeeCommandResponse:
    logger.info("Create employee endpoint called", phone=request_data.phone)
    dto = CreateEmployeeCommand(
        user_uuid=request_data.user_uuid,
        full_name=request_data.full_name,
        phone=request_data.phone,
        position=request_data.position,
        salary=request_data.salary,
        profit_percent=request_data.profit_percent,
    )
    result = await interactor.run(dto, current_employee)
    logger.info("Create employee registered successfully", phone=request_data.phone)
    return result


@router.patch(
    path="/update/{employee_uuid}",
    status_code=status.HTTP_200_OK,
)
async def update_employee(
    employee_uuid: UUID,
    request_data: UpdateEmployeeSchema,
    interactor: FromDishka[UpdateEmployeeCommandHandler],
    current_employee: CurrentEmployee,
) -> None:
    logger.info("Update employee endpoint called", employee_uuid=str(employee_uuid))
    update_data = request_data.model_dump(exclude_unset=True)
    dto = UpdateEmployeeCommand(uuid=employee_uuid, **update_data)
    await interactor.run(dto, current_employee)
    logger.info("Update employee registered successfully", employee_uuid=str(employee_uuid))


@router.get(
    path="/{employee_uuid}",
    status_code=status.HTTP_200_OK,
)
async def get_employee(
    employee_uuid: UUID,
    interactor: FromDishka[ReadEmployeeCommandHandler],
    current_employee: CurrentEmployee,
) -> ReadEmployeeResponse:
    logger.info("Read employee endpoint called", employee_uuid=str(employee_uuid))
    dto = ReadEmployeeCommand(uuid=employee_uuid)
    result = await interactor.run(dto, current_employee)
    logger.info("Read employee successfully", employee_uuid=str(employee_uuid))
    return result


class ChangePasswordSchema(BaseModel):
    new_password: str = Field(..., min_length=6, max_length=128)


@router.post(
    path="/{employee_uuid}/change-password",
    status_code=status.HTTP_200_OK,
)
async def change_employee_password(
    employee_uuid: UUID,
    request_data: ChangePasswordSchema,
    interactor: FromDishka[ChangePasswordCommandHandler],
    current_employee: CurrentEmployee,
) -> None:
    logger.info("Change password endpoint called", employee_uuid=str(employee_uuid))
    dto = ChangePasswordCommand(
        employee_uuid=employee_uuid,
        new_password=request_data.new_password,
    )
    await interactor.run(dto, current_employee)
    logger.info("Password changed successfully", employee_uuid=str(employee_uuid))


@router.delete(
    path="/{employee_uuid}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_employee(
    employee_uuid: UUID,
    interactor: FromDishka[DeleteEmployeeCommandHandler],
    current_employee: CurrentEmployee,
) -> None:
    logger.info("Delete employee endpoint called", employee_uuid=str(employee_uuid))
    dto = DeleteEmployeeCommand(uuid=employee_uuid)
    await interactor.run(dto, current_employee)
    logger.info("Employee deleted successfully", employee_uuid=str(employee_uuid))
