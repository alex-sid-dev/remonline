from typing import List, Annotated
import structlog
from fastapi import APIRouter, Depends, status
from dishka import FromDishka
from dishka.integrations.fastapi import inject, DishkaRoute
from uuid import UUID

from src.application.commands.order_part.create_order_part import CreateOrderPartCommandHandler, CreateOrderPartCommand
from src.application.commands.order_part.read_all_order_part import ReadAllOrderPartCommandHandler, ReadAllOrderPartCommand, ReadOrderPartResponse
from src.application.commands.order_part.read_order_part import ReadOrderPartCommandHandler, ReadOrderPartCommand
from src.application.commands.order_part.update_order_part import UpdateOrderPartCommandHandler, UpdateOrderPartCommand
from src.application.commands.order_part.delete_order_part import DeleteOrderPartCommandHandler, DeleteOrderPartCommand
from src.entities.employees.models import Employee, EmployeePosition
from src.presentation.api.common.schemas.order_part.create_order_part import CreateOrderPartSchema
from src.presentation.api.common.schemas.order_part.update_order_part import UpdateOrderPartSchema
from src.presentation.api.rest.v1.permissions import RoleChecker

router = APIRouter(prefix="/order_part", tags=["Order Part"], route_class=DishkaRoute)

logger = structlog.get_logger("api.order_part").bind(service="order_part")

role_checker = RoleChecker([EmployeePosition.SUPERVISOR, EmployeePosition.ADMIN, EmployeePosition.MASTER, EmployeePosition.MANAGER])
CurrentEmployee = Annotated[Employee, Depends(inject(role_checker.__call__))]

@router.get(
    path="/all",
    status_code=status.HTTP_200_OK,
)
async def get_all_order_parts(
        interactor: FromDishka[ReadAllOrderPartCommandHandler],
        current_employee: CurrentEmployee,
) -> List[ReadOrderPartResponse]:
    logger.info("ReadAll order parts endpoint called")
    dto = ReadAllOrderPartCommand()
    result = await interactor.run(dto, current_employee)
    logger.info("ReadAll order parts successfully")
    return result

@router.post(
    path="/create",
    status_code=status.HTTP_201_CREATED,
)
async def create_order_part(
        request_data: CreateOrderPartSchema,
        interactor: FromDishka[CreateOrderPartCommandHandler],
        current_employee: CurrentEmployee,
) -> None:
    logger.info("Create order part endpoint called")
    dto = CreateOrderPartCommand(
        order_uuid=request_data.order_uuid,
        part_uuid=request_data.part_uuid,
        qty=request_data.qty,
        price=request_data.price
    )
    await interactor.run(dto, current_employee)
    logger.info("Order part created successfully")

@router.patch(
    path="/update/{order_part_uuid}",
    status_code=status.HTTP_200_OK,
)
async def update_order_part(
        order_part_uuid: UUID,
        request_data: UpdateOrderPartSchema,
        interactor: FromDishka[UpdateOrderPartCommandHandler],
        current_employee: CurrentEmployee,
) -> None:
    logger.info("Update order part endpoint called", order_part_uuid=str(order_part_uuid))
    dto = UpdateOrderPartCommand(
        uuid=order_part_uuid,
        qty=request_data.qty,
        price=request_data.price
    )
    await interactor.run(dto, current_employee)
    logger.info("Order part updated successfully", order_part_uuid=str(order_part_uuid))

@router.get(
    path="/{order_part_uuid}",
    status_code=status.HTTP_200_OK,
)
async def get_order_part(
        order_part_uuid: UUID,
        interactor: FromDishka[ReadOrderPartCommandHandler],
        current_employee: CurrentEmployee,
) -> ReadOrderPartResponse:
    logger.info("Read order part endpoint called", order_part_uuid=str(order_part_uuid))
    dto = ReadOrderPartCommand(uuid=order_part_uuid)
    result = await interactor.run(dto, current_employee)
    logger.info("Read order part successfully", order_part_uuid=str(order_part_uuid))
    return result

@router.delete(
    path="/{order_part_uuid}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_order_part(
        order_part_uuid: UUID,
        interactor: FromDishka[DeleteOrderPartCommandHandler],
        current_employee: CurrentEmployee,
) -> None:
    logger.info("Delete order part endpoint called", order_part_uuid=str(order_part_uuid))
    dto = DeleteOrderPartCommand(uuid=order_part_uuid)
    await interactor.run(dto, current_employee)
    logger.info("Order part deleted successfully", order_part_uuid=str(order_part_uuid))
