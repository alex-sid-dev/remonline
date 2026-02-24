from src.entities.employees.models import EmployeeID
from src.entities.order_comments.services import OrderCommentService
from src.entities.orders.models import OrderID


class TestOrderCommentService:
    def setup_method(self):
        self.service = OrderCommentService()

    def test_create_order_comment(self):
        comment = self.service.create_order_comment(
            order_id=OrderID(1),
            creator_id=EmployeeID(2),
            comment="Replaced the battery",
        )
        assert comment.order_id == OrderID(1)
        assert comment.creator_id == EmployeeID(2)
        assert comment.comment == "Replaced the battery"
        assert comment.uuid is not None
        assert comment.created_at is not None
