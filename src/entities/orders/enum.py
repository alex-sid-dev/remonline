from enum import Enum


class OrderStatus(str, Enum):
    NEW = "new"  # новый
    ACCEPTED = "accepted"  # принят в работу
    DIAGNOSTICS = "diagnostics"  # на диагностике
    ON_APPROVAL = "on_approval"  # на согласовании
    WAITING_PARTS = "waiting_parts"  # ждем запчасти
    IN_REPAIR = "in_repair"  # в ремонте
    PAID = "paid"  # оплачен
    CLOSED = "closed"  # закрыт
    REJECTED = "rejected"  # отказ
