"""create order comments table

Revision ID: 4945a6c8d2f1
Revises: devices_orders_parts
Create Date: 2024-05-24 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'add_order_comments_table' # Новый ID миграции
down_revision = 'devices_orders_parts' # Ваша предыдущая миграция
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Создание таблицы order_comments
    op.create_table(
        'order_comments',
        sa.Column('order_comment_id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('order_comment_uuid', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('order_id', sa.BigInteger(), nullable=False),
        sa.Column('creator_id', sa.BigInteger(), nullable=False),
        sa.Column('comment', sa.TEXT(), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['creator_id'], ['employees.employee_id'], ),
        sa.ForeignKeyConstraint(['order_id'], ['orders.order_id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('order_comment_id'),
        sa.UniqueConstraint('order_comment_uuid')
    )
    # Создание индекса (хотя UniqueConstraint его уже создал, Alembic часто дублирует его явно)
    op.create_index('ix_order_comments_order_comment_uuid', 'order_comments', ['order_comment_uuid'], unique=True)


def downgrade() -> None:
    op.drop_index('ix_order_comments_order_comment_uuid', table_name='order_comments')
    op.drop_table('order_comments')
