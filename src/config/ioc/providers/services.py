from dishka import Provider, Scope

from src.entities.employees.services import EmployeeService
from src.entities.users.services import UserService
from src.entities.clients.services import ClientService
from src.entities.orders.services import OrderService
from src.entities.device_types.services import DeviceTypeService
from src.entities.devices.services import DeviceService
from src.entities.parts.services import PartService
from src.entities.works.services import WorkService
from src.entities.payments.services import PaymentService
from src.entities.order_parts.services import OrderPartService
from src.entities.order_comments.services import OrderCommentService
from src.entities.organizations.services import OrganizationService


def services_provider() -> Provider:
    provider = Provider(scope=Scope.REQUEST)
    _ = provider.provide_all(
        UserService,
        EmployeeService,
        ClientService,
        OrderService,
        DeviceTypeService,
        DeviceService,
        PartService,
        WorkService,
        PaymentService,
        OrderPartService,
        OrderCommentService,
        OrganizationService,
    )
    return provider