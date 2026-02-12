from dishka import Provider, Scope

from src.application.ports.employee_reader import EmployeeReader
from src.application.ports.transaction import Transaction, EntitySaver
from src.application.ports.user_reader import UserReader
from src.application.ports.client_reader import ClientReader
from src.application.ports.order_reader import OrderReader
from src.application.ports.device_type_reader import DeviceTypeReader
from src.application.ports.device_reader import DeviceReader
from src.application.ports.part_reader import PartReader
from src.application.ports.work_reader import WorkReader
from src.application.ports.payment_reader import PaymentReader
from src.application.ports.order_part_reader import OrderPartReader
from src.infra.adapters.employee_reader_alchemy import EmployeeReaderAlchemy
from src.infra.adapters.transaction import EntitySaverAlchemy, TransactionAlchemy
from src.infra.adapters.user_reader_alchemy import UserReaderAlchemy
from src.infra.adapters.client_reader import ClientReaderAdapter
from src.infra.adapters.order_reader import OrderReaderAdapter
from src.infra.adapters.device_type_reader import DeviceTypeReaderAdapter
from src.infra.adapters.device_reader import DeviceReaderAdapter
from src.infra.adapters.part_reader import PartReaderAdapter
from src.infra.adapters.work_reader import WorkReaderAdapter
from src.infra.adapters.payment_reader import PaymentReaderAdapter
from src.infra.adapters.order_part_reader import OrderPartReaderAdapter


def gateways_provider() -> Provider:
    provider = Provider(scope=Scope.REQUEST)
    _ = provider.provide(EntitySaverAlchemy, provides=EntitySaver)
    _ = provider.provide(TransactionAlchemy, provides=Transaction)
    _ = provider.provide(UserReaderAlchemy, provides=UserReader)
    _ = provider.provide(EmployeeReaderAlchemy, provides=EmployeeReader)
    _ = provider.provide(ClientReaderAdapter, provides=ClientReader)
    _ = provider.provide(OrderReaderAdapter, provides=OrderReader)
    _ = provider.provide(DeviceTypeReaderAdapter, provides=DeviceTypeReader)
    _ = provider.provide(DeviceReaderAdapter, provides=DeviceReader)
    _ = provider.provide(PartReaderAdapter, provides=PartReader)
    _ = provider.provide(WorkReaderAdapter, provides=WorkReader)
    _ = provider.provide(PaymentReaderAdapter, provides=PaymentReader)
    _ = provider.provide(OrderPartReaderAdapter, provides=OrderPartReader)
    return provider