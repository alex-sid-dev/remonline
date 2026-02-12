from src.infra.models import (map_user_table,
                              map_clients_table,
                              map_employee_table,
                              map_parts_table,
                              map_order_parts_table,
                              map_orders_table,
                              map_works_table,
                              map_device_types_table,
                              map_payments_table,
                              map_devices_table
                              )
from src.infra.models.order_comments import map_order_comments_table


def map_tables() -> None:
    map_user_table()
    map_clients_table()
    map_employee_table()
    map_parts_table()
    map_orders_table()
    map_works_table()
    map_device_types_table()
    map_payments_table()
    map_devices_table()
    map_order_parts_table()
    map_order_comments_table()
