from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest
from src.application.commands.client.read_all_client import (
    PaginatedClientResponse,
    ReadAllClientCommand,
    ReadAllClientCommandHandler,
)
from src.application.commands.employee.change_password import (
    ChangePasswordCommand,
    ChangePasswordCommandHandler,
)
from src.application.commands.employee.read_all_employee import (
    PaginatedEmployeeResponse,
    ReadAllEmployeeCommand,
    ReadAllEmployeeCommandHandler,
)
from src.application.commands.employee.update_employee import (
    UpdateEmployeeCommand,
    UpdateEmployeeCommandHandler,
)
from src.application.commands.order.read_all_order import (
    PaginatedOrderResponse,
    ReadAllOrderCommand,
    ReadAllOrderCommandHandler,
)
from src.application.commands.order.update_order import (
    UpdateOrderCommand,
    UpdateOrderCommandHandler,
)
from src.application.commands.part.read_all_part import (
    PaginatedPartResponse,
    ReadAllPartCommand,
    ReadAllPartCommandHandler,
)
from src.application.errors._base import EntityNotFoundError, PermissionDeniedError
from src.application.errors.employee import EmployeeNotFoundError
from src.entities.clients.models import Client, ClientID, ClientUUID
from src.entities.devices.models import DeviceID
from src.entities.employees.enum import EmployeePosition
from src.entities.employees.models import Employee, EmployeeID, EmployeeUUID
from src.entities.orders.enum import OrderStatus
from src.entities.orders.models import Order, OrderID, OrderUUID
from src.entities.orders.services import OrderService
from src.entities.parts.models import Part, PartID, PartUUID
from src.entities.users.models import User, UserID, UserUUID
from src.entities.works.models import Work, WorkID, WorkUUID

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_employee(
    position=EmployeePosition.SUPERVISOR,
    user_id=1,
    employee_id=1,
):
    return Employee(
        id=EmployeeID(employee_id),
        uuid=EmployeeUUID(uuid4()),
        user_id=UserID(user_id),
        full_name="Test Employee",
        phone="+71234567890",
        position=position,
        is_active=True,
    )


def _make_order(order_id=1):
    return Order(
        id=OrderID(order_id),
        uuid=OrderUUID(uuid4()),
        client_id=ClientID(1),
        device_id=DeviceID(2),
        creator_id=EmployeeID(1),
        assigned_employee_id=None,
        status=OrderStatus.NEW,
        problem_description="test problem",
        price=None,
        is_active=True,
    )


def _make_client(client_id=1):
    return Client(
        id=ClientID(client_id),
        uuid=ClientUUID(uuid4()),
        full_name="Test Client",
        phone="+71234567890",
    )


def _make_part(part_id=1):
    return Part(
        id=PartID(part_id),
        uuid=PartUUID(uuid4()),
        name="Test Part",
        sku="SKU-001",
        price=150.0,
        stock_qty=10,
    )


def _make_work(order_id=1, work_id=1, employee_id=None):
    return Work(
        id=WorkID(work_id),
        uuid=WorkUUID(uuid4()),
        order_id=OrderID(order_id),
        title="Test work",
        employee_id=EmployeeID(employee_id) if employee_id else None,
    )


def _make_user(user_id=1):
    return User(
        id=UserID(user_id),
        uuid=UserUUID(uuid4()),
        email="user@example.com",
        is_active=True,
    )


# ===================================================================
# ReadAll pagination tests
# ===================================================================


