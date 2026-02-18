from enum import Enum


class OrderStatus(str, Enum):
    NEW = "new"                 # новый
    ENGINEER = "engineer"       # инженер
    MANAGER = "manager"         # менеджер
    WAITING_PARTS = "waiting_parts"  # ждём з/ч
    READY = "ready"             # готово
    PAID = "paid"               # оплачено
    CLOSED = "closed"           # закрыт

