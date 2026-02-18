from fastapi import APIRouter

from . import (
    auth,
    health,
    employee,
    client,
    order,
    device_type,
    device,
    part,
    work,
    payment,
    order_part,
    order_comment,
    validation_rules,
)

api_v1_router = APIRouter()
api_v1_router.include_router(health.router)
api_v1_router.include_router(auth.router)
api_v1_router.include_router(employee.router)
api_v1_router.include_router(client.router)
api_v1_router.include_router(order.router)
api_v1_router.include_router(device_type.router)
api_v1_router.include_router(device.router)
api_v1_router.include_router(part.router)
api_v1_router.include_router(work.router)
api_v1_router.include_router(payment.router)
api_v1_router.include_router(order_part.router)
api_v1_router.include_router(order_comment.router)
api_v1_router.include_router(validation_rules.router)