class TestReadAllOrderCommandHandler:
    @pytest.mark.asyncio
    async def test_returns_paginated_response(self):
        order = _make_order()
        mock_reader = AsyncMock()
        mock_reader.read_all_active.return_value = ([order], 1)

        handler = ReadAllOrderCommandHandler(order_reader=mock_reader)
        result = await handler.run(
            ReadAllOrderCommand(limit=50, offset=0),
            _make_employee(),
        )

        assert isinstance(result, PaginatedOrderResponse)
        assert result.total == 1
        assert result.limit == 50
        assert result.offset == 0
        assert len(result.items) == 1
        mock_reader.read_all_active.assert_awaited_once_with(50, 0)

    @pytest.mark.asyncio
    async def test_default_pagination(self):
        mock_reader = AsyncMock()
        mock_reader.read_all_active.return_value = ([], 0)

        handler = ReadAllOrderCommandHandler(order_reader=mock_reader)
        result = await handler.run(ReadAllOrderCommand(), _make_employee())

        assert result.total == 0
        assert result.limit == 200
        assert result.offset == 0
        mock_reader.read_all_active.assert_awaited_once_with(200, 0)

    @pytest.mark.asyncio
    async def test_custom_offset(self):
        mock_reader = AsyncMock()
        mock_reader.read_all_active.return_value = ([], 0)

        handler = ReadAllOrderCommandHandler(order_reader=mock_reader)
        result = await handler.run(
            ReadAllOrderCommand(limit=10, offset=30),
            _make_employee(),
        )

        assert result.offset == 30
        assert result.limit == 10
        mock_reader.read_all_active.assert_awaited_once_with(10, 30)


class TestReadAllClientCommandHandler:
    @pytest.mark.asyncio
    async def test_returns_paginated_response(self):
        client = _make_client()
        mock_reader = AsyncMock()
        mock_reader.read_all_active.return_value = ([client], 1)

        handler = ReadAllClientCommandHandler(client_reader=mock_reader)
        result = await handler.run(
            ReadAllClientCommand(limit=100, offset=10),
            _make_employee(),
        )

        assert isinstance(result, PaginatedClientResponse)
        assert result.total == 1
        assert result.limit == 100
        assert result.offset == 10
        assert len(result.items) == 1
        mock_reader.read_all_active.assert_awaited_once_with(100, 10)

    @pytest.mark.asyncio
    async def test_default_pagination(self):
        mock_reader = AsyncMock()
        mock_reader.read_all_active.return_value = ([], 0)

        handler = ReadAllClientCommandHandler(client_reader=mock_reader)
        result = await handler.run(ReadAllClientCommand(), _make_employee())

        assert result.total == 0
        assert result.limit == 200
        assert result.offset == 0


class TestReadAllEmployeeCommandHandler:
    @pytest.mark.asyncio
    async def test_returns_paginated_response(self):
        emp = _make_employee()
        mock_reader = AsyncMock()
        mock_reader.read_all_active.return_value = ([emp], 1)

        handler = ReadAllEmployeeCommandHandler(employee_reader=mock_reader)
        result = await handler.run(ReadAllEmployeeCommand(), _make_employee())

        assert isinstance(result, PaginatedEmployeeResponse)
        assert result.total == 1
        assert len(result.items) == 1

    @pytest.mark.asyncio
    async def test_pagination_params_forwarded(self):
        mock_reader = AsyncMock()
        mock_reader.read_all_active.return_value = ([], 0)

        handler = ReadAllEmployeeCommandHandler(employee_reader=mock_reader)
        result = await handler.run(
            ReadAllEmployeeCommand(limit=25, offset=5),
            _make_employee(),
        )

        assert result.limit == 25
        assert result.offset == 5
        mock_reader.read_all_active.assert_awaited_once_with(25, 5)


class TestReadAllPartCommandHandler:
    @pytest.mark.asyncio
    async def test_returns_paginated_response(self):
        part = _make_part()
        mock_reader = AsyncMock()
        mock_reader.read_all_active.return_value = ([part], 1)

        handler = ReadAllPartCommandHandler(part_reader=mock_reader)
        result = await handler.run(ReadAllPartCommand(), _make_employee())

        assert isinstance(result, PaginatedPartResponse)
        assert result.total == 1
        assert len(result.items) == 1

    @pytest.mark.asyncio
    async def test_pagination_params_forwarded(self):
        mock_reader = AsyncMock()
        mock_reader.read_all_active.return_value = ([], 0)

        handler = ReadAllPartCommandHandler(part_reader=mock_reader)
        result = await handler.run(
            ReadAllPartCommand(limit=15, offset=3),
            _make_employee(),
        )

        assert result.limit == 15
        assert result.offset == 3
        mock_reader.read_all_active.assert_awaited_once_with(15, 3)


