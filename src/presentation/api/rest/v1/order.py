from typing import List, Annotated
import structlog
from fastapi import APIRouter, Depends, status
from dishka import FromDishka
from dishka.integrations.fastapi import inject, DishkaRoute
from uuid import UUID

from src.application.commands.order.create_order import CreateOrderCommandHandler, CreateOrderCommand
from src.application.commands.order.read_all_order import ReadAllOrderCommandHandler, ReadAllOrderCommand, ReadOrderResponse
from src.application.commands.order.read_order import ReadOrderCommandHandler, ReadOrderCommand
from src.application.commands.order.update_order import UpdateOrderCommandHandler, UpdateOrderCommand
from src.application.commands.order.delete_order import DeleteOrderCommandHandler, DeleteOrderCommand
from src.entities.employees.models import Employee, EmployeePosition
from src.presentation.api.common.schemas.order.create_order import CreateOrderSchema
from src.presentation.api.common.schemas.order.update_order import UpdateOrderSchema
from src.presentation.api.rest.v1.permissions import RoleChecker

router = APIRouter(prefix="/order", tags=["Order"], route_class=DishkaRoute)

logger = structlog.get_logger("api.order").bind(service="order")

role_checker = RoleChecker([EmployeePosition.SUPERVISOR, EmployeePosition.ADMIN, EmployeePosition.MASTER, EmployeePosition.MANAGER])
CurrentEmployee = Annotated[Employee, Depends(inject(role_checker.__call__))]

@router.get(
    path="/all",
    status_code=status.HTTP_200_OK,
)
async def get_all_orders(
        interactor: FromDishka[ReadAllOrderCommandHandler],
        current_employee: CurrentEmployee,
) -> List[ReadOrderResponse]:
    logger.info("ReadAll orders endpoint called")
    dto = ReadAllOrderCommand()
    result = await interactor.run(dto, current_employee)
    logger.info("ReadAll orders successfully")
    return result

@router.post(
    path="/create",
    status_code=status.HTTP_201_CREATED,
)
async def create_order(
        request_data: CreateOrderSchema,
        interactor: FromDishka[CreateOrderCommandHandler],
        current_employee: CurrentEmployee,
) -> None:
    logger.info("Create order endpoint called", client_uuid=str(request_data.client_uuid))
    dto = CreateOrderCommand(
        client_uuid=request_data.client_uuid,
        device_uuid=request_data.device_uuid,
        problem_description=request_data.problem_description,
        comment=request_data.comment,
        assigned_employee_uuid=request_data.assigned_employee_uuid,
        status=request_data.status,
        price=request_data.price
    )
    await interactor.run(dto, current_employee)
    logger.info("Order created successfully")

@router.patch(
    path="/update/{order_uuid}",
    status_code=status.HTTP_200_OK,
)
async def update_order(
        order_uuid: UUID,
        request_data: UpdateOrderSchema,
        interactor: FromDishka[UpdateOrderCommandHandler],
        current_employee: CurrentEmployee,
) -> None:
    logger.info("Update order endpoint called", order_uuid=str(order_uuid))
    update_data = request_data.model_dump(exclude_unset=True)
    dto = UpdateOrderCommand(
        uuid=order_uuid,
        **update_data
    )
    await interactor.run(dto, current_employee)
    logger.info("Order updated successfully", order_uuid=str(order_uuid))

@router.get(
    path="/{order_uuid}",
    status_code=status.HTTP_200_OK,
)
async def get_order(
        order_uuid: UUID,
        interactor: FromDishka[ReadOrderCommandHandler],
        current_employee: CurrentEmployee,
) -> ReadOrderResponse:
    logger.info("Read order endpoint called", order_uuid=str(order_uuid))
    dto = ReadOrderCommand(uuid=order_uuid)
    result = await interactor.run(dto, current_employee)
    logger.info("Read order successfully", order_uuid=str(order_uuid))
    return result

@router.delete(
    path="/{order_uuid}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_order(
        order_uuid: UUID,
        interactor: FromDishka[DeleteOrderCommandHandler],
        current_employee: CurrentEmployee,
) -> None:
    logger.info("Delete order endpoint called", order_uuid=str(order_uuid))
    dto = DeleteOrderCommand(uuid=order_uuid)
    await interactor.run(dto, current_employee)
    logger.info("Order deleted successfully", order_uuid=str(order_uuid))
