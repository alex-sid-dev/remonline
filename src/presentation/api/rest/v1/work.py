from typing import List, Annotated
import structlog
from fastapi import APIRouter, Depends, status
from dishka import FromDishka
from dishka.integrations.fastapi import inject, DishkaRoute
from uuid import UUID

from src.application.commands.work.create_work import CreateWorkCommandHandler, CreateWorkCommand
from src.application.commands.work.read_all_work import ReadAllWorkCommandHandler, ReadAllWorkCommand, ReadWorkResponse
from src.application.commands.work.read_work import ReadWorkCommandHandler, ReadWorkCommand
from src.application.commands.work.update_work import UpdateWorkCommandHandler, UpdateWorkCommand
from src.application.commands.work.delete_work import DeleteWorkCommandHandler, DeleteWorkCommand
from src.entities.employees.models import Employee, EmployeePosition
from src.presentation.api.common.schemas.work.create_work import CreateWorkSchema, UpdateWorkSchema
from src.presentation.api.rest.v1.permissions import RoleChecker

router = APIRouter(prefix="/work", tags=["Work"], route_class=DishkaRoute)

logger = structlog.get_logger("api.work").bind(service="work")

role_checker = RoleChecker([EmployeePosition.SUPERVISOR, EmployeePosition.ADMIN, EmployeePosition.MASTER, EmployeePosition.MANAGER])
CurrentEmployee = Annotated[Employee, Depends(inject(role_checker.__call__))]

@router.get(
    path="/all",
    status_code=status.HTTP_200_OK,
)
async def get_all_works(
        interactor: FromDishka[ReadAllWorkCommandHandler],
        current_employee: CurrentEmployee,
) -> List[ReadWorkResponse]:
    logger.info("ReadAll works endpoint called")
    dto = ReadAllWorkCommand()
    result = await interactor.run(dto, current_employee)
    logger.info("ReadAll works successfully")
    return result

@router.post(
    path="/create",
    status_code=status.HTTP_201_CREATED,
)
async def create_work(
        request_data: CreateWorkSchema,
        interactor: FromDishka[CreateWorkCommandHandler],
        current_employee: CurrentEmployee,
) -> None:
    logger.info("Create work endpoint called", title=request_data.title)
    dto = CreateWorkCommand(
        order_uuid=request_data.order_uuid,
        title=request_data.title,
        employee_uuid=request_data.employee_uuid,
        description=request_data.description,
        price=request_data.price
    )
    await interactor.run(dto, current_employee)
    logger.info("Work created successfully")

@router.patch(
    path="/update/{work_uuid}",
    status_code=status.HTTP_200_OK,
)
async def update_work(
        work_uuid: UUID,
        request_data: UpdateWorkSchema,
        interactor: FromDishka[UpdateWorkCommandHandler],
        current_employee: CurrentEmployee,
) -> None:
    logger.info("Update work endpoint called", work_uuid=str(work_uuid))
    update_data = request_data.model_dump(exclude_unset=True)
    dto = UpdateWorkCommand(
        uuid=work_uuid,
        **update_data
    )
    await interactor.run(dto, current_employee)
    logger.info("Work updated successfully", work_uuid=str(work_uuid))

@router.get(
    path="/{work_uuid}",
    status_code=status.HTTP_200_OK,
)
async def get_work(
        work_uuid: UUID,
        interactor: FromDishka[ReadWorkCommandHandler],
        current_employee: CurrentEmployee,
) -> ReadWorkResponse:
    logger.info("Read work endpoint called", work_uuid=str(work_uuid))
    dto = ReadWorkCommand(uuid=work_uuid)
    result = await interactor.run(dto, current_employee)
    logger.info("Read work successfully", work_uuid=str(work_uuid))
    return result

@router.delete(
    path="/{work_uuid}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_work(
        work_uuid: UUID,
        interactor: FromDishka[DeleteWorkCommandHandler],
        current_employee: CurrentEmployee,
) -> None:
    logger.info("Delete work endpoint called", work_uuid=str(work_uuid))
    dto = DeleteWorkCommand(uuid=work_uuid)
    await interactor.run(dto, current_employee)
    logger.info("Work deleted successfully", work_uuid=str(work_uuid))