# ===================================================================
# UpdateOrderCommandHandler tests
# ===================================================================


class TestUpdateOrderCommandHandler:
    def _make_handler(self, *, order=None, employee=None, works=None):
        mock_transaction = AsyncMock()
        mock_order_reader = AsyncMock()
        mock_employee_reader = AsyncMock()
        mock_work_reader = AsyncMock()

        mock_order_reader.read_by_uuid.return_value = order
        mock_employee_reader.read_by_uuid.return_value = employee
        mock_work_reader.read_by_order_id.return_value = works or []

        handler = UpdateOrderCommandHandler(
            transaction=mock_transaction,
            order_reader=mock_order_reader,
            order_service=OrderService(),
            employee_reader=mock_employee_reader,
            work_reader=mock_work_reader,
        )
        return handler, mock_transaction, mock_order_reader, mock_employee_reader

    @pytest.mark.asyncio
    async def test_order_not_found_raises_error(self):
        handler, *_ = self._make_handler(order=None)

        with pytest.raises(EntityNotFoundError):
            await handler.run(
                UpdateOrderCommand(uuid=uuid4(), status="accepted"),
                _make_employee(),
            )

    @pytest.mark.asyncio
    async def test_successful_status_update(self):
        order = _make_order()
        handler, mock_tx, *_ = self._make_handler(order=order)

        await handler.run(
            UpdateOrderCommand(uuid=order.uuid, status="accepted"),
            _make_employee(),
        )

        assert order.status == OrderStatus.ACCEPTED
        mock_tx.commit.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_assign_employee_not_found(self):
        order = _make_order()
        handler, *_ = self._make_handler(order=order, employee=None)

        with pytest.raises(EntityNotFoundError):
            await handler.run(
                UpdateOrderCommand(uuid=order.uuid, assigned_employee_uuid=uuid4()),
                _make_employee(),
            )

    @pytest.mark.asyncio
    async def test_assign_employee_updates_order(self):
        order = _make_order()
        assigned = _make_employee(
            position=EmployeePosition.MASTER,
            employee_id=5,
        )
        handler, mock_tx, *_ = self._make_handler(
            order=order,
            employee=assigned,
            works=[],
        )

        await handler.run(
            UpdateOrderCommand(uuid=order.uuid, assigned_employee_uuid=assigned.uuid),
            _make_employee(),
        )

        assert order.assigned_employee_id == EmployeeID(5)
        mock_tx.commit.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_auto_assigns_engineer_to_unassigned_works(self):
        order = _make_order()
        assigned = _make_employee(
            position=EmployeePosition.MASTER,
            employee_id=5,
        )
        unassigned_work = _make_work(order_id=order.id, employee_id=None)
        already_assigned_work = _make_work(
            order_id=order.id,
            work_id=2,
            employee_id=3,
        )

        handler, mock_tx, _, _ = self._make_handler(
            order=order,
            employee=assigned,
            works=[unassigned_work, already_assigned_work],
        )

        await handler.run(
            UpdateOrderCommand(uuid=order.uuid, assigned_employee_uuid=assigned.uuid),
            _make_employee(),
        )

        assert unassigned_work.employee_id == EmployeeID(5)
        assert already_assigned_work.employee_id == EmployeeID(3)

    @pytest.mark.asyncio
    async def test_update_price(self):
        order = _make_order()
        handler, mock_tx, *_ = self._make_handler(order=order)

        await handler.run(
            UpdateOrderCommand(uuid=order.uuid, price=999.0),
            _make_employee(),
        )

        assert order.price == 999.0
        mock_tx.commit.assert_awaited_once()


