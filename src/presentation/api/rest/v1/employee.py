import structlog
from dishka import FromDishka

from dishka.integrations.fastapi import DishkaRoute, inject
from fastapi import APIRouter, Depends
from starlette import status

from src.application.commands.employee.create_employee import CreateEmployeeCommand, CreateEmployeeCommandHandler
from src.application.commands.employee.read_all_employee import ReadAllEmployeeCommandHandler, ReadAllEmployeeCommand
from src.application.commands.employee.update_employee import UpdateEmployeeCommand, UpdateEmployeeCommandHandler
from src.entities.employees.enum import EmployeePosition
from src.presentation.api.common.dependencies import CredentialsDependency
from src.presentation.api.common.schemas.employee.create_employee import CreateEmployeeSchema
from src.presentation.api.common.schemas.employee.update_employee import UpdateEmployeeSchema
from src.presentation.api.rest.v1.permissions import RoleChecker

router = APIRouter(prefix="/employee", tags=["Employee"], route_class=DishkaRoute)

logger = structlog.get_logger("api.employee").bind(service="employee")

health_checker = RoleChecker([EmployeePosition.SUPERVISOR, EmployeePosition.ADMIN])

@router.get(
    path="/all_employee",
    dependencies=[Depends(inject(health_checker.__call__))],
    status_code=status.HTTP_200_OK,
)
async def get_all_employees(
        interactor: FromDishka[ReadAllEmployeeCommandHandler],
        credentials: CredentialsDependency,
) -> None:
    logger.info("ReadAll employees endpoint called")
    dto = ReadAllEmployeeCommand(
        access_token=credentials.credentials,
    )
    result = await interactor.run(dto)
    logger.info("ReadAll employees successfully")
    return result



@router.post(
    path="/create_employee",
    dependencies=[Depends(inject(health_checker.__call__))],
    status_code=status.HTTP_201_CREATED,
)
async def create_employee(
        request_data: CreateEmployeeSchema,
        interactor: FromDishka[CreateEmployeeCommandHandler],
        credentials: CredentialsDependency,
) -> None:
    logger.info("Create employee endpoint called", email=str(request_data.phone))
    dto = CreateEmployeeCommand(
        user_id=request_data.user_id,
        full_name=request_data.full_name,
        phone=request_data.phone,
        position=request_data.position,
        access_token=credentials.credentials
    )
    result = await interactor.run(dto)
    logger.info("Create employee registered successfully", email=str(request_data.phone))
    return result


@router.patch(
    path="/update_employee/{employee_id}",
    dependencies=[Depends(inject(health_checker.__call__))],
    status_code=status.HTTP_200_OK,
)
async def update_employee(
        employee_id: int,
        request_data: UpdateEmployeeSchema,
        interactor: FromDishka[UpdateEmployeeCommandHandler],
        credentials: CredentialsDependency,
) -> None:
    logger.info("Update employee endpoint called", email=str(request_data.phone))
    update_data = request_data.model_dump(exclude_unset=True)
    dto = UpdateEmployeeCommand(
        employee_id=employee_id,
        access_token=credentials.credentials,
        **update_data

    )
    result = await interactor.run(dto)
    logger.info("Update employee registered successfully", email=str(request_data.phone))
    return result
