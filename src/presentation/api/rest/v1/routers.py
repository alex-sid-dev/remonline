from fastapi import APIRouter

from . import (
    auth,
    brand,
    client,
    device,
    device_type,
    employee,
    health,
    order,
    order_comment,
    order_part,
    organization,
    part,
    payment,
    statistics,
    validation_rules,
    work,
)

api_v1_router = APIRouter()
api_v1_router.include_router(health.router)
api_v1_router.include_router(auth.router)
api_v1_router.include_router(employee.router)
api_v1_router.include_router(client.router)
api_v1_router.include_router(order.router)
api_v1_router.include_router(organization.router)
api_v1_router.include_router(device_type.router)
api_v1_router.include_router(brand.router)
api_v1_router.include_router(device.router)
api_v1_router.include_router(part.router)
api_v1_router.include_router(work.router)
api_v1_router.include_router(payment.router)
api_v1_router.include_router(order_part.router)
api_v1_router.include_router(order_comment.router)
api_v1_router.include_router(validation_rules.router)
api_v1_router.include_router(statistics.router)