# ===================================================================
# UpdateEmployeeCommandHandler – permission tests
# ===================================================================


class TestUpdateEmployeePermissions:
    def _make_handler(self, *, target_employee=None):
        mock_transaction = AsyncMock()
        mock_employee_reader = AsyncMock()
        mock_employee_service = MagicMock()
        mock_employee_service.update_employee.side_effect = lambda employee, **kw: employee
        mock_employee_reader.read_by_uuid.return_value = target_employee

        handler = UpdateEmployeeCommandHandler(
            transaction=mock_transaction,
            employee_reader=mock_employee_reader,
            employee_service=mock_employee_service,
        )
        return handler, mock_transaction, mock_employee_service

    @pytest.mark.asyncio
    async def test_admin_cannot_update_supervisor(self):
        supervisor = _make_employee(
            position=EmployeePosition.SUPERVISOR,
            employee_id=2,
        )
        handler, *_ = self._make_handler(target_employee=supervisor)
        admin = _make_employee(position=EmployeePosition.ADMIN, employee_id=1)

        with pytest.raises(PermissionDeniedError):
            await handler.run(
                UpdateEmployeeCommand(uuid=supervisor.uuid, full_name="New Name"),
                admin,
            )

    @pytest.mark.asyncio
    async def test_admin_cannot_update_other_admin(self):
        other_admin = _make_employee(
            position=EmployeePosition.ADMIN,
            employee_id=2,
        )
        handler, *_ = self._make_handler(target_employee=other_admin)
        admin = _make_employee(position=EmployeePosition.ADMIN, employee_id=1)

        with pytest.raises(PermissionDeniedError):
            await handler.run(
                UpdateEmployeeCommand(uuid=other_admin.uuid, full_name="New Name"),
                admin,
            )

    @pytest.mark.asyncio
    async def test_admin_can_update_master(self):
        master = _make_employee(
            position=EmployeePosition.MASTER,
            employee_id=2,
        )
        handler, mock_tx, mock_service = self._make_handler(
            target_employee=master,
        )
        admin = _make_employee(position=EmployeePosition.ADMIN, employee_id=1)

        await handler.run(
            UpdateEmployeeCommand(uuid=master.uuid, full_name="Updated Name"),
            admin,
        )

        mock_service.update_employee.assert_called_once()
        mock_tx.commit.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_admin_can_update_manager(self):
        manager = _make_employee(
            position=EmployeePosition.MANAGER,
            employee_id=3,
        )
        handler, mock_tx, mock_service = self._make_handler(
            target_employee=manager,
        )
        admin = _make_employee(position=EmployeePosition.ADMIN, employee_id=1)

        await handler.run(
            UpdateEmployeeCommand(uuid=manager.uuid, phone="+79990001122"),
            admin,
        )

        mock_service.update_employee.assert_called_once()
        mock_tx.commit.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_supervisor_can_update_any_employee(self):
        admin_target = _make_employee(
            position=EmployeePosition.ADMIN,
            employee_id=2,
        )
        handler, mock_tx, mock_service = self._make_handler(
            target_employee=admin_target,
        )
        supervisor = _make_employee(
            position=EmployeePosition.SUPERVISOR,
            employee_id=1,
        )

        await handler.run(
            UpdateEmployeeCommand(uuid=admin_target.uuid, full_name="Changed"),
            supervisor,
        )

        mock_service.update_employee.assert_called_once()
        mock_tx.commit.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_only_supervisor_can_change_salary(self):
        master = _make_employee(
            position=EmployeePosition.MASTER,
            employee_id=2,
        )
        handler, *_ = self._make_handler(target_employee=master)
        admin = _make_employee(position=EmployeePosition.ADMIN, employee_id=1)

        with pytest.raises(PermissionDeniedError):
            await handler.run(
                UpdateEmployeeCommand(uuid=master.uuid, salary=70000.0),
                admin,
            )

    @pytest.mark.asyncio
    async def test_supervisor_can_change_salary(self):
        master = _make_employee(
            position=EmployeePosition.MASTER,
            employee_id=2,
        )
        handler, mock_tx, mock_service = self._make_handler(
            target_employee=master,
        )
        supervisor = _make_employee(
            position=EmployeePosition.SUPERVISOR,
            employee_id=1,
        )

        await handler.run(
            UpdateEmployeeCommand(
                uuid=master.uuid,
                salary=80000.0,
                profit_percent=12.0,
            ),
            supervisor,
        )

        mock_service.update_employee.assert_called_once()
        mock_tx.commit.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_employee_not_found(self):
        handler, *_ = self._make_handler(target_employee=None)
        supervisor = _make_employee(
            position=EmployeePosition.SUPERVISOR,
            employee_id=1,
        )

        with pytest.raises(EmployeeNotFoundError):
            await handler.run(
                UpdateEmployeeCommand(uuid=uuid4(), full_name="X"),
                supervisor,
            )

    @pytest.mark.asyncio
    async def test_admin_cannot_set_supervisor_position(self):
        master = _make_employee(
            position=EmployeePosition.MASTER,
            employee_id=2,
        )
        handler, *_ = self._make_handler(target_employee=master)
        admin = _make_employee(position=EmployeePosition.ADMIN, employee_id=1)

        with pytest.raises(PermissionDeniedError):
            await handler.run(
                UpdateEmployeeCommand(
                    uuid=master.uuid,
                    position=EmployeePosition.SUPERVISOR,
                ),
                admin,
            )


