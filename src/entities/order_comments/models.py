from dataclasses import dataclass
from datetime import datetime
from typing import NewType
from uuid import UUID

from src.entities.base_entity import BaseEntity
from src.entities.employees.models import EmployeeID
from src.entities.orders.models import OrderID

OrderCommentID = NewType("OrderCommentID", int)
OrderCommentUUID = NewType("OrderCommentUUID", UUID)


@dataclass
class OrderComment(BaseEntity[OrderCommentID, OrderCommentUUID]):
    order_id: OrderID
    creator_id: EmployeeID
    comment: str | None
    created_at: datetime
