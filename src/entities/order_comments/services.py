from datetime import datetime
from typing import cast
from uuid import uuid4

from src.entities.employees.models import EmployeeID
from src.entities.order_comments.models import OrderComment, OrderCommentID, OrderCommentUUID
from src.entities.orders.models import OrderID


class OrderCommentService:
    @staticmethod
    def create_order_comment(
        order_id: OrderID,
        creator_id: EmployeeID,
        comment: str,
    ) -> OrderComment:
        return OrderComment(
            id=cast(OrderCommentID, None),
            uuid=OrderCommentUUID(uuid4()),
            order_id=order_id,
            creator_id=creator_id,
            comment=comment,
            created_at=datetime.now(),
        )