# ===================================================================
# ChangePasswordCommandHandler tests
# ===================================================================


class TestChangePasswordCommandHandler:
    def _make_handler(self, *, target_employee=None, user=None):
        mock_employee_reader = AsyncMock()
        mock_user_reader = AsyncMock()
        mock_admin_manager = AsyncMock()

        mock_employee_reader.read_by_uuid.return_value = target_employee
        mock_user_reader.read_by_id.return_value = user

        handler = ChangePasswordCommandHandler(
            employee_reader=mock_employee_reader,
            user_reader=mock_user_reader,
            admin_manager=mock_admin_manager,
        )
        return handler, mock_admin_manager

    @pytest.mark.asyncio
    async def test_supervisor_can_change_any_password(self):
        target = _make_employee(
            position=EmployeePosition.ADMIN,
            employee_id=2,
            user_id=2,
        )
        user = _make_user(user_id=2)
        handler, mock_admin = self._make_handler(
            target_employee=target,
            user=user,
        )
        supervisor = _make_employee(
            position=EmployeePosition.SUPERVISOR,
            employee_id=1,
        )

        await handler.run(
            ChangePasswordCommand(employee_uuid=target.uuid, new_password="newpass123"),
            supervisor,
        )

        mock_admin.update_password.assert_awaited_once_with(
            str(user.uuid),
            "newpass123",
        )

    @pytest.mark.asyncio
    async def test_admin_can_change_master_password(self):
        target = _make_employee(
            position=EmployeePosition.MASTER,
            employee_id=3,
            user_id=3,
        )
        user = _make_user(user_id=3)
        handler, mock_admin = self._make_handler(
            target_employee=target,
            user=user,
        )
        admin = _make_employee(position=EmployeePosition.ADMIN, employee_id=1)

        await handler.run(
            ChangePasswordCommand(employee_uuid=target.uuid, new_password="secret"),
            admin,
        )

        mock_admin.update_password.assert_awaited_once_with(
            str(user.uuid),
            "secret",
        )

    @pytest.mark.asyncio
    async def test_admin_can_change_manager_password(self):
        target = _make_employee(
            position=EmployeePosition.MANAGER,
            employee_id=4,
            user_id=4,
        )
        user = _make_user(user_id=4)
        handler, mock_admin = self._make_handler(
            target_employee=target,
            user=user,
        )
        admin = _make_employee(position=EmployeePosition.ADMIN, employee_id=1)

        await handler.run(
            ChangePasswordCommand(employee_uuid=target.uuid, new_password="s3cret"),
            admin,
        )

        mock_admin.update_password.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_admin_cannot_change_supervisor_password(self):
        target = _make_employee(
            position=EmployeePosition.SUPERVISOR,
            employee_id=2,
            user_id=2,
        )
        handler, _ = self._make_handler(target_employee=target)
        admin = _make_employee(position=EmployeePosition.ADMIN, employee_id=1)

        with pytest.raises(PermissionDeniedError):
            await handler.run(
                ChangePasswordCommand(
                    employee_uuid=target.uuid,
                    new_password="nope",
                ),
                admin,
            )

    @pytest.mark.asyncio
    async def test_admin_cannot_change_other_admin_password(self):
        target = _make_employee(
            position=EmployeePosition.ADMIN,
            employee_id=2,
            user_id=2,
        )
        handler, _ = self._make_handler(target_employee=target)
        admin = _make_employee(position=EmployeePosition.ADMIN, employee_id=1)

        with pytest.raises(PermissionDeniedError):
            await handler.run(
                ChangePasswordCommand(
                    employee_uuid=target.uuid,
                    new_password="nope",
                ),
                admin,
            )

    @pytest.mark.asyncio
    async def test_master_cannot_change_password(self):
        target = _make_employee(
            position=EmployeePosition.MANAGER,
            employee_id=2,
            user_id=2,
        )
        handler, _ = self._make_handler(target_employee=target)
        master = _make_employee(
            position=EmployeePosition.MASTER,
            employee_id=3,
        )

        with pytest.raises(PermissionDeniedError):
            await handler.run(
                ChangePasswordCommand(
                    employee_uuid=target.uuid,
                    new_password="nope",
                ),
                master,
            )

    @pytest.mark.asyncio
    async def test_target_employee_not_found(self):
        handler, _ = self._make_handler(target_employee=None)
        supervisor = _make_employee(
            position=EmployeePosition.SUPERVISOR,
            employee_id=1,
        )

        with pytest.raises(EntityNotFoundError):
            await handler.run(
                ChangePasswordCommand(employee_uuid=uuid4(), new_password="x"),
                supervisor,
            )

    @pytest.mark.asyncio
    async def test_linked_user_not_found(self):
        target = _make_employee(
            position=EmployeePosition.MASTER,
            employee_id=2,
            user_id=2,
        )
        handler, _ = self._make_handler(target_employee=target, user=None)
        supervisor = _make_employee(
            position=EmployeePosition.SUPERVISOR,
            employee_id=1,
        )

        with pytest.raises(EntityNotFoundError):
            await handler.run(
                ChangePasswordCommand(
                    employee_uuid=target.uuid,
                    new_password="pass",
                ),
                supervisor,
            )


