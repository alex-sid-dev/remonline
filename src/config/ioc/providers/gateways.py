from dishka import Provider, Scope

from src.application.ports.employee_reader import EmployeeReader
from src.application.ports.transaction import Transaction, EntitySaver
from src.application.ports.user_reader import UserReader
from src.infra.adapters.employee_reader_alchemy import EmployeeReaderAlchemy
from src.infra.adapters.transaction import EntitySaverAlchemy, TransactionAlchemy
from src.infra.adapters.user_reader_alchemy import UserReaderAlchemy


def gateways_provider() -> Provider:
    provider = Provider(scope=Scope.REQUEST)
    _ = provider.provide(EntitySaverAlchemy, provides=EntitySaver)
    _ = provider.provide(TransactionAlchemy, provides=Transaction)
    _ = provider.provide(UserReaderAlchemy, provides=UserReader)
    _ = provider.provide(EmployeeReaderAlchemy, provides=EmployeeReader)
    return provider