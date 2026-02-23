from typing import List, Annotated
import structlog
from fastapi import APIRouter, Depends, status
from dishka import FromDishka
from dishka.integrations.fastapi import inject, DishkaRoute
from uuid import UUID

from src.application.commands.device.create_device import CreateDeviceCommandHandler, CreateDeviceCommand, \
    CreateDeviceCommandResponse
from src.application.commands.device.read_all_device import ReadAllDeviceCommandHandler, ReadAllDeviceCommand, \
    ReadDeviceResponse
from src.application.commands.device.read_device import ReadDeviceCommandHandler, ReadDeviceCommand
from src.application.commands.device.update_device import UpdateDeviceCommandHandler, UpdateDeviceCommand
from src.application.commands.device.delete_device import DeleteDeviceCommandHandler, DeleteDeviceCommand
from src.entities.employees.models import Employee, EmployeePosition
from src.presentation.api.common.schemas.device.create_device import CreateDeviceSchema
from src.presentation.api.common.schemas.device.update_device import UpdateDeviceSchema
from src.presentation.api.rest.v1.permissions import RoleChecker

router = APIRouter(prefix="/device", tags=["Device"], route_class=DishkaRoute)

logger = structlog.get_logger("api.device").bind(service="device")

role_checker = RoleChecker(
    [EmployeePosition.SUPERVISOR, EmployeePosition.ADMIN, EmployeePosition.MASTER, EmployeePosition.MANAGER])
CurrentEmployee = Annotated[Employee, Depends(inject(role_checker.__call__))]


@router.get(
    path="/all",
    status_code=status.HTTP_200_OK,
)
async def get_all_devices(
        interactor: FromDishka[ReadAllDeviceCommandHandler],
        current_employee: CurrentEmployee,
) -> List[ReadDeviceResponse]:
    logger.info("ReadAll devices endpoint called")
    dto = ReadAllDeviceCommand()
    result = await interactor.run(dto, current_employee)
    logger.info("ReadAll devices successfully")
    return result


@router.post(
    path="/create",
    status_code=status.HTTP_201_CREATED,
)
async def create_device(
        request_data: CreateDeviceSchema,
        interactor: FromDishka[CreateDeviceCommandHandler],
        current_employee: CurrentEmployee,
) -> CreateDeviceCommandResponse:
    logger.info("Create device endpoint called", brand_uuid=str(request_data.brand_uuid), model=request_data.model)
    dto = CreateDeviceCommand(
        client_uuid=request_data.client_uuid,
        type_uuid=request_data.type_uuid,
        brand_uuid=request_data.brand_uuid,
        model=request_data.model,
        serial_number=request_data.serial_number,
        description=request_data.description
    )
    result = await interactor.run(dto)
    logger.info("Device created successfully")
    return result


@router.patch(
    path="/update/{device_uuid}",
    status_code=status.HTTP_200_OK,
)
async def update_device(
        device_uuid: UUID,
        request_data: UpdateDeviceSchema,
        interactor: FromDishka[UpdateDeviceCommandHandler],
        current_employee: CurrentEmployee,
) -> None:
    logger.info("Update device endpoint called", device_uuid=str(device_uuid))
    update_data = request_data.model_dump(exclude_unset=True)
    dto = UpdateDeviceCommand(
        uuid=device_uuid,
        **update_data
    )
    await interactor.run(dto, current_employee)
    logger.info("Device updated successfully", device_uuid=str(device_uuid))


@router.get(
    path="/{device_uuid}",
    status_code=status.HTTP_200_OK,
)
async def get_device(
        device_uuid: UUID,
        interactor: FromDishka[ReadDeviceCommandHandler],
        current_employee: CurrentEmployee,
) -> ReadDeviceResponse:
    logger.info("Read device endpoint called", device_uuid=str(device_uuid))
    dto = ReadDeviceCommand(uuid=device_uuid)
    result = await interactor.run(dto, current_employee)
    logger.info("Read device successfully", device_uuid=str(device_uuid))
    return result


@router.delete(
    path="/{device_uuid}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_device(
        device_uuid: UUID,
        interactor: FromDishka[DeleteDeviceCommandHandler],
        current_employee: CurrentEmployee,
) -> None:
    logger.info("Delete device endpoint called", device_uuid=str(device_uuid))
    dto = DeleteDeviceCommand(uuid=device_uuid)
    await interactor.run(dto, current_employee)
    logger.info("Device deleted successfully", device_uuid=str(device_uuid))
