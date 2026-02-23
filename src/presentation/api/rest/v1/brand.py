from typing import List, Annotated
from uuid import UUID

import structlog
from fastapi import APIRouter, Depends, status
from dishka import FromDishka
from dishka.integrations.fastapi import inject, DishkaRoute

from src.application.commands.brand.create_brand import (
    CreateBrandCommandHandler,
    CreateBrandCommand,
    CreateBrandCommandResponse,
)
from src.application.commands.brand.read_all_brand import (
    ReadAllBrandCommandHandler,
    ReadBrandResponse as ReadBrandResponseDto,
)
from src.application.commands.brand.read_brand import (
    ReadBrandCommandHandler,
    ReadBrandCommand,
    ReadBrandResponse,
)
from src.application.commands.brand.update_brand import (
    UpdateBrandCommandHandler,
    UpdateBrandCommand,
)
from src.application.commands.brand.delete_brand import DeleteBrandCommandHandler
from src.entities.employees.models import Employee, EmployeePosition
from src.presentation.api.common.schemas.brand.create_brand import CreateBrandSchema
from src.presentation.api.common.schemas.brand.update_brand import UpdateBrandSchema
from src.presentation.api.rest.v1.permissions import RoleChecker

router = APIRouter(prefix="/brand", tags=["Brand"], route_class=DishkaRoute)
logger = structlog.get_logger("api.brand").bind(service="brand")

role_checker = RoleChecker(
    [EmployeePosition.SUPERVISOR, EmployeePosition.ADMIN, EmployeePosition.MASTER, EmployeePosition.MANAGER]
)
CurrentEmployee = Annotated[Employee, Depends(inject(role_checker.__call__))]


@router.get("/all", status_code=status.HTTP_200_OK)
async def get_all_brands(
    interactor: FromDishka[ReadAllBrandCommandHandler],
    current_employee: CurrentEmployee,
) -> List[ReadBrandResponseDto]:
    return await interactor.run(current_employee)


@router.get("/{brand_uuid}", status_code=status.HTTP_200_OK)
async def get_brand(
    brand_uuid: UUID,
    interactor: FromDishka[ReadBrandCommandHandler],
    current_employee: CurrentEmployee,
) -> ReadBrandResponse:
    return await interactor.run(ReadBrandCommand(uuid=brand_uuid), current_employee)


@router.post("/create", status_code=status.HTTP_201_CREATED)
async def create_brand(
    request_data: CreateBrandSchema,
    interactor: FromDishka[CreateBrandCommandHandler],
    current_employee: CurrentEmployee,
) -> CreateBrandCommandResponse:
    return await interactor.run(CreateBrandCommand(name=request_data.name))


@router.patch("/update/{brand_uuid}", status_code=status.HTTP_200_OK)
async def update_brand(
    brand_uuid: UUID,
    request_data: UpdateBrandSchema,
    interactor: FromDishka[UpdateBrandCommandHandler],
    current_employee: CurrentEmployee,
) -> None:
    update_data = request_data.model_dump(exclude_unset=True)
    await interactor.run(UpdateBrandCommand(uuid=brand_uuid, **update_data), current_employee)


@router.delete("/{brand_uuid}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_brand(
    brand_uuid: UUID,
    interactor: FromDishka[DeleteBrandCommandHandler],
    current_employee: CurrentEmployee,
) -> None:
    await interactor.run(brand_uuid, current_employee)
