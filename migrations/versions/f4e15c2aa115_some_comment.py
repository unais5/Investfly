"""some comment

Revision ID: f4e15c2aa115
Revises: 
Create Date: 2020-12-26 03:58:52.574715

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f4e15c2aa115'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
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

    op.create_table('stock',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('stock_name', sa.String(), nullable=False),
    sa.Column('quantity', sa.Integer(), nullable=False),
    sa.Column('curr_price', sa.Float(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['user_login.id'], onupdate='CASCADE', ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('user_info',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('name', sa.String(length=20), nullable=True),
    sa.Column('phone', sa.String(), nullable=False),
    sa.Column('acc_num', sa.Integer(), nullable=False),
    sa.Column('cnic', sa.Integer(), nullable=False),
    sa.Column('addr', sa.String(length=50), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['user_login.id'], onupdate='CASCADE', ondelete='NO ACTION'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('acc_num'),
    sa.UniqueConstraint('cnic'),
    sa.UniqueConstraint('phone'),
    sa.UniqueConstraint('user_id')
    )
    op.create_table('wallet',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('balance', sa.Float(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['user_login.id'], onupdate='CASCADE', ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('user_id')
    )
    op.create_table('available_stocks',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('stock_name', sa.String(), nullable=False),
    sa.Column('seller_id', sa.Integer(), nullable=False),
    sa.Column('quantity', sa.Integer(), nullable=False),
    sa.Column('curr_price', sa.Float(), nullable=False),
    sa.ForeignKeyConstraint(['curr_price'], ['stock.curr_price'], onupdate='CASCADE', ondelete='NO ACTION'),
    sa.ForeignKeyConstraint(['seller_id'], ['user_login.id'], onupdate='CASCADE', ondelete='NO ACTION'),
    sa.ForeignKeyConstraint(['stock_name'], ['stock.stock_name'], onupdate='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('transaction',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('transaction_date', sa.Date(), nullable=False),
    sa.Column('buyer_id', sa.Integer(), nullable=False),
    sa.Column('quantity', sa.Integer(), nullable=False),
    sa.Column('seller_id', sa.Integer(), nullable=False),
    sa.Column('selling_price', sa.Float(), nullable=False),
    sa.Column('stock_name', sa.String(), nullable=False),
    sa.ForeignKeyConstraint(['stock_name'], ['stock.stock_name'], onupdate='CASCADE', ondelete='NO ACTION'),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('transaction')
    op.drop_table('available_stocks')
    op.drop_table('wallet')
    op.drop_table('user_info')
    op.drop_table('stock')
    with op.batch_alter_table('user_login', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_user_login_username'))
        batch_op.drop_index(batch_op.f('ix_user_login_email'))

    op.drop_table('user_login')
    # ### end Alembic commands ###
