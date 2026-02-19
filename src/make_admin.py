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

logger = structlog.get_logger("make_admin").bind(service="bootstrap")

ADMIN_EMAIL = "admin@admin.ru"
ADMIN_PASSWORD = "1!String"
ADMIN_FULL_NAME = "Yahve"
ADMIN_PHONE = "+1 000 000 000"


async def make_admin(container: AsyncContainer) -> None:
    """Ensure a default supervisor account exists in Keycloak and the local DB."""
    async with container() as request_scope:
        admin_manager = await request_scope.get(AdminManager)
        user_reader = await request_scope.get(UserReader)
        employee_reader = await request_scope.get(EmployeeReader)
        entity_saver = await request_scope.get(EntitySaver)
        transaction = await request_scope.get(Transaction)
        user_service = await request_scope.get(UserService)
        employee_service = await request_scope.get(EmployeeService)

        user = await user_reader.read_by_email(ADMIN_EMAIL)
        if user:
            employee = await employee_reader.read_by_user_id(user.id)
            if employee:
                logger.info("Admin account already exists, skipping")
                return

            new_employee = employee_service.create_employee(
                user_id=user.id,
                full_name=ADMIN_FULL_NAME,
                phone=ADMIN_PHONE,
                position=EmployeePosition.SUPERVISOR,
                is_active=True,
                uuid=uuid4(),
            )
            entity_saver.add_one(new_employee)
            await transaction.commit()
            logger.info("Created employee record for existing admin user")
            return

        try:
            kc_user_uuid = await admin_manager.register_user(
                email=ADMIN_EMAIL,
                password=ADMIN_PASSWORD,
            )
        except Exception:
            logger.warning("Keycloak registration failed, checking if user already exists there")
            kc_user_uuid = None

        if kc_user_uuid is None:
            logger.warning("Could not create or find admin in Keycloak, skipping")
            return

        new_user = user_service.create_user(
            user_uuid=kc_user_uuid,
            email=ADMIN_EMAIL,
        )
        entity_saver.add_one(new_user)
        await transaction.flush()

        new_employee = employee_service.create_employee(
            user_id=new_user.id,
            full_name=ADMIN_FULL_NAME,
            phone=ADMIN_PHONE,
            position=EmployeePosition.SUPERVISOR,
            is_active=True,
            uuid=uuid4(),
        )
        entity_saver.add_one(new_employee)
        await transaction.commit()
        logger.info("Admin account created successfully", user_uuid=kc_user_uuid)