# ===================================================================
# Close order permission tests
# ===================================================================

from src.application.commands.statistics.get_statistics import (
    GetStatisticsCommandHandler,
    StatisticsResponse,
)
from src.application.ports.statistics_reader import OrderStatRow


class TestCloseOrderPermission:
    def _make_handler(self, *, order=None, employee=None, works=None):
        mock_transaction = AsyncMock()
        mock_order_reader = AsyncMock()
        mock_employee_reader = AsyncMock()
        mock_work_reader = AsyncMock()

        mock_order_reader.read_by_uuid.return_value = order
        mock_employee_reader.read_by_uuid.return_value = employee
        mock_work_reader.read_by_order_id.return_value = works or []

        handler = UpdateOrderCommandHandler(
            transaction=mock_transaction,
            order_reader=mock_order_reader,
            order_service=OrderService(),
            employee_reader=mock_employee_reader,
            work_reader=mock_work_reader,
        )
        return handler, mock_transaction

    @pytest.mark.asyncio
    async def test_supervisor_can_close_order(self):
        order = _make_order()
        handler, mock_tx = self._make_handler(order=order)
        supervisor = _make_employee(position=EmployeePosition.SUPERVISOR)

        await handler.run(
            UpdateOrderCommand(uuid=order.uuid, status="closed"),
            supervisor,
        )

        assert order.status == OrderStatus.CLOSED
        mock_tx.commit.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_admin_cannot_close_order(self):
        order = _make_order()
        handler, _ = self._make_handler(order=order)
        admin = _make_employee(position=EmployeePosition.ADMIN)

        with pytest.raises(PermissionDeniedError):
            await handler.run(
                UpdateOrderCommand(uuid=order.uuid, status="closed"),
                admin,
            )

    @pytest.mark.asyncio
    async def test_manager_cannot_close_order(self):
        order = _make_order()
        handler, _ = self._make_handler(order=order)
        manager = _make_employee(position=EmployeePosition.MANAGER)

        with pytest.raises(PermissionDeniedError):
            await handler.run(
                UpdateOrderCommand(uuid=order.uuid, status="closed"),
                manager,
            )

    @pytest.mark.asyncio
    async def test_master_cannot_close_order(self):
        order = _make_order()
        handler, _ = self._make_handler(order=order)
        master = _make_employee(position=EmployeePosition.MASTER)

        with pytest.raises(PermissionDeniedError):
            await handler.run(
                UpdateOrderCommand(uuid=order.uuid, status="closed"),
                master,
            )

    @pytest.mark.asyncio
    async def test_non_closed_status_allowed_for_all_roles(self):
        """Admin, Manager, Master can still change to non-closed statuses."""
        for pos in (EmployeePosition.ADMIN, EmployeePosition.MANAGER, EmployeePosition.MASTER):
            order = _make_order()
            handler, mock_tx = self._make_handler(order=order)
            emp = _make_employee(position=pos)

            await handler.run(
                UpdateOrderCommand(uuid=order.uuid, status="accepted"),
                emp,
            )
            assert order.status == OrderStatus.ACCEPTED


