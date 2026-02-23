from dishka import Provider, Scope

from src.application.commands.base.auth.login import LoginCommandHandler
from src.application.commands.base.auth.logout import LogoutCommandHandler
from src.application.commands.base.auth.registration import RegisterCommandHandler
from src.application.commands.base.auth.update_access_token import UpdateAccessTokenCommandHandler
from src.application.commands.employee.create_employee import CreateEmployeeCommandHandler
from src.application.commands.employee.read_all_employee import ReadAllEmployeeCommandHandler
from src.application.commands.employee.read_employee import ReadEmployeeCommandHandler
from src.application.commands.employee.update_employee import UpdateEmployeeCommandHandler
from src.application.commands.employee.delete_employee import DeleteEmployeeCommandHandler
from src.application.commands.employee.change_password import ChangePasswordCommandHandler
from src.application.commands.client.create_client import CreateClientCommandHandler
from src.application.commands.client.read_all_client import ReadAllClientCommandHandler
from src.application.commands.client.read_client import ReadClientCommandHandler
from src.application.commands.client.update_client import UpdateClientCommandHandler
from src.application.commands.client.delete_client import DeleteClientCommandHandler
from src.application.commands.order.create_order import CreateOrderCommandHandler
from src.application.commands.order.create_order_with_client_and_device import (
    CreateOrderWithClientAndDeviceCommandHandler,
)
from src.application.commands.order.read_all_order import ReadAllOrderCommandHandler
from src.application.commands.order.read_order import ReadOrderCommandHandler
from src.application.commands.order.update_order import UpdateOrderCommandHandler
from src.application.commands.order.delete_order import DeleteOrderCommandHandler
from src.application.commands.order.generate_act_pdf import GenerateActPdfCommandHandler
from src.application.commands.order.generate_receipt_html import GenerateReceiptHtmlCommandHandler
from src.application.commands.device_type.create_device_type import CreateDeviceTypeCommandHandler
from src.application.commands.device_type.read_all_device_type import ReadAllDeviceTypeCommandHandler
from src.application.commands.device_type.read_device_type import ReadDeviceTypeCommandHandler
from src.application.commands.device_type.update_device_type import UpdateDeviceTypeCommandHandler
from src.application.commands.device_type.delete_device_type import DeleteDeviceTypeCommandHandler
from src.application.commands.brand.create_brand import CreateBrandCommandHandler
from src.application.commands.brand.read_all_brand import ReadAllBrandCommandHandler
from src.application.commands.brand.read_brand import ReadBrandCommandHandler
from src.application.commands.brand.update_brand import UpdateBrandCommandHandler
from src.application.commands.brand.delete_brand import DeleteBrandCommandHandler
from src.application.commands.device.create_device import CreateDeviceCommandHandler
from src.application.commands.device.read_all_device import ReadAllDeviceCommandHandler
from src.application.commands.device.read_device import ReadDeviceCommandHandler
from src.application.commands.device.update_device import UpdateDeviceCommandHandler
from src.application.commands.device.delete_device import DeleteDeviceCommandHandler
from src.application.commands.part.create_part import CreatePartCommandHandler
from src.application.commands.part.read_all_part import ReadAllPartCommandHandler
from src.application.commands.part.read_part import ReadPartCommandHandler
from src.application.commands.part.update_part import UpdatePartCommandHandler
from src.application.commands.part.delete_part import DeletePartCommandHandler
from src.application.commands.work.create_work import CreateWorkCommandHandler
from src.application.commands.work.read_all_work import ReadAllWorkCommandHandler
from src.application.commands.work.read_work import ReadWorkCommandHandler
from src.application.commands.work.update_work import UpdateWorkCommandHandler
from src.application.commands.work.delete_work import DeleteWorkCommandHandler
from src.application.commands.payment.create_payment import CreatePaymentCommandHandler
from src.application.commands.payment.read_all_payment import ReadAllPaymentCommandHandler
from src.application.commands.payment.read_payment import ReadPaymentCommandHandler
from src.application.commands.payment.update_payment import UpdatePaymentCommandHandler
from src.application.commands.payment.delete_payment import DeletePaymentCommandHandler
from src.application.commands.order_part.create_order_part import CreateOrderPartCommandHandler
from src.application.commands.order_part.read_all_order_part import ReadAllOrderPartCommandHandler
from src.application.commands.order_part.read_order_part import ReadOrderPartCommandHandler
from src.application.commands.order_part.update_order_part import UpdateOrderPartCommandHandler
from src.application.commands.order_part.delete_order_part import DeleteOrderPartCommandHandler
from src.application.commands.order_comment.create_order_comment import CreateOrderCommentCommandHandler
from src.application.commands.organization.get_organization import GetOrganizationCommandHandler
from src.application.commands.organization.create_organization import CreateOrganizationCommandHandler
from src.application.commands.organization.update_organization import UpdateOrganizationCommandHandler
from src.application.commands.organization.delete_organization import DeleteOrganizationCommandHandler
from src.application.commands.statistics.get_statistics import GetStatisticsCommandHandler


