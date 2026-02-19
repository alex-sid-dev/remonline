from dataclasses import dataclass
from uuid import UUID

import structlog

from src.application.commands.base_command_handler import BaseCommandHandler
from src.application.ports.order_reader import OrderReader
from src.application.ports.transaction import Transaction, EntitySaver
from src.entities.order_comments.services import OrderCommentService
from src.entities.orders.models import OrderUUID, OrderID
from src.entities.employees.models import Employee, EmployeeID
from src.application.errors._base import EntityNotFoundError

logger = structlog.get_logger("create_order_comment").bind(service="order_comment")


@dataclass
class CreateOrderCommentCommandResponse:
    uuid: UUID


@dataclass
class CreateOrderCommentCommand:
    order_uuid: UUID
    text: str


class CreateOrderCommentCommandHandler(BaseCommandHandler):
    def __init__(
            self,
            transaction: Transaction,
            entity_saver: EntitySaver,
            order_reader: OrderReader,
            order_comment_service: OrderCommentService,
    ) -> None:
        self._transaction = transaction
        self._entity_saver = entity_saver
        self._order_reader = order_reader
        self._order_comment_service = order_comment_service

    async def run(self, data: CreateOrderCommentCommand, current_employee: Employee) -> CreateOrderCommentCommandResponse:
        order = await self._order_reader.read_by_uuid(OrderUUID(data.order_uuid))
        if not order:
            raise EntityNotFoundError(message=f"Order with uuid {data.order_uuid} not found")

        comment = self._order_comment_service.create_order_comment(
            order_id=OrderID(order.id),
            creator_id=EmployeeID(current_employee.id),
            comment=data.text,
        )
        self._entity_saver.add_one(comment)
        await self._transaction.commit()
        logger.info("Order comment created successfully", order_comment_uuid=str(comment.uuid))

        return CreateOrderCommentCommandResponse(uuid=comment.uuid)