# ===================================================================
# Statistics calculation tests
# ===================================================================


class TestGetStatisticsCommandHandler:
    def _make_handler(self, *, order_rows=None, employees=None):
        mock_stats_reader = AsyncMock()
        mock_stats_reader.get_closed_orders_stats.return_value = order_rows or []

        mock_employee_reader = AsyncMock()
        mock_employee_reader.read_all_active.return_value = (employees or [], len(employees or []))

        handler = GetStatisticsCommandHandler(
            statistics_reader=mock_stats_reader,
            employee_reader=mock_employee_reader,
        )
        return handler

    @pytest.mark.asyncio
    async def test_empty_statistics(self):
        handler = self._make_handler(order_rows=[], employees=[])
        result = await handler.run(_make_employee())

        assert isinstance(result, StatisticsResponse)
        assert result.total_orders == 0
        assert result.total_revenue == 0.0
        assert result.total_expenses == 0.0
        assert result.net_profit == 0.0
        assert result.employees == []

    @pytest.mark.asyncio
    async def test_company_totals(self):
        rows = [
            OrderStatRow(
                order_id=1,
                creator_id=10,
                assigned_employee_id=20,
                works_revenue=1000.0,
                parts_expenses=300.0,
            ),
            OrderStatRow(
                order_id=2,
                creator_id=10,
                assigned_employee_id=20,
                works_revenue=500.0,
                parts_expenses=100.0,
            ),
        ]
        handler = self._make_handler(order_rows=rows, employees=[])
        result = await handler.run(_make_employee())

        assert result.total_orders == 2
        assert result.total_revenue == 1900.0  # (1000+300) + (500+100)
        assert result.total_expenses == 400.0  # 300 + 100
        assert result.net_profit == 1500.0  # 1900 - 400

    @pytest.mark.asyncio
    async def test_supervisor_sees_all_orders(self):
        rows = [
            OrderStatRow(
                order_id=1,
                creator_id=10,
                assigned_employee_id=20,
                works_revenue=1000.0,
                parts_expenses=200.0,
            ),
            OrderStatRow(
                order_id=2,
                creator_id=11,
                assigned_employee_id=21,
                works_revenue=500.0,
                parts_expenses=100.0,
            ),
        ]
        sup = _make_employee(position=EmployeePosition.SUPERVISOR, employee_id=99)
        handler = self._make_handler(order_rows=rows, employees=[sup])
        result = await handler.run(sup)

        emp_stat = result.employees[0]
        assert emp_stat.orders_count == 2
        assert emp_stat.revenue == 1800.0  # (1000+200) + (500+100)
        assert emp_stat.expenses == 300.0  # 200 + 100
        assert emp_stat.net_profit == 1500.0  # 1800 - 300

    @pytest.mark.asyncio
    async def test_manager_only_their_orders(self):
        rows = [
            OrderStatRow(
                order_id=1,
                creator_id=10,
                assigned_employee_id=20,
                works_revenue=1000.0,
                parts_expenses=200.0,
            ),
            OrderStatRow(
                order_id=2,
                creator_id=11,
                assigned_employee_id=20,
                works_revenue=500.0,
                parts_expenses=100.0,
            ),
        ]
        manager = _make_employee(position=EmployeePosition.MANAGER, employee_id=10)
        handler = self._make_handler(order_rows=rows, employees=[manager])
        result = await handler.run(manager)

        emp_stat = result.employees[0]
        assert emp_stat.orders_count == 1
        assert emp_stat.revenue == 1200.0  # 1000 + 200
        assert emp_stat.expenses == 200.0
        assert emp_stat.net_profit == 1000.0

    @pytest.mark.asyncio
    async def test_master_only_assigned_orders(self):
        rows = [
            OrderStatRow(
                order_id=1,
                creator_id=10,
                assigned_employee_id=20,
                works_revenue=1000.0,
                parts_expenses=200.0,
            ),
            OrderStatRow(
                order_id=2,
                creator_id=10,
                assigned_employee_id=21,
                works_revenue=500.0,
                parts_expenses=100.0,
            ),
        ]
        master = _make_employee(position=EmployeePosition.MASTER, employee_id=20)
        handler = self._make_handler(order_rows=rows, employees=[master])
        result = await handler.run(master)

        emp_stat = result.employees[0]
        assert emp_stat.orders_count == 1
        assert emp_stat.revenue == 1200.0  # 1000 + 200
        assert emp_stat.expenses == 200.0
        assert emp_stat.net_profit == 1000.0

    @pytest.mark.asyncio
    async def test_salary_calculation(self):
        rows = [
            OrderStatRow(
                order_id=1,
                creator_id=10,
                assigned_employee_id=20,
                works_revenue=2000.0,
                parts_expenses=500.0,
            ),
        ]
        master = Employee(
            id=EmployeeID(20),
            uuid=EmployeeUUID(uuid4()),
            user_id=UserID(2),
            full_name="Master",
            phone="+71234567890",
            position=EmployeePosition.MASTER,
            is_active=True,
            salary=30000.0,
            profit_percent=10.0,
        )
        handler = self._make_handler(order_rows=rows, employees=[master])
        result = await handler.run(master)

        emp_stat = result.employees[0]
        # net_profit = (2000+500) - 500 = 2000
        assert emp_stat.net_profit == 2000.0
        assert emp_stat.base_salary == 30000.0
        assert emp_stat.profit_percent == 10.0
        assert emp_stat.bonus == 200.0  # 10% of 2000
        assert emp_stat.total_salary == 30200.0  # 30000 + 200
