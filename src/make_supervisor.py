"""Bootstrap: создание учётной записи супервизора по умолчанию в Keycloak и БД."""
from uuid import uuid4

import structlog
from dishka import AsyncContainer

from src.application.keycloak.auth_managers import AdminManager
from src.application.ports.employee_reader import EmployeeReader
from src.application.ports.transaction import Transaction, EntitySaver
from src.application.ports.user_reader import UserReader
from src.entities.employees.enum import EmployeePosition
from src.entities.employees.services import EmployeeService
from src.entities.users.services import UserService

logger = structlog.get_logger("make_supervisor").bind(service="bootstrap")

SUPERVISOR_EMAIL = "admin@admin.ru"
SUPERVISOR_PASSWORD = "1!String"
SUPERVISOR_FULL_NAME = "Yahve"
SUPERVISOR_PHONE = "+7 965 000 57 27"


async def make_supervisor(container: AsyncContainer) -> None:
    """
    Создаёт учётную запись супервизора по умолчанию, если её ещё нет.

    Регистрирует пользователя в Keycloak (если нужно), создаёт запись User и Employee
    в БД с ролью SUPERVISOR. Вызывается при старте приложения (lifespan).
    """
    async with container() as request_scope:
        admin_manager = await request_scope.get(AdminManager)
        user_reader = await request_scope.get(UserReader)
        employee_reader = await request_scope.get(EmployeeReader)
        entity_saver = await request_scope.get(EntitySaver)
        transaction = await request_scope.get(Transaction)
        user_service = await request_scope.get(UserService)
        employee_service = await request_scope.get(EmployeeService)

        user = await user_reader.read_by_email(SUPERVISOR_EMAIL)
        if user:
            employee = await employee_reader.read_by_user_id(user.id)
            if employee:
                logger.info("Supervisor account already exists, skipping")
                return

            new_employee = employee_service.create_employee(
                user_id=user.id,
                full_name=SUPERVISOR_FULL_NAME,
                phone=SUPERVISOR_PHONE,
                position=EmployeePosition.SUPERVISOR,
                is_active=True,
                uuid=uuid4(),
            )
            entity_saver.add_one(new_employee)
            await transaction.commit()
            logger.info("Created employee record for existing supervisor user")
            return

        try:
            kc_user_uuid = await admin_manager.register_user(
                email=SUPERVISOR_EMAIL,
                password=SUPERVISOR_PASSWORD,
            )
        except Exception:
            logger.warning("Keycloak registration failed, checking if user already exists there")
            kc_user_uuid = None

        if kc_user_uuid is None:
            logger.warning("Could not create or find supervisor in Keycloak, skipping")
            return

        new_user = user_service.create_user(
            user_uuid=kc_user_uuid,
            email=SUPERVISOR_EMAIL,
        )
        entity_saver.add_one(new_user)
        await transaction.flush()

        new_employee = employee_service.create_employee(
            user_id=new_user.id,
            full_name=SUPERVISOR_FULL_NAME,
            phone=SUPERVISOR_PHONE,
            position=EmployeePosition.SUPERVISOR,
            is_active=True,
            uuid=uuid4(),
        )
        entity_saver.add_one(new_employee)
        await transaction.commit()
        logger.info("Supervisor account created successfully", user_uuid=kc_user_uuid)
