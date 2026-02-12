from typing import List, Optional, Protocol
from src.entities.works.models import Work, WorkID, WorkUUID
from src.entities.orders.models import OrderID

class WorkReader(Protocol):
    async def read_by_id(self, work_id: WorkID) -> Optional[Work]:
        ...

    async def read_by_uuid(self, work_uuid: WorkUUID) -> Optional[Work]:
        ...

    async def read_all_active(self) -> List[Work]:
        ...

    async def read_by_order_id(self, order_id: OrderID) -> List[Work]:
        ...
