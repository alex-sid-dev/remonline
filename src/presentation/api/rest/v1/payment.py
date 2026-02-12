from typing import List, Annotated
import structlog
from fastapi import APIRouter, Depends, status
from dishka import FromDishka
from dishka.integrations.fastapi import inject, DishkaRoute
from uuid import UUID

from src.application.commands.payment.create_payment import CreatePaymentCommandHandler, CreatePaymentCommand
from src.application.commands.payment.read_all_payment import ReadAllPaymentCommandHandler, ReadAllPaymentCommand, ReadPaymentResponse
from src.application.commands.payment.read_payment import ReadPaymentCommandHandler, ReadPaymentCommand
from src.application.commands.payment.update_payment import UpdatePaymentCommandHandler, UpdatePaymentCommand
from src.application.commands.payment.delete_payment import DeletePaymentCommandHandler, DeletePaymentCommand
from src.entities.employees.models import Employee, EmployeePosition
from src.presentation.api.common.schemas.payment.create_payment import CreatePaymentSchema, UpdatePaymentSchema
from src.presentation.api.rest.v1.permissions import RoleChecker

router = APIRouter(prefix="/payment", tags=["Payment"], route_class=DishkaRoute)

logger = structlog.get_logger("api.payment").bind(service="payment")

role_checker = RoleChecker([EmployeePosition.SUPERVISOR, EmployeePosition.ADMIN, EmployeePosition.MASTER, EmployeePosition.MANAGER])
CurrentEmployee = Annotated[Employee, Depends(inject(role_checker.__call__))]

@router.get(
    path="/all",
    status_code=status.HTTP_200_OK,
)
async def get_all_payments(
        interactor: FromDishka[ReadAllPaymentCommandHandler],
        current_employee: CurrentEmployee,
) -> List[ReadPaymentResponse]:
    logger.info("ReadAll payments endpoint called")
    dto = ReadAllPaymentCommand()
    result = await interactor.run(dto, current_employee)
    logger.info("ReadAll payments successfully")
    return result

@router.post(
    path="/create",
    status_code=status.HTTP_201_CREATED,
)
async def create_payment(
        request_data: CreatePaymentSchema,
        interactor: FromDishka[CreatePaymentCommandHandler],
        current_employee: CurrentEmployee,
) -> None:
    logger.info("Create payment endpoint called", amount=request_data.amount)
    dto = CreatePaymentCommand(
        order_uuid=request_data.order_uuid,
        amount=request_data.amount,
        payment_method=request_data.payment_method,
        employee_uuid=request_data.employee_uuid,
        comment=request_data.comment
    )
    await interactor.run(dto, current_employee)
    logger.info("Payment created successfully")

@router.patch(
    path="/update/{payment_uuid}",
    status_code=status.HTTP_200_OK,
)
async def update_payment(
        payment_uuid: UUID,
        request_data: UpdatePaymentSchema,
        interactor: FromDishka[UpdatePaymentCommandHandler],
        current_employee: CurrentEmployee,
) -> None:
    logger.info("Update payment endpoint called", payment_uuid=str(payment_uuid))
    update_data = request_data.model_dump(exclude_unset=True)
    dto = UpdatePaymentCommand(
        uuid=payment_uuid,
        **update_data
    )
    await interactor.run(dto, current_employee)
    logger.info("Payment updated successfully", payment_uuid=str(payment_uuid))

@router.get(
    path="/{payment_uuid}",
    status_code=status.HTTP_200_OK,
)
async def get_payment(
        payment_uuid: UUID,
        interactor: FromDishka[ReadPaymentCommandHandler],
        current_employee: CurrentEmployee,
) -> ReadPaymentResponse:
    logger.info("Read payment endpoint called", payment_uuid=str(payment_uuid))
    dto = ReadPaymentCommand(uuid=payment_uuid)
    result = await interactor.run(dto, current_employee)
    logger.info("Read payment successfully", payment_uuid=str(payment_uuid))
    return result

@router.delete(
    path="/{payment_uuid}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_payment(
        payment_uuid: UUID,
        interactor: FromDishka[DeletePaymentCommandHandler],
        current_employee: CurrentEmployee,
) -> None:
    logger.info("Delete payment endpoint called", payment_uuid=str(payment_uuid))
    dto = DeletePaymentCommand(uuid=payment_uuid)
    await interactor.run(dto, current_employee)
    logger.info("Payment deleted successfully", payment_uuid=str(payment_uuid))
