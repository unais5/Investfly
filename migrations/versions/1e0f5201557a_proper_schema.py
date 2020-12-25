"""Proper Schema

Revision ID: 1e0f5201557a
Revises: 
Create Date: 2020-12-25 16:00:12.894177

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1e0f5201557a'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('stock',
    sa.Column('stock_name', sa.String(), nullable=False),
    sa.Column('curr_price', sa.Float(), nullable=False),
    sa.Column('vol', sa.Integer(), nullable=False),
    sa.PrimaryKeyConstraint('stock_name')
    )
    op.create_table('user_login',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('username', sa.String(length=64), nullable=False),
    sa.Column('email', sa.String(length=120), nullable=False),
    sa.Column('password_hash', sa.String(length=128), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('id')
    )
    with op.batch_alter_table('user_login', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_user_login_email'), ['email'], unique=True)
        batch_op.create_index(batch_op.f('ix_user_login_username'), ['username'], unique=True)

    op.create_table('listings',
    sa.Column('stock_name', sa.String(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('listed_qty', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['stock_name'], ['stock.stock_name'], ),
    sa.ForeignKeyConstraint(['user_id'], ['user_login.id'], ),
    sa.PrimaryKeyConstraint('stock_name', 'user_id')
    )
    op.create_table('owns',
    sa.Column('stock_name', sa.String(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('owned_qty', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['stock_name'], ['stock.stock_name'], ),
    sa.ForeignKeyConstraint(['user_id'], ['user_login.id'], ),
    sa.PrimaryKeyConstraint('stock_name', 'user_id')
    )
    op.create_table('transactions',
    sa.Column('stock_name', sa.String(), nullable=False),
    sa.Column('seller_id', sa.Integer(), nullable=False),
    sa.Column('buyer_id', sa.Integer(), nullable=False),
    sa.Column('quantity', sa.Integer(), nullable=False),
    sa.Column('sale_price', sa.Float(), nullable=False),
    sa.Column('date', sa.Date(), nullable=False),
    sa.ForeignKeyConstraint(['buyer_id'], ['user_login.id'], ),
    sa.ForeignKeyConstraint(['seller_id'], ['user_login.id'], ),
    sa.ForeignKeyConstraint(['stock_name'], ['stock.stock_name'], ),
    sa.PrimaryKeyConstraint('stock_name', 'seller_id', 'buyer_id')
    )
    op.create_table('user_info',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=20), nullable=True),
    sa.Column('phone', sa.String(), nullable=False),
    sa.Column('acc_num', sa.Integer(), nullable=False),
    sa.Column('cnic', sa.Integer(), nullable=False),
    sa.Column('addr', sa.String(length=50), nullable=True),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['user_login.id'], ondelete='NO ACTION'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('acc_num'),
    sa.UniqueConstraint('cnic'),
    sa.UniqueConstraint('phone')
    )
    op.create_table('wallet',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('balance', sa.Float(), nullable=True),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['user_login.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('wallet')
    op.drop_table('user_info')
    op.drop_table('transactions')
    op.drop_table('owns')
    op.drop_table('listings')
    with op.batch_alter_table('user_login', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_user_login_username'))
        batch_op.drop_index(batch_op.f('ix_user_login_email'))

    op.drop_table('user_login')
    op.drop_table('stock')
    # ### end Alembic commands ###
