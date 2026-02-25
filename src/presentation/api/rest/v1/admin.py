from typing import Annotated

import structlog
from dishka import FromDishka
from dishka.integrations.fastapi import DishkaRoute, inject
from fastapi import APIRouter, Depends, UploadFile
from fastapi.responses import Response
from starlette import status

from src.application.commands.admin.backup_database import BackupDatabaseCommandHandler
from src.application.commands.admin.purge_database import PurgeDatabaseCommandHandler
from src.application.commands.admin.restore_database import RestoreDatabaseCommandHandler
from src.entities.employees.models import Employee, EmployeePosition
from src.presentation.api.rest.v1.permissions import RoleChecker

router = APIRouter(prefix="/admin", tags=["Admin"], route_class=DishkaRoute)

logger = structlog.get_logger("api.admin").bind(service="admin")

supervisor_checker = RoleChecker([EmployeePosition.SUPERVISOR])
SupervisorEmployee = Annotated[Employee, Depends(inject(supervisor_checker.__call__))]


@router.delete(
    path="/purge",
    status_code=status.HTTP_200_OK,
)
async def purge_database(
    interactor: FromDishka[PurgeDatabaseCommandHandler],
    current_employee: SupervisorEmployee,
) -> dict[str, int]:
    logger.warning("Database purge requested", employee=str(current_employee.uuid))
    result = await interactor.run(current_employee)
    logger.warning("Database purged successfully")
    return result


@router.get(
    path="/backup",
    status_code=status.HTTP_200_OK,
)
async def backup_database(
    interactor: FromDishka[BackupDatabaseCommandHandler],
    current_employee: SupervisorEmployee,
) -> Response:
    logger.info("Database backup requested", employee=str(current_employee.uuid))
    data, filename = await interactor.run(current_employee)
    return Response(
        content=data,
        media_type="application/gzip",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.post(
    path="/restore",
    status_code=status.HTTP_200_OK,
)
async def restore_database(
    file: UploadFile,
    interactor: FromDishka[RestoreDatabaseCommandHandler],
    current_employee: SupervisorEmployee,
) -> dict[str, str]:
    logger.warning("Database restore requested", employee=str(current_employee.uuid))
    archive = await file.read()
    await interactor.run(archive, current_employee)
    logger.warning("Database restored successfully")
    return {"status": "ok", "message": "База данных успешно восстановлена из архива."}
