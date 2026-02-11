from dishka import Provider, Scope

from src.entities.employees.services import EmployeeService
from src.entities.users.services import UserService


def services_provider() -> Provider:
    provider = Provider(scope=Scope.REQUEST)
    _ = provider.provide_all(
        UserService,
        EmployeeService,
    )
    return provider