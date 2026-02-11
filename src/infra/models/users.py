from sqlalchemy import (
    UUID,
    BigInteger,
    Column,
    DateTime,
    String,
    Table,
    func,
    Index, Boolean,
)
from sqlalchemy.orm import relationship
from src.entities.users.models import User
from src.infra.models._base import mapper_registry

users_table = Table(
    "users",
    mapper_registry.metadata,
    Column("user_id", BigInteger, primary_key=True, autoincrement=True),
    Column("user_uuid", UUID(as_uuid=True), nullable=False, comment="Keycloak user id (JWT sub)"),
    Column("is_active", Boolean, nullable=False, server_default="true"),
    Column("email", String(255), nullable=False),
    Column("created_at", DateTime, default=func.now(), server_default=func.now(), nullable=False),
    Column(
        "updated_at",
        DateTime,
        default=func.now(),
        server_default=func.now(),
        onupdate=func.now(),
        server_onupdate=func.now(),
        nullable=True,
    ),
    Index("ix_users_user_uuid", "user_uuid", unique=True),
    Index("ix_users_email", "email", unique=True),
)


def map_user_table() -> None:
    _ = mapper_registry.map_imperatively(
        User,
        users_table,
        properties={
            "oid": users_table.c.user_id,
            "ouuid": users_table.c.user_uuid,
        },
    )
