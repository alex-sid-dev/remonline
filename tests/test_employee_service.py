from uuid import uuid4

from src.entities.employees.enum import EmployeePosition
from src.entities.employees.services import EmployeeService
from src.entities.users.models import UserID


class TestEmployeeService:
    def setup_method(self):
        self.service = EmployeeService()

    def test_create_employee(self):
        emp = self.service.create_employee(
            user_id=UserID(1),
            full_name="Test Worker",
            phone="+79001234567",
            position=EmployeePosition.MASTER,
            is_active=True,
            uuid=uuid4(),
        )
        assert emp.full_name == "Test Worker"
        assert emp.position == EmployeePosition.MASTER
        assert emp.is_active is True
        assert emp.user_id == UserID(1)
        assert emp.salary is None
        assert emp.profit_percent is None

    def test_create_employee_with_salary(self):
        emp = self.service.create_employee(
            user_id=UserID(1),
            full_name="Paid Worker",
            phone="+79001234567",
            position=EmployeePosition.MASTER,
            is_active=True,
            uuid=uuid4(),
            salary=50000.0,
            profit_percent=10.5,
        )
        assert emp.salary == 50000.0
        assert emp.profit_percent == 10.5

    def test_create_employee_supervisor(self):
        emp = self.service.create_employee(
            user_id=UserID(2),
            full_name="Admin Boss",
            phone="+79009999999",
            position=EmployeePosition.SUPERVISOR,
            is_active=True,
            uuid=uuid4(),
        )
        assert emp.position == EmployeePosition.SUPERVISOR

    def test_update_employee_name(self):
        emp = self.service.create_employee(
            user_id=UserID(1),
            full_name="Old Name",
            phone="+79001234567",
            position=EmployeePosition.MASTER,
            is_active=True,
            uuid=uuid4(),
        )
        updated = self.service.update_employee(emp, full_name="New Name")
        assert updated.full_name == "New Name"
        assert updated.phone == "+79001234567"

    def test_update_employee_position(self):
        emp = self.service.create_employee(
            user_id=UserID(1),
            full_name="Worker",
            phone="+79001234567",
            position=EmployeePosition.MASTER,
            is_active=True,
            uuid=uuid4(),
        )
        updated = self.service.update_employee(emp, position=EmployeePosition.MANAGER)
        assert updated.position == EmployeePosition.MANAGER

    def test_update_employee_salary(self):
        emp = self.service.create_employee(
            user_id=UserID(1),
            full_name="Worker",
            phone="+79001234567",
            position=EmployeePosition.MASTER,
            is_active=True,
            uuid=uuid4(),
        )
        updated = self.service.update_employee(emp, salary=75000.0)
        assert updated.salary == 75000.0
        assert updated.full_name == "Worker"

    def test_update_employee_profit_percent(self):
        emp = self.service.create_employee(
            user_id=UserID(1),
            full_name="Worker",
            phone="+79001234567",
            position=EmployeePosition.MASTER,
            is_active=True,
            uuid=uuid4(),
            salary=50000.0,
        )
        updated = self.service.update_employee(emp, profit_percent=15.0)
        assert updated.profit_percent == 15.0
        assert updated.salary == 50000.0

    def test_update_employee_none_preserves_values(self):
        emp = self.service.create_employee(
            user_id=UserID(1),
            full_name="Worker",
            phone="+79001234567",
            position=EmployeePosition.MASTER,
            is_active=True,
            uuid=uuid4(),
            salary=60000.0,
            profit_percent=5.0,
        )
        updated = self.service.update_employee(emp)
        assert updated.full_name == "Worker"
        assert updated.phone == "+79001234567"
        assert updated.position == EmployeePosition.MASTER
        assert updated.salary == 60000.0
        assert updated.profit_percent == 5.0
