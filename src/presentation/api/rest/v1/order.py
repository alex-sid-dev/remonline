from typing import Annotated
from uuid import UUID

import structlog
from dishka import FromDishka
from dishka.integrations.fastapi import DishkaRoute, inject
from fastapi import APIRouter, Depends, Query, status
from fastapi.responses import Response

from src.application.commands.order.create_order import (
    CreateOrderCommand,
    CreateOrderCommandHandler,
    CreateOrderCommandResponse,
)
from src.application.commands.order.create_order_with_client_and_device import (
    CreateOrderWithClientAndDeviceCommand,
    CreateOrderWithClientAndDeviceCommandHandler,
    CreateOrderWithClientAndDeviceCommandResponse,
)
from src.application.commands.order.delete_order import (
    DeleteOrderCommand,
    DeleteOrderCommandHandler,
)
from src.application.commands.order.generate_act_pdf import (
    GenerateActPdfCommand,
    GenerateActPdfCommandHandler,
)
from src.application.commands.order.generate_receipt_html import (
    GenerateReceiptHtmlCommand,
    GenerateReceiptHtmlCommandHandler,
)
from src.application.commands.order.read_all_order import (
    PaginatedOrderResponse,
    ReadAllOrderCommand,
    ReadAllOrderCommandHandler,
)
from src.application.commands.order.read_order import (
    ReadOrderCommand,
    ReadOrderCommandHandler,
    ReadOrderOneResponse,
)
from src.application.commands.order.update_order import (
    UpdateOrderCommand,
    UpdateOrderCommandHandler,
)
from src.entities.employees.models import Employee, EmployeePosition
from src.presentation.api.common.schemas.order.create_order import CreateOrderSchema
from src.presentation.api.common.schemas.order.create_order_with_client_and_device import (
    CreateOrderWithClientAndDeviceSchema,
)
from src.presentation.api.common.schemas.order.update_order import UpdateOrderSchema
from src.presentation.api.rest.v1.permissions import RoleChecker

router = APIRouter(prefix="/order", tags=["Order"], route_class=DishkaRoute)

logger = structlog.get_logger("api.order").bind(service="order")

role_checker_all = RoleChecker(
    [
        EmployeePosition.SUPERVISOR,
        EmployeePosition.ADMIN,
        EmployeePosition.MASTER,
        EmployeePosition.MANAGER,
    ]
)
CurrentEmployee = Annotated[Employee, Depends(inject(role_checker_all.__call__))]

# Только супервизор / админ / менеджер могут создавать заказы,
# мастер может только работать с уже существующими.
role_checker_create = RoleChecker(
    [EmployeePosition.SUPERVISOR, EmployeePosition.ADMIN, EmployeePosition.MANAGER]
)
CreatorEmployee = Annotated[Employee, Depends(inject(role_checker_create.__call__))]


@router.get(
    path="/all",
    status_code=status.HTTP_200_OK,
)
async def get_all_orders(
    interactor: FromDishka[ReadAllOrderCommandHandler],
    current_employee: CurrentEmployee,
    limit: int = Query(200, ge=1, le=1000),
    offset: int = Query(0, ge=0),
) -> PaginatedOrderResponse:
    logger.info("ReadAll orders endpoint called", limit=limit, offset=offset)
    dto = ReadAllOrderCommand(limit=limit, offset=offset)
    result = await interactor.run(dto, current_employee)
    logger.info("ReadAll orders successfully", total=result.total)
    return result


@router.post(
    path="/create",
    status_code=status.HTTP_201_CREATED,
)
async def create_order(
    request_data: CreateOrderSchema,
    interactor: FromDishka[CreateOrderCommandHandler],
    current_employee: CreatorEmployee,
) -> CreateOrderCommandResponse:
    logger.info("Create order endpoint called", client_uuid=str(request_data.client_uuid))
    dto = CreateOrderCommand(
        client_uuid=request_data.client_uuid,
        device_uuid=request_data.device_uuid,
        problem_description=request_data.problem_description,
        assigned_employee_uuid=request_data.assigned_employee_uuid,
        manager_uuid=request_data.manager_uuid,
        status=request_data.status.value,
        price=request_data.price,
    )
    result = await interactor.run(dto, current_employee)
    logger.info("Order created successfully")
    return result


@router.post(
    path="/create-aggregate",
    status_code=status.HTTP_201_CREATED,
)
async def create_order_with_client_and_device(
    request_data: CreateOrderWithClientAndDeviceSchema,
    interactor: FromDishka[CreateOrderWithClientAndDeviceCommandHandler],
    current_employee: CreatorEmployee,
) -> CreateOrderWithClientAndDeviceCommandResponse:
    logger.info("Create aggregate order endpoint called")
    dto = CreateOrderWithClientAndDeviceCommand(
        existing_client_uuid=request_data.existing_client_uuid,
        client_full_name=request_data.client_full_name,
        client_phone=request_data.client_phone,
        client_email=request_data.client_email,
        client_telegram_nick=request_data.client_telegram_nick,
        client_comment=request_data.client_comment,
        client_address=request_data.client_address,
        device_type_uuid=request_data.device_type_uuid,
        device_brand_uuid=request_data.device_brand_uuid,
        device_model=request_data.device_model,
        device_serial_number=request_data.device_serial_number,
        device_description=request_data.device_description,
        assigned_employee_uuid=request_data.assigned_employee_uuid,
        manager_uuid=request_data.manager_uuid,
        status=request_data.status.value,
        problem_description=request_data.problem_description,
        price=request_data.price,
    )
    result = await interactor.run(dto, current_employee)
    logger.info(
        "Aggregate order created successfully",
        order_uuid=str(result.order_uuid),
        client_uuid=str(result.client_uuid),
        device_uuid=str(result.device_uuid),
    )
    return result


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
    dto = UpdateOrderCommand(uuid=order_uuid, **update_data)
    await interactor.run(dto, current_employee)
    logger.info("Order updated successfully", order_uuid=str(order_uuid))


@router.get(
    path="/{order_uuid}/act",
    status_code=status.HTTP_200_OK,
    responses={200: {"content": {"text/html": {}}}},
)
async def get_order_act(
    order_uuid: UUID,
    interactor: FromDishka[GenerateActPdfCommandHandler],
    current_employee: CurrentEmployee,
) -> Response:
    logger.info("Generate act endpoint called", order_uuid=str(order_uuid))
    dto = GenerateActPdfCommand(uuid=order_uuid)
    html = await interactor.run(dto, current_employee)
    return Response(content=html, media_type="text/html; charset=utf-8")


@router.get(
    path="/{order_uuid}/receipt",
    status_code=status.HTTP_200_OK,
    responses={200: {"content": {"text/html": {}}}},
)
async def get_order_receipt(
    order_uuid: UUID,
    interactor: FromDishka[GenerateReceiptHtmlCommandHandler],
    current_employee: CurrentEmployee,
) -> Response:
    logger.info("Generate receipt endpoint called", order_uuid=str(order_uuid))
    dto = GenerateReceiptHtmlCommand(uuid=order_uuid)
    html = await interactor.run(dto, current_employee)
    return Response(content=html, media_type="text/html; charset=utf-8")


@router.get(
    path="/{order_uuid}",
    status_code=status.HTTP_200_OK,
)
async def get_order(
    order_uuid: UUID,
    interactor: FromDishka[ReadOrderCommandHandler],
    current_employee: CurrentEmployee,
) -> ReadOrderOneResponse:
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
