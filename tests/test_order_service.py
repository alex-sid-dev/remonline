from src.entities.orders.services import OrderService
from src.entities.orders.enum import OrderStatus
from src.entities.clients.models import ClientID
from src.entities.devices.models import DeviceID
from src.entities.employees.models import EmployeeID


class TestOrderService:
    def setup_method(self):
        self.service = OrderService()

    def test_create_order_defaults(self):
        order = self.service.create_order(
            client_id=ClientID(1),
            device_id=DeviceID(2),
            creator_id=EmployeeID(3),
        )
        assert order.client_id == ClientID(1)
        assert order.device_id == DeviceID(2)
        assert order.creator_id == EmployeeID(3)
        assert order.status == OrderStatus.NEW
        assert order.is_active is True
        assert order.uuid is not None
        assert order.price is None
        assert order.assigned_employee_id is None

    def test_create_order_with_all_fields(self):
        order = self.service.create_order(
            client_id=ClientID(1),
            device_id=DeviceID(2),
            creator_id=EmployeeID(3),
            assigned_employee_id=EmployeeID(4),
            status=OrderStatus.IN_REPAIR,
            price=100.0,
            problem_description="Screen broken",
        )
        assert order.assigned_employee_id == EmployeeID(4)
        assert order.price == 100.0
        assert order.problem_description == "Screen broken"

    def test_create_order_with_string_status(self):
        order = self.service.create_order(
            client_id=ClientID(1),
            device_id=DeviceID(2),
            creator_id=EmployeeID(3),
            status="new",
        )
        assert order.status == OrderStatus.NEW

    def test_update_order_partial(self):
        order = self.service.create_order(
            client_id=ClientID(1),
            device_id=DeviceID(2),
            creator_id=EmployeeID(3),
        )
        updated = self.service.update_order(order, price=200.0)
        assert updated.price == 200.0
        assert updated.status == OrderStatus.NEW

    def test_update_order_status(self):
        order = self.service.create_order(
            client_id=ClientID(1),
            device_id=DeviceID(2),
            creator_id=EmployeeID(3),
        )
        updated = self.service.update_order(order, status=OrderStatus.CLOSED)
        assert updated.status == OrderStatus.CLOSED

    def test_update_order_deactivate(self):
        order = self.service.create_order(
            client_id=ClientID(1),
            device_id=DeviceID(2),
            creator_id=EmployeeID(3),
        )
        updated = self.service.update_order(order, is_active=False)
        assert updated.is_active is False

    def test_update_order_updated_at_changes(self):
        order = self.service.create_order(
            client_id=ClientID(1),
            device_id=DeviceID(2),
            creator_id=EmployeeID(3),
        )
        original_updated_at = order.updated_at
        updated = self.service.update_order(order, price=50.0)
        assert updated.updated_at >= original_updated_at
