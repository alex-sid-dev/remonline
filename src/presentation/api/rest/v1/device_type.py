from typing import List, Annotated
import structlog
from fastapi import APIRouter, Depends, status
from dishka import FromDishka
from dishka.integrations.fastapi import inject, DishkaRoute
from uuid import UUID

from src.application.commands.device_type.create_device_type import CreateDeviceTypeCommandHandler, \
    CreateDeviceTypeCommand, CreateDeviceTypeCommandResponse
from src.application.commands.device_type.read_all_device_type import ReadAllDeviceTypeCommandHandler, \
    ReadAllDeviceTypeCommand, ReadDeviceTypeResponse
from src.application.commands.device_type.read_device_type import ReadDeviceTypeCommandHandler, ReadDeviceTypeCommand
from src.application.commands.device_type.update_device_type import UpdateDeviceTypeCommandHandler, \
    UpdateDeviceTypeCommand
from src.application.commands.device_type.delete_device_type import DeleteDeviceTypeCommandHandler, \
    DeleteDeviceTypeCommand
from src.entities.employees.models import Employee, EmployeePosition
from src.presentation.api.common.schemas.device_type.create_device_type import CreateDeviceTypeSchema
from src.presentation.api.common.schemas.device_type.update_device_type import UpdateDeviceTypeSchema
from src.presentation.api.rest.v1.permissions import RoleChecker

router = APIRouter(prefix="/device_type", tags=["Device Type"], route_class=DishkaRoute)

logger = structlog.get_logger("api.device_type").bind(service="device_type")

role_checker = RoleChecker(
    [EmployeePosition.SUPERVISOR, EmployeePosition.ADMIN, EmployeePosition.MASTER, EmployeePosition.MANAGER])
CurrentEmployee = Annotated[Employee, Depends(inject(role_checker.__call__))]


@router.get(
    path="/all",
    status_code=status.HTTP_200_OK,
)
async def get_all_device_types(
        interactor: FromDishka[ReadAllDeviceTypeCommandHandler],
        current_employee: CurrentEmployee,
) -> List[ReadDeviceTypeResponse]:
    logger.info("ReadAll device types endpoint called")
    dto = ReadAllDeviceTypeCommand()
    result = await interactor.run(dto, current_employee)
    logger.info("ReadAll device types successfully")
    return result


@router.post(
    path="/create",
    status_code=status.HTTP_201_CREATED,
)
async def create_device_type(
        request_data: CreateDeviceTypeSchema,
        interactor: FromDishka[CreateDeviceTypeCommandHandler],
        current_employee: CurrentEmployee,
) -> CreateDeviceTypeCommandResponse:
    logger.info("Create device type endpoint called", name=request_data.name)
    dto = CreateDeviceTypeCommand(
        name=request_data.name,
        description=request_data.description
    )
    result = await interactor.run(dto)
    logger.info("Device type created successfully")
    return result


@router.patch(
    path="/update/{device_type_uuid}",
    status_code=status.HTTP_200_OK,
)
async def update_device_type(
        device_type_uuid: UUID,
        request_data: UpdateDeviceTypeSchema,
        interactor: FromDishka[UpdateDeviceTypeCommandHandler],
        current_employee: CurrentEmployee,
) -> None:
    logger.info("Update device type endpoint called", device_type_uuid=str(device_type_uuid))
    update_data = request_data.model_dump(exclude_unset=True)
    dto = UpdateDeviceTypeCommand(
        uuid=device_type_uuid,
        **update_data
    )
    await interactor.run(dto, current_employee)
    logger.info("Device type updated successfully", device_type_uuid=str(device_type_uuid))


@router.get(
    path="/{device_type_uuid}",
    status_code=status.HTTP_200_OK,
)
async def get_device_type(
        device_type_uuid: UUID,
        interactor: FromDishka[ReadDeviceTypeCommandHandler],
        current_employee: CurrentEmployee,
) -> ReadDeviceTypeResponse:
    logger.info("Read device type endpoint called", device_type_uuid=str(device_type_uuid))
    dto = ReadDeviceTypeCommand(uuid=device_type_uuid)
    result = await interactor.run(dto, current_employee)
    logger.info("Read device type successfully", device_type_uuid=str(device_type_uuid))
    return result


@router.delete(
    path="/{device_type_uuid}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_device_type(
        device_type_uuid: UUID,
        interactor: FromDishka[DeleteDeviceTypeCommandHandler],
        current_employee: CurrentEmployee,
) -> None:
    logger.info("Delete device type endpoint called", device_type_uuid=str(device_type_uuid))
    dto = DeleteDeviceTypeCommand(uuid=device_type_uuid)
    await interactor.run(dto, current_employee)
    logger.info("Device type deleted successfully", device_type_uuid=str(device_type_uuid))
