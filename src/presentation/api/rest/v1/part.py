from typing import List, Annotated
import structlog
from fastapi import APIRouter, Depends, status
from dishka import FromDishka
from dishka.integrations.fastapi import inject, DishkaRoute
from uuid import UUID

from src.application.commands.part.create_part import CreatePartCommandHandler, CreatePartCommand, \
    CreatePartCommandResponse
from src.application.commands.part.read_all_part import ReadAllPartCommandHandler, ReadAllPartCommand, ReadPartResponse
from src.application.commands.part.read_part import ReadPartCommandHandler, ReadPartCommand
from src.application.commands.part.update_part import UpdatePartCommandHandler, UpdatePartCommand
from src.application.commands.part.delete_part import DeletePartCommandHandler, DeletePartCommand
from src.entities.employees.models import Employee, EmployeePosition
from src.presentation.api.common.schemas.part.create_part import CreatePartSchema, UpdatePartSchema
from src.presentation.api.rest.v1.permissions import RoleChecker

router = APIRouter(prefix="/part", tags=["Part"], route_class=DishkaRoute)

logger = structlog.get_logger("api.part").bind(service="part")

role_checker = RoleChecker(
    [EmployeePosition.SUPERVISOR, EmployeePosition.ADMIN, EmployeePosition.MASTER, EmployeePosition.MANAGER])
CurrentEmployee = Annotated[Employee, Depends(inject(role_checker.__call__))]


@router.get(
    path="/all",
    status_code=status.HTTP_200_OK,
)
async def get_all_parts(
        interactor: FromDishka[ReadAllPartCommandHandler],
        current_employee: CurrentEmployee,
) -> List[ReadPartResponse]:
    logger.info("ReadAll parts endpoint called")
    dto = ReadAllPartCommand()
    result = await interactor.run(dto, current_employee)
    logger.info("ReadAll parts successfully")
    return result


@router.post(
    path="/create",
    status_code=status.HTTP_201_CREATED,
)
async def create_part(
        request_data: CreatePartSchema,
        interactor: FromDishka[CreatePartCommandHandler],
        current_employee: CurrentEmployee,
) -> CreatePartCommandResponse:
    logger.info("Create part endpoint called", name=request_data.name)
    dto = CreatePartCommand(
        name=request_data.name,
        sku=request_data.sku,
        price=request_data.price,
        stock_qty=request_data.stock_qty
    )
    result = await interactor.run(dto)
    logger.info("Part created successfully")
    return result


@router.patch(
    path="/update/{part_uuid}",
    status_code=status.HTTP_200_OK,
)
async def update_part(
        part_uuid: UUID,
        request_data: UpdatePartSchema,
        interactor: FromDishka[UpdatePartCommandHandler],
        current_employee: CurrentEmployee,
) -> None:
    logger.info("Update part endpoint called", part_uuid=str(part_uuid))
    update_data = request_data.model_dump(exclude_unset=True)
    dto = UpdatePartCommand(
        uuid=part_uuid,
        **update_data
    )
    await interactor.run(dto, current_employee)
    logger.info("Part updated successfully", part_uuid=str(part_uuid))


@router.get(
    path="/{part_uuid}",
    status_code=status.HTTP_200_OK,
)
async def get_part(
        part_uuid: UUID,
        interactor: FromDishka[ReadPartCommandHandler],
        current_employee: CurrentEmployee,
) -> ReadPartResponse:
    logger.info("Read part endpoint called", part_uuid=str(part_uuid))
    dto = ReadPartCommand(uuid=part_uuid)
    result = await interactor.run(dto, current_employee)
    logger.info("Read part successfully", part_uuid=str(part_uuid))
    return result


@router.delete(
    path="/{part_uuid}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_part(
        part_uuid: UUID,
        interactor: FromDishka[DeletePartCommandHandler],
        current_employee: CurrentEmployee,
) -> None:
    logger.info("Delete part endpoint called", part_uuid=str(part_uuid))
    dto = DeletePartCommand(uuid=part_uuid)
    await interactor.run(dto, current_employee)
    logger.info("Part deleted successfully", part_uuid=str(part_uuid))
