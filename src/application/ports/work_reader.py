from typing import Protocol

from src.entities.orders.models import OrderID
from src.entities.works.models import Work, WorkID, WorkUUID


class WorkReader(Protocol):
    async def read_by_id(self, work_id: WorkID) -> Work | None: ...

    async def read_by_uuid(self, work_uuid: WorkUUID) -> Work | None: ...

    async def read_all_active(self) -> list[Work]: ...

    async def read_by_order_id(self, order_id: OrderID) -> list[Work]: ...
