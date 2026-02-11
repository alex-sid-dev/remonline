from dishka import Provider, Scope

from src.application.commands.base.auth.login import LoginCommandHandler
from src.application.commands.base.auth.logout import LogoutCommandHandler
from src.application.commands.base.auth.registration import RegisterCommandHandler
from src.application.commands.base.auth.update_access_token import UpdateAccessTokenCommandHandler
from src.application.commands.employee.create_employee import CreateEmployeeCommandHandler
from src.application.commands.employee.read_all_employee import ReadAllEmployeeCommandHandler
from src.application.commands.employee.update_employee import UpdateEmployeeCommandHandler


def interactors_provider() -> Provider:
    provider = Provider(scope=Scope.REQUEST)
    _ = provider.provide_all(
        RegisterCommandHandler,
        LoginCommandHandler,
        LogoutCommandHandler,
        UpdateAccessTokenCommandHandler,

        ReadAllEmployeeCommandHandler,
        CreateEmployeeCommandHandler,
        UpdateEmployeeCommandHandler,
    )
    return provider