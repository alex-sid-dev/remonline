from typing import Annotated

import structlog
from fastapi import APIRouter, Depends, status
from dishka import FromDishka
from dishka.integrations.fastapi import inject, DishkaRoute

from src.application.commands.organization.get_organization import (
    GetOrganizationCommandHandler,
    GetOrganizationResponse,
)
from src.application.commands.organization.create_organization import (
    CreateOrganizationCommandHandler,
    CreateOrganizationCommand,
    CreateOrganizationCommandResponse,
)
from src.application.commands.organization.update_organization import (
    UpdateOrganizationCommandHandler,
    UpdateOrganizationCommand,
)
from src.application.commands.organization.delete_organization import (
    DeleteOrganizationCommandHandler,
)
from src.entities.employees.models import Employee, EmployeePosition
from src.presentation.api.common.schemas.organization.organization import (
    OrganizationSchema,
    OrganizationResponseSchema,
)
from src.presentation.api.rest.v1.permissions import RoleChecker

router = APIRouter(prefix="/organization", tags=["Organization"], route_class=DishkaRoute)

logger = structlog.get_logger("api.organization").bind(service="organization")

# Только супервайзер может вводить и менять реквизиты организации
role_checker = RoleChecker([EmployeePosition.SUPERVISOR])
CurrentEmployee = Annotated[Employee, Depends(inject(role_checker.__call__))]


@router.get(
    path="",
    status_code=status.HTTP_200_OK,
)
async def get_organization(
    interactor: FromDishka[GetOrganizationCommandHandler],
    current_employee: CurrentEmployee,
) -> OrganizationResponseSchema:
    result = await interactor.run(current_employee)
    return OrganizationResponseSchema(
        id=result.id,
        uuid=result.uuid,
        name=result.name,
        inn=result.inn,
        address=result.address,
        kpp=result.kpp,
        bank_account=result.bank_account,
        corr_account=result.corr_account,
        bik=result.bik,
    )


@router.post(
    path="",
    status_code=status.HTTP_201_CREATED,
)
async def create_organization(
    request_data: OrganizationSchema,
    interactor: FromDishka[CreateOrganizationCommandHandler],
    current_employee: CurrentEmployee,
) -> CreateOrganizationCommandResponse:
    dto = CreateOrganizationCommand(
        name=request_data.name,
        inn=request_data.inn,
        address=request_data.address,
        kpp=request_data.kpp,
        bank_account=request_data.bank_account,
        corr_account=request_data.corr_account,
        bik=request_data.bik,
    )
    return await interactor.run(dto, current_employee)


@router.put(
    path="",
    status_code=status.HTTP_200_OK,
)
async def update_organization(
    request_data: OrganizationSchema,
    interactor: FromDishka[UpdateOrganizationCommandHandler],
    current_employee: CurrentEmployee,
) -> None:
    update_data = request_data.model_dump(exclude_unset=True)
    dto = UpdateOrganizationCommand(**update_data)
    await interactor.run(dto, current_employee)


@router.delete(
    path="",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_organization(
    interactor: FromDishka[DeleteOrganizationCommandHandler],
    current_employee: CurrentEmployee,
) -> None:
    await interactor.run(current_employee)
