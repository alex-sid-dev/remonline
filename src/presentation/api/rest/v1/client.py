from typing import List, Annotated
from uuid import UUID
import structlog
from fastapi import APIRouter, Depends, Query, status
from dishka import FromDishka
from dishka.integrations.fastapi import inject, DishkaRoute

from src.application.commands.client.create_client import CreateClientCommandHandler, CreateClientCommand, \
    CreateClientCommandResponse
from src.application.commands.client.read_all_client import ReadAllClientCommandHandler, ReadAllClientCommand, \
    ReadClientResponse, PaginatedClientResponse
from src.application.commands.client.read_client import ReadClientCommandHandler, ReadClientCommand
from src.application.commands.client.update_client import UpdateClientCommandHandler, UpdateClientCommand
from src.application.commands.client.delete_client import DeleteClientCommandHandler, DeleteClientCommand
from src.entities.employees.models import Employee, EmployeePosition
from src.presentation.api.common.schemas.client.create_client import CreateClientSchema
from src.presentation.api.common.schemas.client.update_client import UpdateClientSchema
from src.presentation.api.rest.v1.permissions import RoleChecker

router = APIRouter(prefix="/client", tags=["Client"], route_class=DishkaRoute)

logger = structlog.get_logger("api.client").bind(service="client")

role_checker = RoleChecker(
    [EmployeePosition.SUPERVISOR, EmployeePosition.ADMIN, EmployeePosition.MASTER, EmployeePosition.MANAGER])
CurrentEmployee = Annotated[Employee, Depends(inject(role_checker.__call__))]


@router.get(
    path="/all",
    status_code=status.HTTP_200_OK,
)
async def get_all_clients(
        interactor: FromDishka[ReadAllClientCommandHandler],
        current_employee: CurrentEmployee,
        limit: int = Query(200, ge=1, le=1000),
        offset: int = Query(0, ge=0),
) -> PaginatedClientResponse:
    logger.info("ReadAll clients endpoint called", limit=limit, offset=offset)
    dto = ReadAllClientCommand(limit=limit, offset=offset)
    result = await interactor.run(dto, current_employee)
    logger.info("ReadAll clients successfully", total=result.total)
    return result


@router.post(
    path="/create",
    status_code=status.HTTP_201_CREATED,
)
async def create_client(
        request_data: CreateClientSchema,
        interactor: FromDishka[CreateClientCommandHandler],
        current_employee: CurrentEmployee,
) -> CreateClientCommandResponse:
    logger.info("Create client endpoint called", phone=request_data.phone)
    dto = CreateClientCommand(
        full_name=request_data.full_name,
        phone=request_data.phone,
        email=request_data.email,
        telegram_nick=request_data.telegram_nick,
        comment=request_data.comment,
        address=request_data.address,
    )
    result = await interactor.run(dto)
    logger.info("Client created successfully")
    return result


@router.patch(
    path="/update/{client_uuid}",
    status_code=status.HTTP_200_OK,
)
async def update_client(
        client_uuid: UUID,
        request_data: UpdateClientSchema,
        interactor: FromDishka[UpdateClientCommandHandler],
        current_employee: CurrentEmployee,
) -> None:
    logger.info("Update client endpoint called", client_uuid=str(client_uuid))
    update_data = request_data.model_dump(exclude_unset=True)
    dto = UpdateClientCommand(
        uuid=client_uuid,
        **update_data
    )
    await interactor.run(dto, current_employee)
    logger.info("Client updated successfully", client_uuid=str(client_uuid))


@router.get(
    path="/{client_uuid}",
    status_code=status.HTTP_200_OK,
)
async def get_client(
        client_uuid: UUID,
        interactor: FromDishka[ReadClientCommandHandler],
        current_employee: CurrentEmployee,
) -> ReadClientResponse:
    logger.info("Read client endpoint called", client_uuid=str(client_uuid))
    dto = ReadClientCommand(uuid=client_uuid)
    result = await interactor.run(dto, current_employee)
    logger.info("Read client successfully", client_uuid=str(client_uuid))
    return result


@router.delete(
    path="/{client_uuid}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_client(
        client_uuid: UUID,
        interactor: FromDishka[DeleteClientCommandHandler],
        current_employee: CurrentEmployee,
) -> None:
    logger.info("Delete client endpoint called", client_uuid=str(client_uuid))
    dto = DeleteClientCommand(uuid=client_uuid)
    await interactor.run(dto, current_employee)
    logger.info("Client deleted successfully", client_uuid=str(client_uuid))
