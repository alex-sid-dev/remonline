from datetime import datetime
from uuid import uuid4

from src.entities.employees.models import EmployeeID
from src.entities.orders.models import OrderID
from src.entities.payments.models import Payment, PaymentUUID


class PaymentService:
    def create_payment(
        self,
        order_id: OrderID,
        amount: float,
        payment_method: str,
        employee_id: EmployeeID | None = None,
        comment: str | None = None,
    ) -> Payment:
        return Payment(
            id=None,  # type: ignore
            uuid=PaymentUUID(uuid4()),
            order_id=order_id,
            amount=amount,
            payment_method=payment_method,
            employee_id=employee_id,
            comment=comment,
            created_at=datetime.utcnow(),
        )

    def update_payment(
        self,
        payment: Payment,
        amount: float | None = None,
        payment_method: str | None = None,
        employee_id: EmployeeID | None = None,
        comment: str | None = None,
    ) -> Payment:
        if amount is not None:
            payment.amount = amount
        if payment_method is not None:
            payment.payment_method = payment_method
        if employee_id is not None:
            payment.employee_id = employee_id
        if comment is not None:
            payment.comment = comment
        return payment
