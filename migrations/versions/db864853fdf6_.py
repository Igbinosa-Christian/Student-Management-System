"""empty message

Revision ID: db864853fdf6
Revises: e78ed0f622fe
Create Date: 2023-03-09 00:28:36.114647

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'db864853fdf6'
down_revision = 'e78ed0f622fe'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('admin', schema=None) as batch_op:
        batch_op.add_column(sa.Column('is_admin', sa.Integer(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('admin', schema=None) as batch_op:
        batch_op.drop_column('is_admin')

    # ### end Alembic commands ###