def interactors_provider() -> Provider:
    provider = Provider(scope=Scope.REQUEST)
    _ = provider.provide_all(
        RegisterCommandHandler,
        LoginCommandHandler,
        LogoutCommandHandler,
        UpdateAccessTokenCommandHandler,

        ReadAllEmployeeCommandHandler,
        ReadEmployeeCommandHandler,
        CreateEmployeeCommandHandler,
        UpdateEmployeeCommandHandler,
        DeleteEmployeeCommandHandler,
        ChangePasswordCommandHandler,

        ReadAllClientCommandHandler,
        ReadClientCommandHandler,
        CreateClientCommandHandler,
        UpdateClientCommandHandler,
        DeleteClientCommandHandler,

        ReadAllOrderCommandHandler,
        ReadOrderCommandHandler,
        CreateOrderCommandHandler,
        CreateOrderWithClientAndDeviceCommandHandler,
        UpdateOrderCommandHandler,
        DeleteOrderCommandHandler,
        GenerateActPdfCommandHandler,
        GenerateReceiptHtmlCommandHandler,

        ReadAllDeviceTypeCommandHandler,
        ReadDeviceTypeCommandHandler,
        CreateDeviceTypeCommandHandler,
        UpdateDeviceTypeCommandHandler,
        DeleteDeviceTypeCommandHandler,

        CreateBrandCommandHandler,
        ReadAllBrandCommandHandler,
        ReadBrandCommandHandler,
        UpdateBrandCommandHandler,
        DeleteBrandCommandHandler,

        ReadAllDeviceCommandHandler,
        ReadDeviceCommandHandler,
        CreateDeviceCommandHandler,
        UpdateDeviceCommandHandler,
        DeleteDeviceCommandHandler,

        ReadAllPartCommandHandler,
        ReadPartCommandHandler,
        CreatePartCommandHandler,
        UpdatePartCommandHandler,
        DeletePartCommandHandler,

        ReadAllWorkCommandHandler,
        ReadWorkCommandHandler,
        CreateWorkCommandHandler,
        UpdateWorkCommandHandler,
        DeleteWorkCommandHandler,

        ReadAllPaymentCommandHandler,
        ReadPaymentCommandHandler,
        CreatePaymentCommandHandler,
        UpdatePaymentCommandHandler,
        DeletePaymentCommandHandler,

        ReadAllOrderPartCommandHandler,
        ReadOrderPartCommandHandler,
        CreateOrderPartCommandHandler,
        UpdateOrderPartCommandHandler,
        DeleteOrderPartCommandHandler,

        CreateOrderCommentCommandHandler,

        GetOrganizationCommandHandler,
        CreateOrganizationCommandHandler,
        UpdateOrganizationCommandHandler,
        DeleteOrganizationCommandHandler,

        GetStatisticsCommandHandler,
    )
    return provider